#!/usr/bin/env python3
"""Build the ported Xiaomi Creation APK for nabu.

Creation is a Qt app whose DEX is small relative to its native payload. The same
rules as Notes apply: DEX/manifest and resources can change; assets and native
payloads stay byte-identical to the pinned stock APK.

Differences from Notes:
  * Creation is a normal user-facing app whose cloud sync is the only MIUI
    dependency group, so the disabled components are the cloud/sync services.
  * Its Korean translation table has only five regulatory strings; the labels are
    translated and the filing numbers are kept verbatim.
"""
import argparse
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import appbuild
import harden_manifest
from appbuild import ROOT, RomTools, run

APP = 'Creation'
PIN = 'product/data-app/Creation/Creation.apk'
OUT = ROOT / 'proprietary/ported/product/app/Creation/Creation.apk'

# Xiaomi cloud/account components that need a backend PixelOS does not have.
# Explicit components to disable in addition to the shared Xiaomi families.
DISABLE_COMPONENTS = {
    'com.miui.creation.cloudservice.service.CreationsSyncService',
    'com.miui.creation.cloudservice.PushReceiver',
    'com.miui.creation.cloudservice.AccountReceiver',
}


def decode_escapes(text):
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch == '\\' and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == 'n':
                out.append('\n')
                i += 2
                continue
            if nxt == 't':
                out.append('\t')
                i += 2
                continue
            if nxt == '\\':
                out.append('\\')
                i += 2
                continue
        out.append(ch)
        i += 1
    return ''.join(out)


def load_translations():
    path = ROOT / 'translations/creation-ko.tsv'
    table = {}
    for raw in path.read_text().splitlines():
        if not raw.strip() or raw.startswith('#') or '\t' not in raw:
            continue
        key, value = raw.split('\t', 1)
        table[key] = decode_escapes(value)
    return table


def patch_manifest(manifest_path: Path):
    ET.register_namespace('android', appbuild.ANDROID_NS)
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    app = root.find('application')
    if app is None:
        raise SystemExit('no <application> element')
    tree.write(manifest_path, encoding='utf-8', xml_declaration=True)

    # Sever every Xiaomi cloud tie: account sign-in, cloud sync and Market
    # updates. Creation's cloud class names are obfuscated, so the family
    # matcher also covers the `cloudservice` package name.
    changed = []
    for library in harden_manifest.drop_micloud_library(manifest_path):
        changed.append(f'removed unavailable shared library {library}')
    disabled = harden_manifest.block_xiaomi_services(
        manifest_path, extra_components=DISABLE_COMPONENTS)
    for tag, name, family in disabled:
        changed.append(f'disabled {name} [{family}]')

    removed_perms = harden_manifest.drop_install_package_permission(manifest_path)
    for perm in removed_perms:
        changed.append(f'removed {perm}')

    remaining = harden_manifest.report_cloud_permissions(manifest_path)
    if remaining:
        print('  note: Xiaomi cloud permissions still declared (cannot be granted): '
              + ', '.join(remaining))

    return changed


def add_korean(res_dir: Path, table):
    ko = res_dir / 'values-ko'
    ko.mkdir(parents=True, exist_ok=True)
    target = ko / 'strings.xml'
    if target.is_file():
        tree = ET.parse(target)
        root = tree.getroot()
    else:
        root = ET.Element('resources')
        tree = ET.ElementTree(root)
    existing = {node.get('name') for node in root.findall('string')}
    added = 0
    for key, value in sorted(table.items()):
        if key in existing:
            continue
        node = ET.SubElement(root, 'string', {'name': key})
        node.text = value
        added += 1
    tree.write(target, encoding='utf-8', xml_declaration=True)
    return added


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom-root', required=True, type=Path)
    p.add_argument('--output', type=Path, default=OUT)
    p.add_argument('--keep-work', type=Path)
    p.add_argument('--shim-smali', type=Path, required=True,
                   help='decoded shim smali tree (from build-shims.py --keep)')
    a = p.parse_args()

    tools = RomTools(a.rom_root)
    tools.check()
    stock = appbuild.verify_pin(PIN)

    work = a.keep_work or Path(tempfile.mkdtemp(prefix='apps-nabu-creation-'))
    work.mkdir(parents=True, exist_ok=True)
    try:
        frame_dir = appbuild.install_frameworks(tools, work)
        decoded = work / 'decoded'
        appbuild.decode_resources(tools, stock, frame_dir, decoded)

        smali_root = work / 'smali'
        appbuild.decode_dex(tools, stock, smali_root)

        changed = patch_manifest(decoded / 'AndroidManifest.xml')
        for item in changed:
            print(' ', item)

        table = load_translations()
        added = add_korean(decoded / 'res', table)
        print(f'Korean strings added: {added}')

        manifest_apk = work / 'manifest.apk'
        run([tools.java, '-Xmx4g', '-jar', tools.apktool, 'b',
             '-p', frame_dir, '-o', manifest_apk, decoded])
        with zipfile.ZipFile(manifest_apk) as z:
            compiled_manifest = z.read('AndroidManifest.xml')
        # Adding values-ko changes the string pool, so the rebuilt resource table
        # must replace the stock one; copying the original would drop the Korean
        # strings again.
        resources_arsc = appbuild.extract_resources_arsc(manifest_apk)

        smali_dirs = []
        for name in ['classes'] + [f'classes{i}' for i in range(2, 64)]:
            candidate = smali_root / name
            if candidate.is_dir():
                smali_dirs.append(candidate)
        print('dex order:', [d.name for d in smali_dirs])

        dex_dir = work / 'dex'
        dex_dir.mkdir(exist_ok=True)
        dex_files = appbuild.assemble_dex(tools, smali_dirs, dex_dir)

        features = appbuild.verify_pin(appbuild.NABU_FEATURES)
        extra = {'assets/nabu_features.xml': features.read_bytes()}
        shim_dex_dir = work / 'shimdex'
        shim_dex_dir.mkdir(exist_ok=True)
        shim_files = appbuild.assemble_dex(
            tools, [appbuild.filtered_shims(a.shim_smali, smali_root, work / 'filtered-shims')],
            shim_dex_dir, start_index=len(dex_files))
        extra.update({n: p.read_bytes() for n, p in shim_files.items()})

        unsigned = work / 'unsigned.apk'
        appbuild.build_apk(stock, compiled_manifest, dex_files, extra, unsigned,
                           resources_arsc=resources_arsc, rebuilt_resources=manifest_apk)

        aligned = work / 'aligned.apk'
        signed = work / 'signed.apk'
        appbuild.align_and_sign(tools, unsigned, aligned, signed)

        preserved = appbuild.verify_payload_preserved(
            stock, signed, resources_changed=True)
        print(f'preserved original entries: {preserved}')

        a.output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(signed, a.output)
        record = appbuild.record_artifacts(
            APP, a.output,
            [stock, features, ROOT / 'translations/creation-ko.tsv',
             Path(appbuild.__file__), Path(harden_manifest.__file__), Path(__file__),
             ROOT / 'tools/build-shims.py',
             *sorted((ROOT / 'shims').rglob('*.java'))])
        print('built', a.output)
        print('record', record)
    finally:
        if not a.keep_work:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == '__main__':
    main()

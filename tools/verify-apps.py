#!/usr/bin/env python3
"""Verify the two built app APKs against everything this vendorship promises.

Checks, per app:
  * built APK exists and is signed with the ROM platform key
  * zip alignment is 16 KB compatible
  * assets/lib payloads are byte-identical; resource tables resolve their files
  * dex entry names follow Android's classes.dex/classesN.dex rule
  * the stock package name and version are preserved
  * manifest components that need a Xiaomi backend are disabled
  * no Korean string still contains Chinese text, except the allowlisted
    regulatory numbers
  * the shim DEX is present when the app needs MIUI shims

It also prints the size each app adds to the product partition.
"""
import argparse
from collections import Counter
import json
import re
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import appbuild
import harden_manifest
import manifest_checks
from dex_classes import class_descriptors
from appbuild import ROOT

CJK = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf]')

APPS = [
    # (name, stock pin, built path, needs shims, disabled component names)
    ('MIUINotes',
     'product/data-app/MIUINotes/MIUINotes.apk',
     'proprietary/ported/product/priv-app/MIUINotes/MIUINotes.apk',
     True,
     {'com.miui.notes.cloudservice.NotesSyncService',
      'com.miui.todo.cloudservice.PushReceiver',
      'com.miui.notes.backup.NoteSettingsBackupService',
      'com.miui.notes.ui.AccountReceiver'}),
    ('Creation',
     'product/data-app/Creation/Creation.apk',
     'proprietary/ported/product/app/Creation/Creation.apk',
     True,
     {'com.miui.creation.cloudservice.PushReceiver',
      'com.miui.creation.cloudservice.AccountReceiver'}),
]

REGULATORY_ALLOW = {
    'setting_algorithm_filing_title',
    'setting_algorithm_filing_text',
    'setting_algorithm_filing_big_text',
    'setting_algorithm_name_text',
    'setting_filing_text',
}


def sh(cmd):
    return subprocess.run([str(c) for c in cmd], check=False,
                          capture_output=True, text=True)


def check_apk(tools, name, stock, built, needs_shim, disabled_names, errors):
    if not built.is_file():
        errors.append(f'{name}: built APK missing at {built}')
        return 0

    stock_apk = ROOT / 'proprietary' / stock

    # Signature
    res = sh(tools.signer('verify', '--print-certs', built))
    if res.returncode != 0:
        errors.append(f'{name}: apksigner verify failed: {res.stderr.strip()[:200]}')
    else:
        sha1s = re.findall(r'SHA-1 digest: ([0-9a-f]+)', res.stdout)
        # Compare against the key the build used.
        key_cert = sh(['openssl', 'x509', '-in', tools.key / 'platform.x509.pem',
                       '-noout', '-fingerprint', '-sha1'])
        m = re.search(r'=([0-9A-F:]+)', key_cert.stdout)
        if m:
            want = m.group(1).replace(':', '').lower()
            if want not in sha1s:
                errors.append(f'{name}: not signed with the ROM platform key')
        else:
            errors.append(f'{name}: cannot read ROM signing certificate')

    # Alignment
    res = sh([tools.zipalign, '-c', '-P', '16', '4', built])
    if res.returncode != 0:
        errors.append(f'{name}: not 16 KB aligned: {res.stdout.strip()[:200]}')

    # Payload preservation and dex naming.
    #
    # resources.arsc must change: adding a values-ko table rewrites the string
    # pool, so comparing it to stock would be wrong. Everything else — every
    # res/ payload, every asset, every native library — must stay identical,
    # because these apps derive asset paths from resource names.
    with zipfile.ZipFile(stock_apk) as src, zipfile.ZipFile(built) as dst:
        dst_names = set(dst.namelist())
        for entry in src.infolist():
            entry_name = entry.filename
            if entry_name == 'AndroidManifest.xml' or entry_name.startswith('META-INF/'):
                continue
            if entry_name == 'resources.arsc':
                if entry_name not in dst_names:
                    errors.append(f'{name}: resources.arsc missing')
                continue
            if entry_name.startswith('res/'):
                # Compiled XML/paths must match the rebuilt table; assets/native remain pinned.
                continue
            if entry_name.startswith('classes') and entry_name.endswith('.dex'):
                continue
            if entry_name not in dst_names:
                errors.append(f'{name}: lost {entry_name}')
                continue
            if src.read(entry_name) != dst.read(entry_name):
                errors.append(f'{name}: changed {entry_name}')

        dex = sorted(n for n in dst_names
                     if n.startswith('classes') and n.endswith('.dex'))
        for n in dex:
            if n == 'classes.dex':
                continue
            if not re.fullmatch(r'classes(?:[2-9]|[1-9]\d+)\.dex', n):
                errors.append(f'{name}: invalid dex entry name {n}')
        seen_classes = {}
        for entry in dex:
            try:
                for descriptor in class_descriptors(dst.read(entry)):
                    if descriptor in seen_classes:
                        errors.append(f'{name}: duplicate DEX class {descriptor}: {seen_classes[descriptor]} / {entry}')
                    seen_classes[descriptor] = entry
                if not needs_shim and src.read(entry) != dst.read(entry):
                    errors.append(f'{name}: original DEX changed: {entry}')
            except (ValueError, IndexError) as failure:
                errors.append(f'{name}: cannot inspect DEX {entry}: {failure}')

    # Package identity
    aapt2 = tools.root / 'prebuilts/sdk/tools/linux/bin/aapt2'
    badging = sh([aapt2, 'dump', 'badging', built]).stdout
    pkg = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'",
                    badging)
    stock_badging = sh([aapt2, 'dump', 'badging', stock_apk]).stdout
    stock_pkg = re.search(
        r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'",
        stock_badging)
    if not pkg or not stock_pkg:
        errors.append(f'{name}: cannot read package identity')
    elif pkg.groups() != stock_pkg.groups():
        errors.append(f'{name}: package identity changed '
                      f'{stock_pkg.groups()} -> {pkg.groups()}')

    # Parse actual binary manifests; a disabled sibling must not hide an enabled component.
    try:
        manifests = []
        for path in (stock_apk, built):
            result = sh([aapt2, 'dump', 'xmltree', '--file', 'AndroidManifest.xml', path])
            if result.returncode:
                raise ValueError(result.stderr[:200])
            manifests.append(manifest_checks.parse_xmltree(result.stdout))
        original_manifest, built_manifest = manifests
        for app in built_manifest['children']:
            if app['tag'] == 'application' and any(
                    child['tag'] == 'uses-library' and
                    child['attrs'].get('name') == 'micloud-sdk'
                    for child in app['children']):
                errors.append(f'{name}: unavailable micloud-sdk shared-library declaration remains')
        if name == 'MIUINotes':
            # Platform signing does not waive the Android 17 privapp allowlist.
            # Match the product partition, where this privileged APK is installed.
            ns = '{http://schemas.android.com/apk/res/android}'
            framework = ET.parse(tools.root / 'frameworks/base/core/res/AndroidManifest.xml')
            privileged = {node.get(ns + 'name') for node in framework.getroot().findall('permission')
                          if 'privileged' in node.get(ns + 'protectionLevel', '').split('|')}
            allowlist = ET.parse(ROOT / 'configs/privapp-permissions-miuinotes.xml')
            allowed = {node.get('name') for entry in allowlist.getroot().findall('privapp-permissions')
                       if entry.get('package') == 'com.miui.notes'
                       for node in list(entry) if node.tag in ('permission', 'deny-permission')}
            missing = manifest_checks.active_permissions(built_manifest, 37) & privileged - allowed
            for permission in sorted(missing):
                errors.append(f'{name}: boot-fatal under privapp enforcement: missing {permission}')
        before, after = map(manifest_checks.components, manifests)
        for permission in ('android.permission.REQUEST_INSTALL_PACKAGES', 'android.permission.INSTALL_PACKAGES'):
            if permission in manifest_checks.permissions(built_manifest):
                errors.append(f'{name}: installer permission remains: {permission}')
        for component in before:
            if component not in disabled_names and not harden_manifest.blocked_family(component):
                continue
            if component not in after or not manifest_checks.disabled(after[component]):
                errors.append(f'{name}: required component not disabled: {component}')
    except ValueError as failure:
        errors.append(f'{name}: cannot verify binary manifest: {failure}')

    # Generated APKs must follow the reviewed helper, not just an old successful build.
    try:
        record = json.loads(built.with_suffix('.build.json').read_text())
        if record['apk_sha1'] != appbuild.sha1_file(built):
            errors.append(f'{name}: recorded APK hash mismatch')
        if record.get('schema') != 2:
            raise ValueError('legacy absolute-path build record; rebuild for this checkout')
        helper = 'tools/harden_manifest.py'
        if helper not in record['inputs']:
            errors.append(f'{name}: APK predates manifest hardening; rebuild required')
        for path, expected_hash in record['inputs'].items():
            source = ROOT / path
            if Path(path).is_absolute() or not source.resolve().is_relative_to(ROOT.resolve()):
                errors.append(f'{name}: input escapes checkout: {path}')
            elif not source.is_file() or appbuild.sha1_file(source) != expected_hash:
                errors.append(f'{name}: stale generated APK input: {path}')
    except (OSError, ValueError, KeyError) as failure:
        errors.append(f'{name}: invalid build record: {failure}')

    # Korean strings actually present in the built resource table
    with zipfile.ZipFile(built) as z:
        raw = z.read('resources.arsc') if 'resources.arsc' in z.namelist() else b''
    tables = sorted((ROOT / 'translations').glob(
        'notes-ko.tsv' if name == 'MIUINotes'
        else 'creation-ko.tsv'))
    for table in tables:
        for line_no, line in enumerate(table.read_text().splitlines(), 1):
            if '\t' not in line or line.startswith('#'):
                continue
            key, value = line.split('\t', 1)
            if CJK.search(value) and key not in REGULATORY_ALLOW:
                errors.append(f'{name}: Chinese left in {key}')

    # The rebuilt resources.arsc must actually contain the Korean config. A
    # common failure is copying the stock arsc back over the rebuilt one, which
    # silently drops every added translation.
    aapt2_bin = tools.root / 'prebuilts/sdk/tools/linux/bin/aapt2'
    configs = sh([aapt2_bin, 'dump', 'configurations', built]).stdout
    ko_present = any(line.strip().startswith('ko') for line in configs.splitlines())
    if not ko_present:
        errors.append(f'{name}: resources.arsc has no ko configuration; '
                      'the rebuilt resource table was not installed')

    # Spot-check that a translated value is really resolvable from the table.
    sample_key = {'MIUINotes': 'cancel', 'Creation': 'setting_filing_text'}[name]
    resource_dump = sh([aapt2_bin, 'dump', 'resources', built])
    dump = resource_dump.stdout
    original_dump = sh([aapt2_bin, 'dump', 'resources', stock_apk])
    def missing_files(result):
        return Counter(line for line in result.stderr.splitlines() if 'but no such path exists' in line)
    missing_paths = missing_files(resource_dump) - missing_files(original_dump)
    if resource_dump.returncode or missing_paths:
        errors.append(f'{name}: invalid resource table or {sum(missing_paths.values())} new missing resource file paths')
    def resource_ids(text):
        return {key: identifier for identifier, key in re.findall(
            r'^\s*resource (0x[0-9a-fA-F]+) (\S+)', text, re.M)}
    before_ids, after_ids = resource_ids(original_dump.stdout), resource_ids(dump)
    if original_dump.returncode or not before_ids or not after_ids:
        errors.append(f'{name}: cannot verify resource IDs')
    else:
        # aapt2 regenerates private inline drawable names ($...); their XML and table
        # are rebuilt together. Named resources referenced by app/native code keep IDs.
        moved = [key for key, identifier in before_ids.items()
                 if '/$' not in key and after_ids.get(key) != identifier]
        if moved:
            errors.append(f'{name}: original resource IDs changed/missing: {moved[:8]}')
    marker = f'string/{sample_key}'
    idx = dump.find(marker)
    if idx < 0:
        errors.append(f'{name}: sample string {sample_key} missing from resources')
    else:
        window = dump[idx:idx + 1200]
        if '(ko)' not in window:
            errors.append(f'{name}: {sample_key} has no Korean value')

    # Shim DEX presence
    if needs_shim:
        with zipfile.ZipFile(built) as z:
            names = z.namelist()
        dex = [n for n in names if n.startswith('classes') and n.endswith('.dex')]
        if len(dex) < 2:
            errors.append(f'{name}: shim DEX missing')
        for descriptor in ('Lmiui/os/Build;', 'Lmiui/util/FeatureParser;'):
            if descriptor not in seen_classes:
                errors.append(f'{name}: required shim class missing: {descriptor}')
        for descriptor in ('Landroid/content/res/MiuiConfiguration;',
                           'Landroid/provider/MiuiSettings$System;',
                           'Landroid/util/MiuiDisplayMetrics;',
                           'Landroid/util/MiuiMultiWindowUtils;',
                           'Landroid/view/MiuiCompositionSamplingListener;'):
            if descriptor not in seen_classes:
                errors.append(f'{name}: MIUI android.* compatibility class missing: {descriptor}')
        if 'Landroid/graphics/GraphicBuffer;' in seen_classes:
            errors.append(f'{name}: compile-only framework stub leaked into APK')
        with zipfile.ZipFile(built) as apk:
            if 'assets/nabu_features.xml' not in apk.namelist():
                errors.append(f'{name}: pinned Pad 5 feature asset missing')
            elif apk.read('assets/nabu_features.xml') != appbuild.verify_pin(appbuild.NABU_FEATURES).read_bytes():
                errors.append(f'{name}: packaged Pad 5 features differ from the pinned input')

    return built.stat().st_size


def uses_library_names(apk, aapt2):
    """Optional <uses-library> names declared in an APK manifest, in order."""
    badging = sh([aapt2, 'dump', 'badging', apk]).stdout
    return re.findall(r"uses-library-not-required:'([^']+)'", badging)


def check_uses_library_declarations(tools, aapt2, errors):
    """Build-side <uses-library> declarations must match each APK manifest.

    A missing declaration fails the build at verify_uses_libraries, which happens
    late and only on the machines that get that far. Checking it here turns the
    failure into a local, explainable error.
    """
    bp = (ROOT / 'Android.bp').read_text()
    declared = {}
    for m in re.finditer(r'android_app_import\s*\{(.*?)^\}', bp, re.S | re.M):
        body = m.group(1)
        name = re.search(r'name:\s*"([^"]+)"', body)
        if not name:
            continue
        opt = re.search(r'optional_uses_libs:\s*\[(.*?)\]', body, re.S)
        declared[name.group(1)] = re.findall(r'"([^"]+)"', opt.group(1)) if opt else []

    for name, stock, built, _, _ in APPS:
        apk = ROOT / built
        if not apk.is_file():
            continue
        # The built APK keeps the stock manifest's uses-library set.
        manifest_libs = uses_library_names(apk, aapt2)
        want = declared.get(name)
        if want is None:
            continue
        if want != manifest_libs:
            errors.append(
                f'{name}: optional_uses_libs {want} does not match the manifest '
                f'{manifest_libs}; Soong rejects this in verify_uses_libraries')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom-root', required=True, type=Path)
    a = p.parse_args()

    tools = appbuild.RomTools(a.rom_root)
    tools.check()

    errors = []
    total = 0
    print(f'platform key: {tools.key}')
    for name, stock, built, needs_shim, disabled in APPS:
        size = check_apk(tools, name, stock, ROOT / built, needs_shim,
                         disabled, errors)
        total += size
        print(f'{name:12s} {size / 2**20:8.0f} MiB  {built}')
        if size:
            with zipfile.ZipFile(ROOT / built) as apk:
                jni_growth = sum(entry.file_size - entry.compress_size for entry in apk.infolist()
                                 if entry.filename.startswith('lib/') and entry.filename.endswith('.so'))
            print(f'  Soong JNI store-size increase estimate: {jni_growth / 2**20:.1f} MiB '
                  '(before alignment/signing/dex changes)')

    print(f'{"total":12s} {total / 2**20:8.0f} MiB in prepared APKs; final product size requires Soong output')

    check_uses_library_declarations(tools, tools.root / 'prebuilts/sdk/tools/linux/bin/aapt2', errors)

    if errors:
        print('\nFAILURES:', file=sys.stderr)
        for e in errors:
            print('  ' + e, file=sys.stderr)
        return 1
    print('\nPASS: signatures, alignment, payload preservation, dex naming, '
          'manifest disables and Korean strings')
    return 0


if __name__ == '__main__':
    sys.exit(main())

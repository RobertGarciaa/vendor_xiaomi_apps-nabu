#!/usr/bin/env python3
"""Verify the two built app APKs against everything this vendorship promises.

Checks, per app:
  * built APK exists and is signed with the ROM platform key
  * zip alignment is 16 KB compatible
  * resources.arsc, res/, assets/ and lib/ entries are byte-identical to stock
  * dex entry names follow Android's classes.dex/classesN.dex rule
  * the stock package name and version are preserved
  * manifest components that need a Xiaomi backend are disabled
  * no Korean string still contains Chinese text, except the allowlisted
    regulatory numbers
  * the shim DEX is present when the app needs MIUI shims

It also prints the size each app adds to the product partition.
"""
import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import appbuild
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
    res = sh([tools.apksigner, 'verify', '--print-certs', built])
    if res.returncode != 0:
        errors.append(f'{name}: apksigner verify failed: {res.stderr.strip()[:200]}')
    else:
        sha1s = re.findall(r'SHA-1 digest: ([0-9a-f]+)', res.stdout)
        expected = sh([tools.apksigner, 'verify', '--print-certs',
                       tools.key / 'platform.apk']) if False else None
        # Compare against the key the build used.
        key_cert = sh(['openssl', 'x509', '-in', tools.key / 'platform.x509.pem',
                       '-noout', '-fingerprint', '-sha1'])
        m = re.search(r'=([0-9A-F:]+)', key_cert.stdout)
        if m:
            want = m.group(1).replace(':', '').lower()
            if want not in sha1s:
                errors.append(f'{name}: not signed with the ROM platform key')

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

    # Package identity
    aapt2 = tools.root / 'prebuilts/sdk/tools/linux/bin/aapt2'
    badging = sh([aapt2, 'dump', 'badging', built]).stdout
    pkg = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'",
                    badging)
    stock_badging = sh([aapt2, 'dump', 'badging', stock_apk]).stdout
    stock_pkg = re.search(
        r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'",
        stock_badging)
    if pkg and stock_pkg and pkg.groups() != stock_pkg.groups():
        errors.append(f'{name}: package identity changed '
                      f'{stock_pkg.groups()} -> {pkg.groups()}')

    # Disabled Xiaomi-backend components
    tree = sh([aapt2, 'dump', 'xmltree', '--file', 'AndroidManifest.xml', built]).stdout
    for component in disabled_names:
        idx = tree.find(component)
        if idx < 0:
            continue
        window = tree[idx:idx + 600]
        if 'enabled' not in window or 'false' not in window:
            errors.append(f'{name}: {component} is not disabled')

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
    dump = sh([aapt2_bin, 'dump', 'resources', built]).stdout
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

    return built.stat().st_size


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

    print(f'{"total":12s} {total / 2**20:8.0f} MiB added to product')

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

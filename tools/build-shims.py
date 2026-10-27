#!/usr/bin/env python3
"""Compile the shim sources, build a DEX, and check coverage against the app.

Run after editing anything under shims/. It fails if a shim does not compile, if
the DEX cannot be produced, or if the ported apps reference a MIUI/Xiaomi class
or member that neither the app nor the shims provide.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(cmd, **kw):
    print('+', ' '.join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom-root', required=True, type=Path)
    p.add_argument('--app-smali', required=True, type=Path,
                   help='decoded smali tree of the app being checked')
    p.add_argument('--keep', type=Path, help='keep intermediates here')
    a = p.parse_args()

    rom = a.rom_root.resolve()
    framework = (rom / 'out/soong/.intermediates/frameworks/base/framework'
                 '/android_common/turbine-combined/framework.jar')
    android_jar = rom / 'prebuilts/sdk/current/public/android.jar'
    d8 = rom / 'out/host/linux-x86/bin/d8'
    baksmali = rom / 'prebuilts/extract-tools/common/smali/baksmali.jar'
    java = Path(shutil.which('java') or 'java')
    javac = shutil.which('javac')
    if not javac:
        raise SystemExit('javac not found on PATH')

    for required in (framework, android_jar, d8, baksmali):
        if not required.exists():
            raise SystemExit(f'missing tool or artifact: {required}')

    work = a.keep or Path(tempfile.mkdtemp(prefix='apps-nabu-shim-'))
    work.mkdir(parents=True, exist_ok=True)
    classes = work / 'classes'
    dexdir = work / 'dex'
    smali = work / 'smali'
    for d in (classes, dexdir):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    sources = sorted(
        list((ROOT / 'shims/src').rglob('*.java'))
        + list((ROOT / 'shims/compile-stubs/src').rglob('*.java')))
    run([javac, '-source', '17', '-target', '17', '-Xlint:-options', '-nowarn',
         '-classpath', f'{framework}:{android_jar}', '-d', classes, *sources])

    run([d8, '--min-api', '33', '--lib', android_jar, '--output', dexdir]
        + sorted(classes.rglob('*.class')))

    run([java, '-jar', baksmali, 'd', dexdir / 'classes.dex', '-o', smali])

    coverage = ROOT / 'tools/check-shim-coverage.py'
    result = subprocess.run(
        [sys.executable, str(coverage), str(a.app_smali), str(smali),
         str(framework)])
    if result.returncode != 0:
        raise SystemExit('shim coverage check failed')

    shim_count = len(list(smali.rglob('*.smali')))
    print(f'\nPASS: {shim_count} shim classes compile and cover every reference')
    if not a.keep:
        shutil.rmtree(work)


if __name__ == '__main__':
    main()

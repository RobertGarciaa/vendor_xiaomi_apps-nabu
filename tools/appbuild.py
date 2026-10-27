#!/usr/bin/env python3
"""Shared build helpers for the ported apps.

The pipeline is deliberately the same for every app:

  1. verify the pinned stock APK hash
  2. decode resources with the pinned stock resource frameworks
  3. decode DEX to smali
  4. replace only the DEX and the compiled manifest
  5. keep every original resource, asset and native byte identical
  6. align (16 KB), sign with the build platform key, verify the signature
  7. record source/tool/framework hashes for reproducibility

Nothing here rewrites a stock resource or native payload. That rule exists
because these apps derive asset names from resource paths and would break if the
resource table were regenerated.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID_NS = 'http://schemas.android.com/apk/res/android'

FRAMEWORKS = (
    'system/system/framework/framework-res.apk',
    'system_ext/app/miuisystem/miuisystem.apk',
)


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open('rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def read_pins():
    pins = {}
    for line in (ROOT / 'proprietary-files.txt').read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        src, sha1 = line.split('|', 1)
        pins[src.strip()] = sha1.strip()
    return pins


def verify_pin(rel_path: str) -> Path:
    pins = read_pins()
    if rel_path not in pins:
        raise SystemExit(f'not pinned: {rel_path}')
    path = ROOT / 'proprietary' / rel_path
    if not path.is_file():
        raise SystemExit(f'missing pinned input: {path}')
    actual = sha1_file(path)
    if actual != pins[rel_path]:
        raise SystemExit(
            f'wrong stock input: {path}\n  expected {pins[rel_path]}\n  actual   {actual}')
    return path


def run(cmd, **kw):
    printable = ' '.join(str(c) for c in cmd)
    print('+', printable if len(printable) < 300 else printable[:300] + ' ...')
    subprocess.run([str(c) for c in cmd], check=True, **kw)


class RomTools:
    """Paths inside the Android tree that the build needs."""

    def __init__(self, rom_root: Path):
        self.root = rom_root.resolve()
        self.sdk_bin = self.root / 'out/host/linux-x86/bin'
        self.d8 = self.sdk_bin / 'd8'
        self.zipalign = self.sdk_bin / 'zipalign'
        self.apksigner = self.sdk_bin / 'apksigner'
        self.baksmali = self.root / 'prebuilts/extract-tools/common/smali/baksmali.jar'
        self.smali = self.root / 'prebuilts/extract-tools/common/smali/smali.jar'
        self.apktool = self.root / 'prebuilts/extract-tools/common/apktool/apktool.jar'
        self.java = self.root / 'prebuilts/jdk/jdk21/linux-x86/bin/java'
        self.android_jar = self.root / 'prebuilts/sdk/current/public/android.jar'
        self.framework_jar = (self.root / 'out/soong/.intermediates/frameworks/base'
                              '/framework/android_common/turbine-combined/framework.jar')
        # The ROM's real signing keys. PixelOS sets
        #   PRODUCT_DEFAULT_DEV_CERTIFICATE := vendor/lineage-priv/keys/testkey
        # so Soong resolves `certificate: "platform"` against that directory and
        # picks vendor/lineage-priv/keys/platform.*. Pre-signing with the same
        # file keeps a locally verified APK identical to the final image; Soong
        # still re-signs with the same key during the ROM build.
        self.key = self.root / 'vendor/lineage-priv/keys'
        if not (self.key / 'platform.pk8').is_file():
            raise SystemExit(
                'missing ROM signing keys at vendor/lineage-priv/keys/platform.*; '
                'this is the key PixelOS uses for PRODUCT_DEFAULT_DEV_CERTIFICATE')
        if not self.java.exists():
            self.java = Path(shutil.which('java') or 'java')

    def check(self):
        missing = [str(p) for p in
                   (self.d8, self.zipalign, self.apksigner, self.baksmali,
                    self.apktool, self.android_jar)
                   if not Path(p).exists()]
        if missing:
            raise SystemExit('missing build tools:\n  ' + '\n  '.join(missing))


def install_frameworks(tools: RomTools, work: Path) -> Path:
    frame_dir = work / 'framework'
    frame_dir.mkdir(parents=True, exist_ok=True)
    for rel in FRAMEWORKS:
        apk = ROOT / 'proprietary' / rel
        if not apk.is_file():
            raise SystemExit(f'missing pinned framework: {apk}')
        run([tools.java, '-jar', tools.apktool, 'if', apk, '-p', frame_dir])
    return frame_dir


def decode_resources(tools: RomTools, apk: Path, frame_dir: Path, out: Path):
    run([tools.java, '-Xmx6g', '-jar', tools.apktool, 'd', apk,
         '-o', out, '-f', '--no-src', '-p', frame_dir])


def decode_dex(tools: RomTools, apk: Path, out_smali: Path):
    out_smali.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(apk) as z:
        dex_names = [n for n in z.namelist()
                     if n.startswith('classes') and n.endswith('.dex')]
        dex_names.sort()
        for name in dex_names:
            stem = name[:-4]
            target = out_smali / stem
            target.mkdir(exist_ok=True)
            dex = out_smali / name
            dex.write_bytes(z.read(name))
            run([tools.java, '-Xmx6g', '-jar', tools.baksmali, 'd', dex,
                 '-o', target])
            dex.unlink()


def assemble_dex(tools: RomTools, smali_dirs, out_dex: Path, start_index: int = 0):
    """Assemble each smali directory back into classesN.dex.

    Android's dex naming is classes.dex, classes2.dex, classes3.dex, ... — there
    is no classes1.dex. `start_index` counts positions in that sequence, so a
    caller appending extra dex files passes the number already written.
    """
    produced = {}
    for offset, smali_dir in enumerate(smali_dirs):
        position = start_index + offset
        name = 'classes.dex' if position == 0 else f'classes{position + 1}.dex'
        target = out_dex / name
        run([tools.java, '-Xmx6g', '-jar', tools.smali, 'a', smali_dir,
             '-o', target])
        produced[name] = target
    return produced


def build_apk(stock: Path, compiled_manifest: bytes, dex_files: dict,
              extra_entries: dict, out_apk: Path,
              resources_arsc: bytes | None = None,
              native_keep_dir: Path | None = None):
    """Rebuild the APK keeping original entries byte-identical where possible.

    dex_files maps an entry name to a built dex path. extra_entries maps an
    entry name to raw bytes. resources_arsc, when given, replaces the stock
    resources.arsc — required whenever resource values changed (for example an
    added values-ko table), because the arsc holds the string pool.
    If native_keep_dir is given, its symlinked copy of the original lib/ entries
    is reused so no library is recompressed.
    """
    with zipfile.ZipFile(stock) as src, zipfile.ZipFile(out_apk, 'w') as dst:
        dex_names = set(dex_files)
        for entry in src.infolist():
            name = entry.filename
            if name.startswith('META-INF/') and name.upper().endswith(
                    ('.RSA', '.DSA', '.EC', '.SF', 'MANIFEST.MF')):
                continue
            if name in dex_names:
                continue
            if name in extra_entries:
                continue
            if name == 'AndroidManifest.xml':
                data = compiled_manifest
            elif name == 'resources.arsc' and resources_arsc is not None:
                data = resources_arsc
            else:
                data = src.read(name)
            dst.writestr(entry, data)
        for name, path in dex_files.items():
            dst.writestr(name, Path(path).read_bytes(),
                         compress_type=zipfile.ZIP_DEFLATED)
        for name, data in extra_entries.items():
            dst.writestr(name, data, compress_type=zipfile.ZIP_DEFLATED)


def align_and_sign(tools: RomTools, unsigned: Path, aligned: Path, signed: Path):
    run([tools.zipalign, '-f', '-P', '16', '4', unsigned, aligned])
    run([tools.apksigner, 'sign',
         '--key', tools.key / 'platform.pk8',
         '--cert', tools.key / 'platform.x509.pem',
         '--out', signed, aligned])
    run([tools.apksigner, 'verify', signed])


def verify_payload_preserved(stock: Path, built: Path,
                            resources_changed: bool = False):
    """Every original resource, asset, native and unknown entry must be identical.

    resources.arsc is exempt only when the caller added translated resources:
    the string pool lives in that file, so adding a values-ko table necessarily
    changes it. The per-entry res/ payloads are still checked byte for byte.
    """
    checked = 0
    with zipfile.ZipFile(stock) as src, zipfile.ZipFile(built) as dst:
        dst_names = set(dst.namelist())
        for entry in src.infolist():
            name = entry.filename
            if name == 'AndroidManifest.xml':
                continue
            if name == 'resources.arsc' and resources_changed:
                if name not in dst_names:
                    raise SystemExit('resources.arsc missing from rebuilt APK')
                continue
            if name.startswith('classes') and name.endswith('.dex'):
                continue
            if name.startswith('META-INF/'):
                continue
            if name not in dst_names:
                raise SystemExit(f'lost entry during rebuild: {name}')
            if src.read(name) != dst.read(name):
                raise SystemExit(f'changed entry during rebuild: {name}')
            checked += 1
    return checked


def extract_resources_arsc(built_manifest_apk: Path) -> bytes:
    """Read the resources.arsc that aapt2 produced during the resource rebuild.

    apktool writes the rebuilt resource table into the APK it produces, not next
    to the decoded tree, so the caller must pass that APK here.
    """
    with zipfile.ZipFile(built_manifest_apk) as z:
        if 'resources.arsc' not in z.namelist():
            raise SystemExit('aapt2 did not emit resources.arsc')
        return z.read('resources.arsc')


def record_artifacts(app: str, built: Path, inputs):
    """Write a small JSON record next to the built APK (this file is committed)."""
    record = {
        'app': app,
        'apk_sha1': sha1_file(built),
        'apk_sha256': hashlib.sha256(built.read_bytes()).hexdigest(),
        'apk_bytes': built.stat().st_size,
        'inputs': {str(p): sha1_file(p) for p in inputs if Path(p).is_file()},
    }
    out = built.with_suffix('.build.json')
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    return out

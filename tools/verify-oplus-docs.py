#!/usr/bin/env python3
"""Verify document-editor input, payload, signing, build provenance and app-private JNI."""
import argparse,json,subprocess,re,hashlib,zipfile,sys
from pathlib import Path
import appbuild,oplus_docs as port
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom-root',type=Path,required=True);p.add_argument('--apk',type=Path,default=port.OUTPUT);a=p.parse_args()
tools=appbuild.RomTools(a.rom_root);port.verify_payload(a.apk)
appbuild.run(tools.signer('verify',a.apk));appbuild.run([tools.zipalign,'-c','-P','16','4',a.apk])
cert=subprocess.check_output(['openssl','x509','-in',str(tools.key/'platform.x509.pem'),'-noout','-fingerprint','-sha256'],text=True).split('=',1)[1].strip().replace(':','').lower()
signature=subprocess.check_output([str(x) for x in tools.signer('verify','--print-certs',a.apk)],text=True)
assert 'SHA-256 digest: '+cert in signature,'Wrong signing certificate'
record=json.loads(a.apk.with_suffix('.build.json').read_text());assert record['schema']=='oplus-documents-v1'
assert record['apk_sha256']==port.sha256(a.apk)
expected={str(p.relative_to(port.ROOT)):port.sha256(p) for p in port.inputs()};assert record['inputs']==expected,'Stale source/tool record'
with zipfile.ZipFile(a.apk) as z:
    for n,expected in record['dex_sha256'].items():assert hashlib.sha256(z.read(n)).hexdigest()==expected,n
folder=port.ROOT/'proprietary/native'/port.APP;native=port.native(a.apk)
assert {p.name for p in folder.glob('*.so')}==set(native)
for name,data in native.items():assert (folder/name).read_bytes()==data,name
manifest=subprocess.check_output([str(tools.root/'prebuilts/sdk/tools/linux/bin/aapt2'),'dump','badging',str(a.apk)],text=True)
info=port.config();assert "package: name='"+info['package']+"' versionCode='"+str(info['version_code'])+"' versionName='"+info['version_name']+"'" in manifest
assert re.search(r"^(?:sdkVersion|minSdkVersion):'35'$", manifest, re.M) and "targetSdkVersion:'37'" in manifest and "native-code: 'arm64-v8a'" in manifest
assert "application-label-ko:" in manifest
# Verify direct native dependencies against this pinned APK and public Android libraries.
public_native = {'libEGL.so', 'libGLESv2.so', 'libGLESv3.so', 'libandroid.so',
                 'libc.so', 'libdl.so', 'libjnigraphics.so', 'liblog.so',
                 'libm.so', 'libstdc++.so', 'libz.so'}
for name in native:
    dynamic = subprocess.check_output(['readelf', '-d', str(folder / name)], text=True)
    needed = set(re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic))
    assert not needed - set(native) - public_native, (name, needed)
# Use the same manifest/library checker as the ROM build, without a full ROM build.
appbuild.run([sys.executable, tools.root / 'build/soong/scripts/manifest_check.py',
              '--enforce-uses-libraries',
              '--optional-uses-library', 'androidx.window.extensions',
              '--optional-uses-library', 'androidx.window.sidecar',
              '--aapt', tools.root / 'prebuilts/sdk/tools/linux/bin/aapt2', a.apk])
print('PASS: signed/aligned editor, stock identity/payload, 9 nonduplicating DEX, source hashes, 14 private JNI files, direct native dependencies and optional uses-libraries')

"""Pinned, app-local OPlus Documents port helpers. No global framework changes."""
from pathlib import Path
import hashlib,json,zipfile,subprocess,shutil,os,tempfile
ROOT=Path(__file__).resolve().parents[1]
APP='OplusDocuments'
CONFIG=ROOT/'oplus-docs/source.json'
OUTPUT=ROOT/'proprietary/ported/product/app'/APP/(APP+'.apk')
def sha256(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for data in iter(lambda:stream.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def config():return json.loads(CONFIG.read_text())
def stock():
    info=config();p=ROOT/'proprietary'/info['staging']
    if not p.is_file() or sha256(p)!=info['sha256']:raise ValueError('Missing or mismatched OPlus input; run tools/import-oplus-docs.py')
    return p

def native(apk):
    result={}
    with zipfile.ZipFile(apk) as z:
        for name in z.namelist():
            if not name.startswith('lib/') or not name.endswith('.so'):continue
            assert name.startswith('lib/arm64-v8a/') and name.count('/')==2,name
            data=z.read(name)
            assert data[:5]==b'\x7fELF\x02' and int.from_bytes(data[18:20],'little')==183,name
            result[Path(name).name]=data
    assert len(result)==14,'Pinned APK native library count changed'
    return result

def prepare_native(apk):
    files=native(apk);folder=ROOT/'proprietary/native'/APP;folder.mkdir(parents=True,exist_ok=True)
    # This directory belongs to this app only. Refuse stale files instead of deleting them.
    assert not ({p.name for p in folder.glob('*.so')}-set(files)),'Stale OPlus JNI files'
    for name,data in files.items():
        with tempfile.NamedTemporaryFile(dir=folder,delete=False) as stream:
            temporary=Path(stream.name);stream.write(data)
        try:os.replace(temporary,folder/name)
        finally:temporary.unlink(missing_ok=True)
    manifest={name:{'sha256':hashlib.sha256(data).hexdigest(),'size':len(data)} for name,data in sorted(files.items())}
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

def inputs():
    return [CONFIG,ROOT/'tools/oplus_docs.py',ROOT/'tools/appbuild.py',ROOT/'tools/dex_classes.py',ROOT/'tools/build-oplus-docs.py',stock(),*sorted((ROOT/'oplus-docs/patches').glob('*.patch')),*sorted((ROOT/'oplus-docs/compat/src').rglob('*.java'))]

def record(apk):
    with zipfile.ZipFile(apk) as z:
        dex={n:hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if n.startswith('classes') and n.endswith('.dex')}
    data={'schema':'oplus-documents-v1','apk_sha256':sha256(apk),'inputs':{str(p.relative_to(ROOT)):sha256(p) for p in inputs()},'dex_sha256':dex}
    Path(apk).with_suffix('.build.json').write_text(json.dumps(data,indent=2)+'\n')

def verify_payload(apk):
    info=config();changed=set(info['patched_dex']);expected_dex={f'classes{i if i>1 else ""}.dex' for i in range(1,10)}
    with zipfile.ZipFile(stock()) as a,zipfile.ZipFile(apk) as b:
        assert len(b.namelist())==len(set(b.namelist())),'Duplicate ZIP entries'
        dex={n for n in b.namelist() if n.startswith('classes') and n.endswith('.dex')}
        assert dex==expected_dex,sorted(dex)
        assert set(b.namelist())-set(a.namelist())-{'classes9.dex'}<= {n for n in b.namelist() if n.startswith('META-INF/')},'Unexpected APK entries'
        for n in a.namelist():
            if n.startswith('META-INF/'):continue
            assert n in b.namelist(),n
            if n not in changed:assert a.read(n)==b.read(n),'Unexpected payload modification: '+n
        from dex_classes import class_descriptors
        seen=set()
        for n in sorted(dex):
            names=class_descriptors(b.read(n));assert len(names)==len(set(names)),n
            assert not seen.intersection(names),'Duplicate DEX classes: '+n
            seen.update(names)
        added=set(class_descriptors(b.read('classes9.dex')))
        assert added=={'Lcom/oplus/os/OplusBuild;','Lcom/oplus/os/OplusBuild$VERSION;','Lcom/oplus/content/OplusFeatureConfigManager;','Landroid/os/OplusSystemProperties;','Lcom/oplus/os/OplusUsbEnvironment;'},added
    return True

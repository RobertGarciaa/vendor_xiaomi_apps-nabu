#!/usr/bin/env python3
"""Build the pinned document editor with scoped patches and private compatibility DEX."""
import argparse,shutil,tempfile,zipfile,subprocess
from pathlib import Path
import appbuild,oplus_docs as port
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--rom-root',required=True,type=Path);p.add_argument('--output',type=Path,default=port.OUTPUT);p.add_argument('--keep-work',type=Path);a=p.parse_args()
tools=appbuild.RomTools(a.rom_root);tools.check();stock=port.stock();info=port.config()
with tempfile.TemporaryDirectory(prefix='nabu-oplus-docs-') as temporary:
    work=a.keep_work or Path(temporary);work.mkdir(parents=True,exist_ok=True);smali=work/'smali';smali.mkdir(exist_ok=True)
    replacements={}
    with zipfile.ZipFile(stock) as z:
        manifest=z.read('AndroidManifest.xml')
        for dex_name in info['patched_dex']:
            raw=work/dex_name;raw.write_bytes(z.read(dex_name));out=smali/raw.stem
            if out.exists():shutil.rmtree(out)
            appbuild.run([tools.java,'-Xmx6g','-jar',tools.baksmali,'d',raw,'-o',out])
    for patch in sorted((port.ROOT/'oplus-docs/patches').glob('*.patch')):
        appbuild.run(['patch','--batch','--fuzz=0','-p1','-i',patch],cwd=smali)
    for stem,index in [('classes',0),('classes6',5)]:
        out=work/('built-'+stem);out.mkdir(exist_ok=True)
        replacements.update(appbuild.assemble_dex(tools,[smali/stem],out,start_index=index))
    classes=work/'compat-classes';classes.mkdir(exist_ok=True);dex=work/'compat-dex';dex.mkdir(exist_ok=True)
    sources=sorted((port.ROOT/'oplus-docs/compat/src').rglob('*.java'))
    appbuild.run([tools.root/'prebuilts/jdk/jdk21/linux-x86/bin/javac','-source','17','-target','17','-Xlint:-options','-classpath',tools.android_jar,'-d',classes,*sources])
    appbuild.run([tools.d8,'--min-api','35','--output',dex,*sorted(classes.rglob('*.class'))])
    replacements['classes9.dex']=dex/'classes.dex'
    unsigned=work/'unsigned.apk';signed=work/'signed.apk'
    appbuild.build_apk(stock,manifest,replacements,{},unsigned)
    aligned=work/'aligned.apk'
    appbuild.run([tools.zipalign,'-f','-P','16','4',unsigned,aligned])
    appbuild.run(tools.signer('sign','--alignment-preserved','true','--key',tools.key/'platform.pk8','--cert',tools.key/'platform.x509.pem','--out',signed,aligned))
    appbuild.run(tools.signer('verify',signed))
    appbuild.run([tools.zipalign,'-c','-P','16','4',signed])
    port.verify_payload(signed)
    a.output.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(signed,a.output)
    port.prepare_native(a.output);port.record(a.output)
    print('PASS:',a.output,'; original manifest/resources/assets/native retained; 14 app-private JNI files prepared')

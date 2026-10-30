#!/usr/bin/env python3
"""Import only the pinned OPlus document APK; never modify or clear a dump."""
import argparse,os,shutil,tempfile
from pathlib import Path
import oplus_docs as port
p=argparse.ArgumentParser(description=__doc__)
g=p.add_mutually_exclusive_group();g.add_argument('--dump',type=Path);g.add_argument('--apk',type=Path)
p.add_argument('--verify-only',action='store_true');a=p.parse_args();info=port.config()
if a.verify_only:
    print('PASS:',port.stock());raise SystemExit
if a.dump is None and a.apk is None:p.error('provide --dump or --apk')
source=a.apk if a.apk else a.dump/info['dump_path']
if not source.is_file() or port.sha256(source)!=info['sha256']:raise SystemExit('Wrong OPlus input: '+str(source))
target=port.ROOT/'proprietary'/info['staging'];target.parent.mkdir(parents=True,exist_ok=True)
with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as stream:temporary=Path(stream.name)
try:
    shutil.copyfile(source,temporary)
    assert port.sha256(temporary)==info['sha256']
    os.replace(temporary,target)
finally:temporary.unlink(missing_ok=True)
print('Verified and imported:',target)

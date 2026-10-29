#!/usr/bin/env python3
"""Install Qt's absolute nativeLibraryDir payload for read-only system apps."""
from pathlib import Path
import zipfile,hashlib,json,argparse
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args();root=a.root
records=[]
for app in ['Creation']:
 apk=root/'proprietary/ported/product/app'/app/(app+'.apk')
 with zipfile.ZipFile(apk) as z:
  for n in sorted(z.namelist()):
   if not n.startswith('lib/arm64-v8a/') or not n.endswith('.so'):continue
   name=Path(n).name;assert n=='lib/arm64-v8a/'+name
   data=z.read(n);target=root/'proprietary/native'/app/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
   records.append({'app':app,'file':name,'sha256':hashlib.sha256(data).hexdigest(),'size':len(data)})
(root/'proprietary/native/manifest.json').write_text(json.dumps(records,indent=2)+'\n')
print(len(records),'libraries,',sum(r['size'] for r in records),'bytes')

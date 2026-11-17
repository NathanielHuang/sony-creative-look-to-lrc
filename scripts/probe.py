#!/usr/bin/env python3
"""Read camera headers and local environment without installing or changing settings."""
from pathlib import Path
import argparse,json,platform,plistlib,shutil,subprocess,sys
from common import KIT,read,dump,sha,camera_header,read_metadata

def probe(paths):
 known={read(p)['model']:p.parent for p in (KIT/'adapters').glob('*/adapter.json')}
 rows=[]
 for arg in paths:
  p=Path(arg);files=sorted(p.rglob('*')) if p.is_dir() else [p]
  for p in files:
   if not p.is_file() or p.suffix.lower() not in ['.arw','.jpg','.jpeg']:continue
   row={'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p)}
   try:
    header=camera_header(p);row.update(header)
    a=known.get(header.get('model'))
    row['adapter']=a.name if a else None
    row['next_step']='验证配方和成对样本' if a else '建立该机型适配并用样本验证'
    if a:
     try:row['metadata']=read_metadata(p,read(a/'adapter.json'),a/'reader.py')
     except Exception as e:row['metadata_error']=str(e)
   except Exception as e:row['header_error']=str(e)
   rows.append(row)
 apps=[]
 for f in Path('/Applications').glob('*Lightroom*/*.app/Contents/Info.plist'):
  try:
   x=plistlib.loads(f.read_bytes());apps.append({'path':str(f.parents[1]),'version':x.get('CFBundleShortVersionString')})
  except Exception:pass
 return {'environment':{'os':platform.platform(),'python':sys.version.split()[0],'exiftool':shutil.which('exiftool'),'lightroom':apps},'files':rows,'note':'空字段由Agent继续检测或询问。header_error样本可用ExifTool只读检查。'}
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('paths',nargs='*');ap.add_argument('--report',required=True);args=ap.parse_args()
 result=probe(args.paths);dump(args.report,result);print(json.dumps({'report':args.report,'files':len(result['files'])},ensure_ascii=False))

#!/usr/bin/env python3
"""Sony creator-look preparation. Default: report only; --write creates XMP."""
from pathlib import Path
import argparse,json,sys
from metadata import read_metadata,identify
from config import load_recipes
RECIPES=load_recipes()
from xmp_merge import merge,write_atomic,sha
from paths import data_root
ROOT=Path(__file__).resolve().parents[1]

def sidecar_path(path):
 matches=[p for p in path.parent.iterdir() if p.name.casefold()==path.with_suffix('.xmp').name.casefold()]
 if len(matches)>1: raise ValueError('Multiple case-variant XMP files; inspect manually')
 return matches[0] if matches else path.with_suffix('.xmp')

def files(args):
 found=[]
 for item in args:
  p=Path(item)
  found.extend(sorted(p.rglob('*')) if p.is_dir() else [p])
 return list(dict.fromkeys(p.resolve() for p in found if p.is_file() and p.suffix.lower()=='.arw'))

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('paths',nargs='+');ap.add_argument('--write',action='store_true')
 ap.add_argument('--replace-look',action='store_true',help='Replace only profile/look in an existing sidecar; back up first. Run with LRC closed.')
 ap.add_argument('--native',action='store_true',help='Generate capture-specific tables; requires NumPy and a supported Imaging Edge Edit installation.')
 ap.add_argument('--report');ap.add_argument('--profiles-dir',default=str(data_root()/'generated-profiles'))
 args=ap.parse_args();rows=[];failed=False
 for path in files(args.paths):
  row={'file':str(path)}
  try:
   meta=read_metadata(path); key=identify(meta);row.update(recipe=key,metadata=meta)
   if key is None: row['status']='unmatched'
   else:
    row['name']=RECIPES[key]['name'];side=sidecar_path(path)
    original=side.read_bytes() if side.exists() else None
    if not args.write: row.update(status='planned',sidecar_exists=original is not None)
    else:
     raw_hash=sha(path.read_bytes())
     if args.native:
      from build_profiles import build
      profile=build(path,args.profiles_dir)
     else:
      item=next(r for r in json.loads((ROOT/'profiles.json').read_text(encoding='utf-8')) if r['recipe']==key)
      profile=dict(item,profile=str(ROOT/item['file']),mode='fixed-recipe')
     data,status=merge(original,profile['profile'],args.replace_look)
     if sha(path.read_bytes())!=raw_hash: raise ValueError('RAW changed during preparation')
     backup=None
     if status!='unchanged': backup=write_atomic(side,data,original,data_root()/'backups')
     row.update(status=status,sidecar=str(side),profile=profile,backup=backup,raw_sha256=raw_hash)
  except Exception as e: failed=True;row.update(status='error',error=str(e))
  rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 if args.report: Path(args.report).write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 return 1 if failed else 0

if __name__=='__main__':sys.exit(main())

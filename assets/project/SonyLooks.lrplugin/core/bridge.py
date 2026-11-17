"""Local, read-only recipe matching. Only the Python standard library is required."""
from pathlib import Path
import json,sys
from metadata import read_metadata,identify
from xmp_merge import profile_settings
from config import load_adapter
ROOT=Path(__file__).resolve().parents[1]

def lua(v):
 if isinstance(v,dict):return '{'+','.join('['+lua(k)+']='+lua(x) for k,x in v.items())+'}'
 if isinstance(v,list):return '{'+','.join(lua(x) for x in v)+'}'
 if isinstance(v,str):return '"'+''.join('\\%03d'%ord(c) if ord(c)<32 else ('\\'+c if c in '\\"' else c) for c in v)+'"'
 if v is None:return 'nil'
 if isinstance(v,bool):return str(v).lower()
 return repr(v)

def match(paths,allow_recipe_profile=True):
 catalog=json.loads((ROOT/'profiles.json').read_text(encoding='utf-8'))
 registry={(r['recipe'],r['signature']):r for r in catalog if r.get('signature')};rows=[]
 adapter=load_adapter()
 for path in paths:
  row={'path':path}
  try:
   meta=read_metadata(path);key=identify(meta)
   if key is None:row['status']='unmatched'
   else:
    try:
     sig=None
     if adapter.get('signature_engine')=='sony_sr2_v1':
      from native_signature import capture_signature
      sig=capture_signature(path,meta['style'])
    except Exception as e:sig=None;row['signature_note']=str(e)
    profile=registry.get((key,sig));mode='capture_table'
    if profile is None and allow_recipe_profile:
     profile=next((r for r in catalog if r['recipe']==key),None);mode='recipe_profile'
    if profile is None:row.update(status='needs_preimport',reason='No registered profile matches this capture')
    else:
     target=(ROOT/profile['file']).resolve();target.relative_to(ROOT)
     look,params=profile_settings(target)
     look['Amount']=1
     for field in ('SupportsAmount','SupportsMonochrome','SupportsOutputReferred'):look[field]=False
     params={k:v for k,v in params.items() if not k.startswith('Table_')}
     params['ConvertToGrayscale']=False;look['Parameters']=params
     row.update(status='matched',recipe=key,name=profile['name'],match_mode=mode,capture_signature=sig,profile_signature=profile['signature'],settings={'CameraProfile':profile['base'],'Look':look})
  except Exception as e:row.update(status='error',reason=str(e))
  rows.append(row)
 return rows

if __name__=='__main__':
 request,result=sys.argv[1:3]
 rows=match(json.loads(Path(request).read_text(encoding='utf-8')),allow_recipe_profile='--strict' not in sys.argv[3:])
 Path(result).write_text('return '+lua(rows),encoding='utf-8')

"""Shared kit checks. Reads source assets; generated files belong in a separate project."""
from pathlib import Path
import hashlib,json,re,sys
KIT=Path(__file__).resolve().parents[1]
CORE=KIT/'assets/project/SonyLooks.lrplugin/core'
sys.path.insert(0,str(CORE))
from metadata import read_metadata,identify,camera_header
from xmp_merge import parse,description,attribute,profile_settings

def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def dump(path,obj):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def contained(root,relative):
 p=(Path(root)/relative).resolve();p.relative_to(Path(root).resolve());return p

def adapter_files(folder):
 folder=Path(folder).resolve();a=read(folder/'adapter.json');recipes=read(folder/'recipes.json')
 if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',a['id']):raise ValueError('Invalid adapter id')
 for key in ['model','dcp_model','adobe_profile_filename','base_name','reader','fields','base_mode']:
  if not a.get(key):raise ValueError('Missing adapter field: '+key)
 if any(c in a['base_name'] for c in '/\\\0'):raise ValueError('Invalid base name')
 if a['reader'] not in ['sony_makernote','custom']:raise ValueError('Unknown reader')
 if a['reader']=='custom' and not (folder/'reader.py').is_file():raise ValueError('Missing reader.py')
 if a['base_mode'] not in ['linear_from_adobe','provided']:raise ValueError('Unknown base mode')
 if not recipes:raise ValueError('No recipes defined')
 names=set();fingerprints=set()
 for key,r in recipes.items():
  if not re.fullmatch(r'[a-z0-9_-]+',key):raise ValueError('Invalid recipe id')
  name=r['name']
  if not name or any(c in name for c in '/\\<>:"|?*\0') or name[-1] in ' .':raise ValueError('Invalid visible name: '+name)
  if name.casefold() in names:raise ValueError('Duplicate visible name')
  names.add(name.casefold())
  if len(r['values'])!=len(a['fields']) or any(v is None for v in r['values']) or r.get('style') is None:raise ValueError('Incomplete recipe: '+key)
  signature=json.dumps([r['style'],r['values']],sort_keys=True)
  if signature in fingerprints:raise ValueError('Ambiguous recipe fingerprints')
  fingerprints.add(signature)
 return folder,a,recipes

def validate_samples(folder,manifest):
 folder,a,recipes=adapter_files(folder);manifest=Path(manifest).resolve();data=read(manifest)
 pairs=data.get('pairs',[])
 if not pairs:raise ValueError('No paired samples')
 rows=[];covered=set();used=set()
 for pair in pairs:
  key=pair['recipe']
  if key not in recipes:raise ValueError('Unknown recipe in manifest: '+key)
  raw=(manifest.parent/pair['arw']).resolve();jpg=(manifest.parent/pair['jpeg']).resolve()
  if raw.suffix.lower()!='.arw' or jpg.suffix.lower() not in ('.jpg','.jpeg'):raise ValueError('Expected original ARW + JPEG')
  if raw in used:raise ValueError('ARW assigned more than once')
  used.add(raw)
  before={str(p):sha(p) for p in [raw,jpg]}
  result=[]
  for p in [raw,jpg]:
   m=read_metadata(p,a,folder/'reader.py')
   if identify(m,a,recipes)!=key:raise ValueError('Sample does not match declared recipe: '+str(p))
   result.append(m)
  if result[0].get('date') and result[1].get('date') and result[0]['date']!=result[1]['date']:raise ValueError('ARW/JPEG capture time mismatch')
  if any(sha(p)!=before[str(p)] for p in [raw,jpg]):raise ValueError('Source changed during validation')
  covered.add(key);rows.append({'recipe':key,'name':recipes[key]['name'],'arw':str(raw),'jpeg':str(jpg),'sha256':before,'metadata':result,'lighting':pair.get('lighting','未标注')})
 missing=set(recipes)-covered
 if missing:raise ValueError('Missing paired samples for: '+', '.join(sorted(missing)))
 return {'adapter_id':a['id'],'model':a['model'],'pair_count':len(rows),'recipes':len(covered),'metadata_result':'passed','render_result':'pending_lrc_validation','samples':rows}

def validate_profiles(folder):
 folder,a,recipes=adapter_files(folder);profiles=read(folder/'profiles.json');keys=set();ids=set()
 if a['base_mode']=='provided' and not (folder/'base.dcp').is_file():raise ValueError('Missing base.dcp')
 for row in profiles:
  key=row['recipe']
  if key not in recipes or key in keys:raise ValueError('Unknown or duplicate profile recipe')
  p=contained(folder,row['file']);look,params=profile_settings(p);d=description(parse(p.read_bytes()))
  if look['Name']!=recipes[key]['name'] or row['name']!=look['Name']:raise ValueError('Profile name differs from recipe name')
  if not re.fullmatch('[0-9A-Fa-f]{32}',look['UUID']) or look['UUID'] in ids:raise ValueError('Invalid or duplicate profile UUID')
  if look['UUID']!=row['uuid']:raise ValueError('Profile UUID mismatch')
  if attribute(d,'CameraModelRestriction')!=a['dcp_model']:raise ValueError('Profile camera restriction mismatch')
  if params.get('CameraProfile')!=a['base_name'] or row['base']!=a['base_name']:raise ValueError('Profile base mismatch')
  if not params.get('RGBTable') or not params.get('Table_'+params['RGBTable']):raise ValueError('Missing RGB color table')
  keys.add(key);ids.add(look['UUID'])
 if keys!=set(recipes):raise ValueError('Every recipe needs one profile')
 return profiles

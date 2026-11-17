#!/usr/bin/env python3
"""Install or repair the configured Sony Lightroom plugin and profiles."""
from pathlib import Path
import re
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile,time,uuid
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'SonyLooks.lrplugin'
ADAPTER=json.loads((SOURCE/'adapter.json').read_text(encoding='utf-8'))
if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}',ADAPTER['id']):raise ValueError('Invalid adapter id')
PACKAGE='SonyCreativeLooks-'+ADAPTER['id']
sys.path.insert(0,str(SOURCE/'core'))
from base_profile import build_base,find_adobe_profile,BASE
from paths import data_root
from bridge import lua
from xmp_merge import profile_settings,parse,description,attribute

def locations(home=None):
 home=Path(home or Path.home())
 if os.name=='nt':support=Path(os.environ['APPDATA']) if home==Path.home() else home/'AppData/Roaming'
 elif sys.platform=='darwin':support=home/'Library/Application Support'
 else:raise RuntimeError('当前安装器支持macOS和Windows。')
 adobe=support/'Adobe'
 return {'plugin':adobe/('Lightroom/Modules/'+PACKAGE+'.lrplugin'),
 'profiles':adobe/('CameraRaw/Settings/'+PACKAGE),
 'base':adobe/('CameraRaw/CameraProfiles/'+PACKAGE),
 'data':support/PACKAGE}

def lightroom_running():
 if sys.platform=='darwin':return subprocess.run(['pgrep','-x','Adobe Lightroom Classic'],stdout=subprocess.DEVNULL).returncode==0
 if os.name=='nt':return 'lightroom.exe' in subprocess.check_output(['tasklist','/FI','IMAGENAME eq Lightroom.exe'],text=True).lower()
 return False

def deploy(target,source,backup):
 target.parent.mkdir(parents=True,exist_ok=True)
 temp=Path(tempfile.mkdtemp(prefix='.'+target.name+'-',dir=target.parent))
 shutil.copytree(source,temp,dirs_exist_ok=True)
 moved=False
 try:
  if target.exists():
   backup.parent.mkdir(parents=True,exist_ok=True);os.replace(target,backup);moved=True
  os.replace(temp,target)
 except Exception:
  if moved and not target.exists():os.replace(backup,target)
  raise
 finally:
  if temp.exists():shutil.rmtree(temp)

def install(home=None,adobe=None,dry_run=False):
 if (ROOT/'DRAFT.json').exists():raise ValueError('草稿仅供制作配置。请先验证样本，再组装安装版。')
 dest=locations(home)
 profiles=json.loads((SOURCE/'profiles.json').read_text(encoding='utf-8'))
 if not profiles:raise ValueError('No profiles supplied')
 if any(c in BASE for c in '/\\\0'):raise ValueError('Invalid base name')
 seen=set();ids=set()
 for item in profiles:
  p=(SOURCE/item['file']).resolve();p.relative_to(SOURCE.resolve())
  look,params=profile_settings(p)
  if look['UUID']!=item['uuid'] or params['CameraProfile']!=item['base']:raise ValueError('Profile identity mismatch: '+item['name'])
  if item['recipe'] in seen:raise ValueError('Duplicate recipe')
  if not item['name'] or any(c in item['name'] for c in '/\\<>:"|?*\0') or item['name'][-1] in ' .':raise ValueError('Invalid profile name')
  if look['Name']!=item['name'] or attribute(description(parse(p.read_bytes())),'CameraModelRestriction')!=ADAPTER['dcp_model']:raise ValueError('Profile name or camera mismatch')
  if item['uuid'] in ids:raise ValueError('Duplicate profile UUID')
  ids.add(item['uuid']);seen.add(item['recipe'])
 base_source=SOURCE/'base.dcp'
 if ADAPTER['base_mode']=='provided':
  base=base_source.read_bytes()
  if base[:4]!=b'IIRC':raise ValueError('Invalid provided DCP header')
  from metadata import Tiff
  blob=bytearray(base);blob[2:4]=b'\x2a\x00';t=Tiff(bytes(blob));tags=t.ifd(t.unpack('I',4)[0])
  if tags.get(50708,('',0))[0]!=ADAPTER['dcp_model'] or tags.get(50936,('',0))[0]!=BASE:raise ValueError('Provided DCP identity mismatch')
 elif ADAPTER['base_mode']=='linear_from_adobe':base=build_base(find_adobe_profile(adobe))
 else:raise ValueError('Unknown base mode')
 if dry_run:return {k:str(v) for k,v in dest.items()}
 if home is None and lightroom_running():raise RuntimeError('请先完全退出LRC，再运行安装。')
 backup=dest['data']/'安装备份'/(time.strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6])
 # Unknown assets in our dedicated old folder are retained in the new folder too.
 with tempfile.TemporaryDirectory(prefix='sony-looks-install-') as td:
  stage=Path(td);plug=stage/'plugin';colors=stage/'profiles';dcp=stage/'base'
  shutil.copytree(SOURCE,plug,ignore=shutil.ignore_patterns('__pycache__','*.pyc','reports','cache','Config.lua'))
  config={'python':sys.executable,'dataDir':str(dest['data']),'displayName':'索尼创作者外观 '+ADAPTER['model'],'lookNames':'、'.join(x['name'] for x in profiles)}
  (plug/'Config.lua').write_text('return '+lua(config)+'\n',encoding='utf-8')
  colors.mkdir();dcp.mkdir()
  ids={x['uuid'] for x in profiles}
  if dest['profiles'].exists():
   for p in dest['profiles'].iterdir():
    if not p.is_file():raise ValueError('Unexpected subfolder in managed profiles: '+str(p))
    known=False
    if p.suffix.lower()=='.xmp':
     try:known=profile_settings(p)[0]['UUID'] in ids
     except Exception:pass
    if not known:shutil.copy2(p,colors/p.name)
  for item in profiles:shutil.copy2(SOURCE/item['file'],colors/(item['name']+'.xmp'))
  if dest['base'].exists():shutil.copytree(dest['base'],dcp,dirs_exist_ok=True)
  (dcp/(BASE+'.dcp')).write_bytes(base)
  # Validate all payloads before replacing the installed directories.
  done=[]
  try:
   for key,folder in [('profiles',colors),('base',dcp),('plugin',plug)]:
    prior=dest[key].exists();deploy(dest[key],folder,backup/key);done.append((key,prior))
  except Exception:
   for key,prior in reversed(done):
    shutil.rmtree(dest[key])
    if prior:os.replace(backup/key,dest[key])
   raise
 dest['data'].mkdir(parents=True,exist_ok=True)
 manifest={'version':'0.4.0','python':sys.executable,'paths':{k:str(v) for k,v in dest.items()},'profiles':[]}
 for p in sorted(dest['profiles'].glob('*.xmp')):manifest['profiles'].append({'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 (dest['data']/'安装记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 return manifest

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--adobe-profile');ap.add_argument('--dry-run',action='store_true')
 args=ap.parse_args()
 try:
  result=install(adobe=args.adobe_profile,dry_run=args.dry_run)
  print(json.dumps(result,ensure_ascii=False,indent=2));print('\n安装检查完成。' if args.dry_run else '\n安装完成。重新打开LRC即可使用。')
 except Exception as e:print('安装未完成：'+str(e),file=sys.stderr);sys.exit(1)

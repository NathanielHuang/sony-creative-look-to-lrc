"""Build native, capture-specific Sony RGBTable profiles without altering ARWs."""
from pathlib import Path
import argparse, hashlib, json, os, sys
ROOT=Path(__file__).resolve().parents[1]
VENDOR=ROOT/'vendor'/'sony-look-bridge'
for folder in ('sonylook','capture_one','camera_raw'): sys.path.insert(0,str(VENDOR/folder))
from paths import data_root
os.environ.setdefault('SONYLOOK_CACHE_DIR',str(data_root()/'cache'))
from metadata import read_metadata, identify
from config import load_adapter,load_recipes
ADAPTER=load_adapter();RECIPES=load_recipes()

def build(path, out=None, grid=64, label=None):
 if ADAPTER.get('renderer')!='sony_sr2':raise ValueError('This adapter requires a different profile builder')
 import numpy as np
 import sony_render as R
 import acr_profiles as A
 import acr_look as AL
 import acr_encoding as E
 import c1_look_profile as C
 meta=read_metadata(path); key=identify(meta)
 if key is None: raise ValueError('Unknown recipe: '+str(path))
 looks=R.load_looks(str(path),neutral=False)
 name=meta['style']
 # The main IFD already includes camera contrast/highlight/shadow and the
 # captured three-source matrix. Saturation is already in the RGB2YCC tags.
 # Adding the camera slider numbers again would apply the look twice.
 look=R.Look(name,looks,fade=meta['fade'],chroma_suppress=False)
 signature=hashlib.sha256(json.dumps({'version':1,'look':looks[name],
                 'main':looks['_main'],'grid':grid},sort_keys=True).encode()).hexdigest()[:12]
 out=Path(out or data_root()/'generated-profiles'); out.mkdir(parents=True,exist_ok=True)
 A.OUT=out; A.MODEL=ADAPTER['dcp_model']; A.PREFIX='Sony '+ADAPTER['model']
 A.GROUP='索尼创作者外观'; A.BASE_NAME=ADAPTER['base_name']
 from base_profile import find_adobe_profile
 A.ADOBE_STD=find_adobe_profile()
 from base_profile import build_base
 (out/(A.BASE_NAME+'.dcp')).write_bytes(build_base(A.ADOBE_STD))
 title=label or RECIPES[key].get('english',key)+' '+signature
 target=out/(A.PREFIX+' '+title+'.xmp')
 if not target.exists():
  lin=np.minimum(E.inverse(A.grid(grid)),E.CLIP)
  values=AL.srgb_to_prophoto_v(C.look_srgb(look,lin))
  if not np.isfinite(values).all(): raise ValueError('Non-finite color transform')
  target=A.write_look(title,values)
  from xml.dom import minidom
  doc=minidom.parse(str(target))
  for field,value in [('Name',RECIPES[key]['name']),('Group','索尼创作者外观')]:
   element=doc.getElementsByTagNameNS('http://ns.adobe.com/camera-raw-settings/1.0/',field)[0]
   item=element.getElementsByTagNameNS('http://www.w3.org/1999/02/22-rdf-syntax-ns#','li')[0]
   if item.firstChild:item.firstChild.data=value
   else:item.appendChild(doc.createTextNode(value))
  target.write_bytes(doc.toxml(encoding='utf-8'))
 return dict(recipe=key,name=RECIPES[key]['name'],profile=str(target),
             base=A.BASE_NAME,signature=signature,grid=grid,
             source=meta, matrix_weights=looks['_main']['0x7848'],
             mode='native-as-shot', spatial_effects='Adobe defaults; Sony DRO/sharpness/clarity not reproduced')

if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('files',nargs='+'); ap.add_argument('--out'); ap.add_argument('--grid',type=int,default=64)
 ap.add_argument('--report');args=ap.parse_args(); rows=[]
 for f in args.files:
  row=build(f,args.out,args.grid); rows.append(row); print(json.dumps(row,ensure_ascii=False),flush=True)
 report=Path(args.report) if args.report else Path(args.out or data_root()/'generated-profiles')/'profile-build.json';report.parent.mkdir(parents=True,exist_ok=True)
 report.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')

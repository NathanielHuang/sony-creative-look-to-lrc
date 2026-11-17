"""Generate the local linear base from the owner's installed Adobe camera profile.

Based on Sony Look Bridge's MIT-licensed acr_profiles.py and dcp.py.
Adobe camera matrices are read locally; they are not bundled in the generic package.
"""
from pathlib import Path
import os,struct,sys
from config import load_adapter
ADAPTER=load_adapter()
BASE=ADAPTER['base_name']
FILENAME=ADAPTER['adobe_profile_filename']
PROPHOTO=[.7976749,.1351917,.0313534,.2880402,.7118741,.0000857,0.,0.,.8252100]

def find_adobe_profile(explicit=None):
 if explicit:
  p=Path(explicit)
  if p.is_file():return p
  raise FileNotFoundError(p)
 roots=[Path('/Library/Application Support/Adobe/CameraRaw/CameraProfiles'),Path.home()/'Library/Application Support/Adobe/CameraRaw/CameraProfiles']
 if os.name=='nt':
  roots=[Path(os.environ.get('PROGRAMDATA','C:/ProgramData'))/'Adobe/CameraRaw/CameraProfiles',Path(os.environ.get('PROGRAMFILES','C:/Program Files'))/'Adobe']
 for root in roots:
  if root.exists():
   found=next(root.rglob(FILENAME),None)
   if found:return found
 raise FileNotFoundError('找不到当前机型的Adobe Standard配置文件。请安装LRC，或使用--adobe-profile指定该DCP路径。')

def read_fields(path):
 data=Path(path).read_bytes()
 if data[:4]!=b'IIRC':raise ValueError('Invalid DCP header')
 off=struct.unpack_from('<I',data,4)[0];n=struct.unpack_from('<H',data,off)[0];out={}
 for i in range(n):
  pos=off+2+i*12;tag,typ,cnt,value=struct.unpack_from('<HHII',data,pos)
  if tag not in (50721,50722,50778,50779):continue
  size={3:2,10:8}.get(typ)
  if size is None:raise ValueError('Unexpected Adobe matrix field type')
  loc=pos+8 if cnt*size<=4 else value
  if typ==3:values=list(struct.unpack_from('<'+str(cnt)+'H',data,loc))
  else:
   pair=struct.unpack_from('<'+str(cnt*2)+'i',data,loc)
   values=[pair[j]/pair[j+1] for j in range(0,len(pair),2)]
  out[tag]=values
 if set(out)!={50721,50722,50778,50779}:raise ValueError('Incomplete Adobe camera matrices')
 return out

def build_base(adobe_profile):
 from metadata import Tiff
 raw=bytearray(Path(adobe_profile).read_bytes());raw[2:4]=b'\x2a\x00'
 t=Tiff(bytes(raw));tags=t.ifd(t.unpack('I',4)[0])
 if tags.get(50708,('',0))[0]!=ADAPTER['dcp_model']:raise ValueError('Adobe DCP camera model mismatch')
 a=read_fields(adobe_profile)
 entries=[(50708,2,ADAPTER['dcp_model']),(50936,2,BASE),(50721,10,a[50721]),(50722,10,a[50722]),
  (50778,3,a[50778]),(50779,3,a[50779]),(50964,10,PROPHOTO),(50965,10,PROPHOTO),
  (50940,11,[0.,0.,1.,1.]),(50941,4,[0]),(51110,4,[1]),(50942,2,'Sony Look Bridge (not an Adobe profile)')]
 items=[]
 for tag,typ,value in entries:
  if typ==2:raw=value.encode('latin1')+b'\0';cnt=len(raw)
  elif typ==10:
   cnt=len(value);raw=b''.join(struct.pack('<ii',int(round(x*10000)),10000) for x in value)
  else:
   cnt=len(value);raw=struct.pack('<'+str(cnt)+{3:'H',4:'I',11:'f'}[typ],*value)
  items.append((tag,typ,cnt,raw))
 items.sort();start=8+2+12*len(items)+4;head=bytearray();blob=bytearray()
 for tag,typ,cnt,raw in items:
  if len(raw)<=4:head+=struct.pack('<HHI',tag,typ,cnt)+raw+bytes(4-len(raw))
  else:
   if (start+len(blob))%2:blob+=b'\0'
   head+=struct.pack('<HHII',tag,typ,cnt,start+len(blob));blob+=raw
 return b'IIRC'+struct.pack('<I',8)+struct.pack('<H',len(items))+head+b'\0'*4+blob

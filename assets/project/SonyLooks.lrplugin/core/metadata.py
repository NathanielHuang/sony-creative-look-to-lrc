"""Read-only Sony metadata reader, configured by a sample-validated adapter."""
from pathlib import Path
import struct

import importlib.util
from config import load_adapter,load_recipes,ROOT

class Tiff:
 def __init__(self, data):
  self.data=data
  if data[:2] not in (b'II',b'MM'): raise ValueError('Missing TIFF byte order')
  self.order='<' if data[:2]==b'II' else '>'
  if self.unpack('H',2)[0]!=42: raise ValueError('Unsupported TIFF header')
 def span(self, off, n):
  if off<0 or n<0 or off+n>len(self.data): raise ValueError('TIFF field outside file')
  return self.data[off:off+n]
 def unpack(self, fmt, off):
  return struct.unpack(self.order+fmt,self.span(off,struct.calcsize(self.order+fmt)))
 def ifd(self, off):
  count=self.unpack('H',off)[0]
  if count>4096: raise ValueError('Unreasonable IFD size')
  self.span(off+2,count*12)
  result={}
  formats={1:'B',2:'c',3:'H',4:'I',5:'II',6:'b',7:'B',8:'h',9:'i',10:'ii',11:'f',12:'d',13:'I'}
  for i in range(count):
   pos=off+2+12*i
   tag,typ,n=self.unpack('HHI',pos)
   if typ not in formats: continue
   fmt=formats[typ]; size=struct.calcsize(self.order+fmt)*n
   loc=pos+8 if size<=4 else self.unpack('I',pos+8)[0]
   raw=self.span(loc,size)
   if typ==2: val=raw.rstrip(b'\0').decode('utf-8',errors='replace')
   elif typ==7: val=raw
   else:
    val=struct.unpack(self.order+fmt*n,raw)
    if len(val)==1: val=val[0]
   result[tag]=(val,loc)
  return result

def tiff_bytes(path):
 with open(path,'rb') as f:
  magic=f.read(2)
  if magic!=b'\xff\xd8':
   f.seek(0); return f.read()
  while True:
   mark=f.read(2)
   if len(mark)!=2 or mark[0]!=255: raise ValueError('Invalid JPEG marker')
   if mark[1] in (0xda,0xd9): break
   raw=f.read(2)
   if len(raw)!=2: break
   size=int.from_bytes(raw,'big')-2
   if size<0: raise ValueError('Invalid JPEG segment')
   data=f.read(size)
   if mark[1]==0xe1 and data.startswith(b'Exif\0\0'): return data[6:]
 raise ValueError('JPEG has no EXIF')

def camera_header(path):
 t=Tiff(tiff_bytes(path));root=t.ifd(t.unpack('I',4)[0])
 return {'model':root.get(0x110,('',0))[0], 'make':root.get(0x10f,('',0))[0],
         'software':root.get(0x131,('',0))[0]}

def read_metadata(path,adapter=None,reader_path=None):
 adapter=adapter or load_adapter()
 if adapter['reader']=='custom':
  reader_path=Path(reader_path or ROOT/'reader.py')
  spec=importlib.util.spec_from_file_location('sony_custom_reader',reader_path)
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  return mod.read_metadata(path,adapter)
 if adapter['reader']!='sony_makernote':raise ValueError('Unknown metadata reader')
 t=Tiff(tiff_bytes(path)); root=t.ifd(t.unpack('I',4)[0])
 result={'file':str(Path(path).resolve()),'model':root.get(0x110,('',0))[0],
         'software':root.get(0x131,('',0))[0]}
 if result['model']!=adapter['model']:return result
 exif=t.ifd(root[0x8769][0]); off=exif[0x927c][1]
 prefix=adapter.get('maker_note_prefix','SONY').encode('ascii')
 note=t.ifd(off+adapter.get('maker_note_skip',12) if t.span(off,len(prefix))==prefix else off)
 result.update(style=note.get(adapter['style_tag'],(None,0))[0],date=exif.get(0x9003,('',0))[0])
 result.update({key:note.get(tag,(None,0))[0] for key,tag in adapter['fields'].items()})
 return result

def identify(meta,adapter=None,recipes=None):
 adapter=adapter or load_adapter();recipes=recipes if recipes is not None else load_recipes()
 if meta.get('model')!=adapter['model']:return None
 values=[meta.get(k) for k in adapter['fields']]
 if meta.get('style') is None or any(v is None for v in values):return None
 hits=[key for key,r in recipes.items() if meta['style']==r['style'] and values==r['values']]
 if len(hits)>1:raise ValueError('Ambiguous recipe fingerprints: '+', '.join(hits))
 return hits[0] if hits else None

"""Selective XMP merge with conflict detection, exact backups, and atomic writes."""
from pathlib import Path
from xml.dom import minidom as M
import hashlib, os, tempfile

CRS='http://ns.adobe.com/camera-raw-settings/1.0/'
RDF='http://www.w3.org/1999/02/22-rdf-syntax-ns#'
OWN='https://local.invalid/sony-creative-looks-looks/1.0/'
XMLNS='http://www.w3.org/2000/xmlns/'

def parse(data):
 if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper(): raise ValueError('XML DTD/entities are unsupported')
 return M.parseString(data)

def description(doc):
 rdf=doc.getElementsByTagNameNS(RDF,'RDF')
 if len(rdf)!=1: raise ValueError('Expected one RDF document')
 nodes=[n for n in rdf[0].childNodes if n.nodeType==n.ELEMENT_NODE and n.namespaceURI==RDF and n.localName=='Description']
 if len(nodes)!=1: raise ValueError('Ambiguous RDF subjects; inspect manually')
 return nodes[0]

def attribute(node,name): return node.getAttributeNS(CRS,name)

def profile_settings(path):
 doc=parse(Path(path).read_bytes()); d=description(doc)
 name=d.getElementsByTagNameNS(CRS,'Name')[0].getElementsByTagNameNS(RDF,'li')[0].firstChild.data
 params={a.localName:a.value for a in d.attributes.values()
         if a.namespaceURI==CRS and (a.localName in ('Version','ProcessVersion','CameraProfile','RGBTable') or a.localName.startswith('Table_'))}
 params['ConvertToGrayscale']='False'
 look={'Name':name,'UUID':attribute(d,'UUID'),'Amount':'1','SupportsAmount':'false',
       'SupportsMonochrome':'false','SupportsOutputReferred':'false'}
 return look,params

def merge(original,profile,replace_look=False):
 look,params=profile_settings(profile)
 if original is None:
  original=b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about=""/></rdf:RDF></x:xmpmeta>'
 doc=parse(original); d=description(doc)
 old=d.getElementsByTagNameNS(CRS,'Look')
 existing=[n for n in old if n.parentNode is d]
 if len(existing)>1: raise ValueError('Multiple existing looks')
 if existing:
  desc=existing[0].getElementsByTagNameNS(RDF,'Description')
  # Same UUID alone is insufficient: an earlier SDK attempt may have lost its RGBTable.
  if desc and attribute(desc[0],'UUID')==look['UUID']:
   p=existing[0].getElementsByTagNameNS(CRS,'Parameters')
   if p:
    pd=p[0].getElementsByTagNameNS(RDF,'Description')
    if pd and all(attribute(pd[0],k)==v for k,v in params.items() if k=='RGBTable' or k.startswith('Table_')) and attribute(d,'CameraProfile')==params['CameraProfile']:
     return original,'unchanged'
 developed=any(a.namespaceURI==CRS and a.localName not in ('RawFileName','Version','ProcessVersion','HasSettings','HasCrop') for a in d.attributes.values())
 developed=developed or bool(d.getElementsByTagNameNS(CRS,'Look'))
 developed=developed or any(n.namespaceURI==CRS for n in d.childNodes if n.nodeType==n.ELEMENT_NODE)
 if developed and not replace_look: raise ValueError('Existing develop settings: use catalog plugin or explicitly --replace-look')
 d.setAttributeNS(XMLNS,'xmlns:crs',CRS)
 d.setAttributeNS(XMLNS,'xmlns:rdf',RDF)
 for name in ('CameraProfile','CameraProfileDigest'):
  if d.hasAttributeNS(CRS,name): d.removeAttributeNS(CRS,name)
  for n in list(d.childNodes):
   if n.nodeType==n.ELEMENT_NODE and n.namespaceURI==CRS and n.localName==name: d.removeChild(n)
 for n in existing: d.removeChild(n)
 d.setAttributeNS(CRS,'crs:CameraProfile',params['CameraProfile'])
 d.setAttributeNS(CRS,'crs:HasSettings','True')
 if not developed:
  for k,v in {'HasSettings':'True','Version':'19.0','ProcessVersion':'15.4','WhiteBalance':'As Shot'}.items():
   if not d.hasAttributeNS(CRS,k): d.setAttributeNS(CRS,'crs:'+k,v)
 node=doc.createElementNS(CRS,'crs:Look'); d.appendChild(node)
 ld=doc.createElementNS(RDF,'rdf:Description'); node.appendChild(ld)
 for k,v in look.items(): ld.setAttributeNS(CRS,'crs:'+k,v)
 p=doc.createElementNS(CRS,'crs:Parameters'); ld.appendChild(p)
 pd=doc.createElementNS(RDF,'rdf:Description');p.appendChild(pd)
 for k,v in params.items(): pd.setAttributeNS(CRS,'crs:'+k,v)
 return doc.toxml(encoding='utf-8'),'updated'

def sha(data): return hashlib.sha256(data).hexdigest()

def write_atomic(path,data,expected,backup_dir):
 path=Path(path)
 if path.is_symlink(): raise ValueError('Refusing symlink sidecar')
 lock=path.with_name(path.name+'.sony-creative-looks-lock')
 fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 tmp=None
 try:
  os.close(fd)
  current=path.read_bytes() if path.exists() else None
  if current!=expected: raise ValueError('Sidecar changed since planning')
  backup=None
  if current is not None:
   backup_dir=Path(backup_dir);backup_dir.mkdir(parents=True,exist_ok=True)
   backup=backup_dir/(path.name+'.'+sha(str(path.resolve()).encode())[:10]+'.'+sha(current)+'.bak')
   if backup.exists():
    if backup.read_bytes()!=current: raise ValueError('Backup collision')
   else:
    with backup.open('xb') as f: f.write(current);f.flush();os.fsync(f.fileno())
  handle,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
  with os.fdopen(handle,'wb') as f: f.write(data);f.flush();os.fsync(f.fileno())
  if (path.read_bytes() if path.exists() else None)!=expected: raise ValueError('Concurrent sidecar change')
  if expected is None:
   os.link(tmp,path);os.unlink(tmp)
  else: os.replace(tmp,path)
  tmp=None
  return str(backup) if backup else None
 finally:
  if tmp: os.unlink(tmp)
  lock.unlink()

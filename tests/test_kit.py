from pathlib import Path
import importlib.util,json,os,shutil,struct,subprocess,sys,tempfile,unittest
KIT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(KIT/'scripts'))
from common import read,dump,validate_samples,validate_profiles
from assemble import assemble
from new_adapter import create
from probe import probe
from metadata import identify,read_metadata
from xmp_merge import merge,parse,description,CRS,write_atomic
REF=KIT/'adapters/sony-ilce-9m3'

# Synthetic TIFF fixtures exercise model routing and metadata logic, not camera color accuracy.
def sample(path,a,recipe):
 root=8;exif=8+2+3*12+4;note=exif+2+2*12+4
 note_ifd=note+12;blob_start=note_ifd+2+(len(a['fields'])+1)*12+4
 data=bytearray(blob_start);data[:8]=b'II*\0'+struct.pack('<I',8)
 def ifd(off,rows):
  struct.pack_into('<H',data,off,len(rows))
  for i,(tag,typ,n,raw) in enumerate(rows):
   pos=off+2+i*12;struct.pack_into('<HHI',data,pos,tag,typ,n)
   if len(raw)<=4:data[pos+8:pos+12]=raw.ljust(4,b'\0')
   else:
    loc=len(data);data.extend(raw);struct.pack_into('<I',data,pos+8,loc)
 def string(tag,s):
  b=s.encode()+b'\0';return tag,2,len(b),b
 ifd(root,[string(0x110,a['model']),string(0x131,'synthetic test'),(0x8769,4,1,struct.pack('<I',exif))])
 date=string(0x9003,'2026:11:17 12:00:00');ifd(exif,[date,(0x927c,7,12,bytes(12))])
 # Point MakerNote to a preallocated IFD rather than its temporary unused blob.
 struct.pack_into('<I',data,exif+2+12+8,note);data[note:note+12]=b'SONY DSC \0\0\0'
 rows=[string(a['style_tag'],recipe['style'])]
 rows.extend((tag,9,1,struct.pack('<i',value)) for tag,value in zip(a['fields'].values(),recipe['values']))
 ifd(note_ifd,rows)
 if path.suffix.lower()=='.jpg':
  payload=b'Exif\0\0'+data;path.write_bytes(b'\xff\xd8\xff\xe1'+struct.pack('>H',len(payload)+2)+payload+b'\xff\xd9')
 else:path.write_bytes(data)

def manifest_for(folder,adapter):
 a=read(adapter/'adapter.json');recipes=read(adapter/'recipes.json');pairs=[]
 for key,r in recipes.items():
  raw=folder/(key+'.ARW');jpg=folder/(key+'.JPG');sample(raw,a,r);sample(jpg,a,r)
  pairs.append({'recipe':key,'arw':str(raw),'jpeg':str(jpg),'lighting':'synthetic'})
 p=folder/'samples.json';dump(p,{'pairs':pairs});return p

def synthetic_adobe(path,model):
 vals=[1,0,0,0,1,0,0,0,1];matrix=struct.pack('<18i',*[v for x in vals for v in (x,1)])
 model=model.encode()+b'\0'
 entries=[(50708,2,len(model),model),(50721,10,9,matrix),(50722,10,9,matrix),(50778,3,1,struct.pack('<H',17)),(50779,3,1,struct.pack('<H',21))]
 head=b'';blob=b'';offset=8+2+12*len(entries)+4
 for tag,typ,n,data in entries:
  head+=struct.pack('<HHI',tag,typ,n)
  if len(data)<=4:head+=data.ljust(4,b'\0')
  else:head+=struct.pack('<I',offset+len(blob));blob+=data
 path.write_bytes(b'IIRC'+struct.pack('<IH',8,len(entries))+head+b'\0'*4+blob)

class Kit(unittest.TestCase):
 def test_arbitrary_model_candidate_and_probe(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);adapter=create('ILCE-FIXTURE-X',root/'adapter');a=read(adapter/'adapter.json')
   self.assertEqual(a['validation']['status'],'candidate');a['base_mode']='linear_from_adobe';dump(adapter/'adapter.json',a)
   dump(adapter/'recipes.json',read(REF/'recipes.json'));manifest=manifest_for(root,adapter)
   report=validate_samples(adapter,manifest);self.assertEqual(report['pair_count'],4)
   self.assertEqual(report['render_result'],'pending_lrc_validation')
   p=probe([root/'light_seeker.ARW'])['files'][0];self.assertEqual(p['model'],'ILCE-FIXTURE-X');self.assertIsNone(p['adapter'])
 def test_bad_pair_and_missing_fields_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);m=manifest_for(root,REF);a=read(REF/'adapter.json');recipes=read(REF/'recipes.json')
   sample(root/'light_seeker.JPG',a,recipes['lucid_cyan'])
   with self.assertRaises(ValueError):validate_samples(REF,m)
   meta={'model':a['model'],'style':'BW'};self.assertIsNone(identify(meta,a,recipes))
 def test_collision_and_wrong_camera_rejected(self):
  a=read(REF/'adapter.json');r=read(REF/'recipes.json');m={'model':a['model'],'style':r['light_seeker']['style'],**dict(zip(a['fields'],r['light_seeker']['values']))}
  self.assertEqual(identify(m,a,r),'light_seeker');m['model']='another camera';self.assertIsNone(identify(m,a,r))
  m['model']=a['model'];r['duplicate']=r['light_seeker']
  with self.assertRaises(ValueError):identify(m,a,r)
 def test_assembly_and_draft_guard(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);m=manifest_for(root,REF);project=assemble(REF,root/'complete',m)
   self.assertEqual(len(read(project/'SonyLooks.lrplugin/profiles.json')),4)
   self.assertEqual(read(project/'验收记录.json')['lrc_render'],'pending')
   draft=assemble(REF,root/'draft',draft=True)
   r=subprocess.run([sys.executable,'-B',str(draft/'install.py'),'--dry-run'],capture_output=True,text=True)
   self.assertNotEqual(r.returncode,0);self.assertIn('草稿',r.stderr)
   with self.assertRaises(ValueError):assemble(REF,root/'missing-samples')
 def test_xmp_preservation_and_conflicts(self):
  original=b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><r:RDF xmlns:r="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><r:Description r:about="" xmlns:c="http://ns.adobe.com/camera-raw-settings/1.0/" xmlns:xmp="http://ns.adobe.com/xap/1.0/" c:Exposure2012="1.25" c:CropLeft=".03" xmp:Rating="4"><c:MaskGroupBasedCorrections><r:Seq><r:li>opaque-mask</r:li></r:Seq></c:MaskGroupBasedCorrections></r:Description></r:RDF></x:xmpmeta>'
  p=REF/'profiles/追光者.xmp'
  with self.assertRaises(ValueError):merge(original,p)
  result,_=merge(original,p,True);d=description(parse(result))
  self.assertEqual(d.getAttributeNS(CRS,'Exposure2012'),'1.25');self.assertEqual(d.getAttributeNS(CRS,'CropLeft'),'.03')
  self.assertEqual(d.getAttributeNS('http://ns.adobe.com/xap/1.0/','Rating'),'4');self.assertIn(b'opaque-mask',result)
  self.assertEqual(merge(result,p),(result,'unchanged'))
  with tempfile.TemporaryDirectory() as td:
   target=Path(td)/'photo.xmp';target.write_bytes(original)
   with self.assertRaises(ValueError):write_atomic(target,result,b'wrong',Path(td)/'backup')
   backup=write_atomic(target,result,original,Path(td)/'backup');self.assertEqual(Path(backup).read_bytes(),original)
 def test_installation_sandbox_and_model_check(self):
  if sys.platform!='darwin' and os.name!='nt':self.skipTest('Installer targets macOS/Windows')
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);m=manifest_for(root,REF);project=assemble(REF,root/'project',m)
   adobe=root/'adobe.dcp';synthetic_adobe(adobe,'Sony ILCE-9M3')
   script='''import sys\nsys.path.insert(0,sys.argv[1])\nfrom pathlib import Path\nfrom install import install,locations\nhome=Path(sys.argv[2]);adobe=sys.argv[3]\ninstall(home=home,adobe=adobe)\nextra=locations(home)['profiles']/'keep.txt';extra.write_text('user content')\ninstall(home=home,adobe=adobe)\nassert extra.read_text()=='user content'\n'''
   r=subprocess.run([sys.executable,'-B','-c',script,str(project),str(root/'home'),str(adobe)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
   synthetic_adobe(adobe,'Sony OTHER');r=subprocess.run([sys.executable,'-B',str(project/'install.py'),'--dry-run','--adobe-profile',str(adobe)],capture_output=True,text=True)
   self.assertNotEqual(r.returncode,0);self.assertIn('model mismatch',r.stderr)
 @unittest.skipUnless(os.environ.get('SONY_LOOK_SAMPLES'),'Optional original sample manifest')
 def test_real_camera_samples(self):
  manifest=Path(os.environ['SONY_LOOK_SAMPLES']);report=validate_samples(REF,manifest);self.assertEqual(report['metadata_result'],'passed')
  with tempfile.TemporaryDirectory() as td:
   project=assemble(REF,Path(td)/'project',manifest)
   script="import sys,json;sys.path.insert(0,sys.argv[1]);from bridge import match;print(json.dumps(match(json.loads(sys.argv[2])),ensure_ascii=False))"
   paths=[str((manifest.parent/r['arw']).resolve()) for r in read(manifest)['pairs']]
   r=subprocess.run([sys.executable,'-B','-S','-c',script,str(project/'SonyLooks.lrplugin/core'),json.dumps(paths)],capture_output=True,text=True)
   self.assertEqual(r.returncode,0,r.stderr);rows=json.loads(r.stdout)
   self.assertEqual(len(rows),4);self.assertTrue(all(x['status']=='matched' and x['match_mode']=='capture_table' for x in rows),rows)

if __name__=='__main__':unittest.main()

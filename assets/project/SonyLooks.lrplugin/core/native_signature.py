from pathlib import Path
import hashlib,json,sys
VENDOR=Path(__file__).resolve().parents[1]/'vendor/sony-look-bridge/sonylook'
sys.path.insert(0,str(VENDOR))
import arw_looks as AL
MAIN_TAGS=("0x7841","0x7847","0x7848","0x780b","0x787e","0x787f","0x7880","0x7881","0x74c5")
def capture_signature(path,style):
 looks=AL.look_ifds(str(path)); main=AL.main_tags(str(path))
 chosen={t:main[t] for t in MAIN_TAGS}
 chosen["SonyModelID"]=AL.sony_model_id(str(path)); chosen["settings"]=AL.look_settings(str(path))
 for t in ("0x7770","0x780f","0x7805","0x7806","0x74c6"):
  if t in main:chosen[t]=main[t]
 return hashlib.sha256(json.dumps({'version':1,'look':looks[style], 'main':chosen,'grid':64},sort_keys=True).encode()).hexdigest()[:12]

from pathlib import Path
import os
from config import load_adapter
def data_root():
 name='SonyCreativeLooks-'+load_adapter()['id']
 if os.name=='nt':return Path(os.environ['APPDATA'])/name
 return Path.home()/'Library/Application Support'/name

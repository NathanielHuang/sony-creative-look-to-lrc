#!/usr/bin/env python3
"""Register constructed RGBTable profiles in a working adapter; never edit source profiles."""
from pathlib import Path
import argparse,shutil
from common import adapter_files,read,dump,profile_settings,parse,description,attribute,sha

def register(adapter,source):
 folder,a,recipes=adapter_files(adapter);source=Path(source).resolve()
 existing=read(folder/'profiles.json') if (folder/'profiles.json').exists() else []
 if existing:raise ValueError('Use a new adapter version with an empty profiles.json; keep the prior version for rollback')
 build=read(source/'profile-build.json') if (source/'profile-build.json').exists() else []
 captures={Path(r['profile']).resolve():r['signature'] for r in build}
 rows=[];seen=set();pending=[]
 for p in sorted(source.glob('*.xmp')):
  look,params=profile_settings(p)
  matches=[k for k,v in recipes.items() if v['name']==look['Name']]
  if len(matches)!=1:raise ValueError('Unknown or ambiguous visible name: '+look['Name'])
  key=matches[0]
  if key in seen:raise ValueError('Multiple profiles for recipe: '+key)
  if attribute(description(parse(p.read_bytes())),'CameraModelRestriction')!=a['dcp_model'] or params['CameraProfile']!=a['base_name']:raise ValueError('Profile camera/base mismatch')
  if not params.get('Table_'+params.get('RGBTable','')):raise ValueError('Missing RGB table')
  target=folder/'profiles'/(look['Name']+'.xmp')
  if target.exists():raise ValueError('Target already exists: '+str(target))
  rows.append({'recipe':key,'name':look['Name'],'file':'profiles/'+target.name,'base':a['base_name'],'signature':captures.get(p.resolve(),''),'uuid':look['UUID'],'source_sha256':sha(p)})
  seen.add(key);pending.append((p,target))
 if seen!=set(recipes):raise ValueError('Missing profiles for some recipes')
 for p,target in pending:target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 dump(folder/'profiles.json',rows)
 return len(rows)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--adapter',required=True);ap.add_argument('--profiles',required=True);a=ap.parse_args();print('Registered profiles:',register(a.adapter,a.profiles))

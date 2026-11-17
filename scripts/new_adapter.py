#!/usr/bin/env python3
"""Create an unverified candidate for any Sony model, outside the shipped kit."""
from pathlib import Path
import argparse,re
from common import dump

def create(model,out):
 out=Path(out)
 if out.exists():raise ValueError('Output already exists')
 key='sony-'+re.sub('[^a-z0-9]+','-',model.lower()).strip('-')
 if key=='sony-':raise ValueError('Empty model')
 a={'schema_version':1,'id':key,'model':model,'dcp_model':'Sony '+model,'adobe_profile_filename':'Sony '+model+' Adobe Standard.dcp','base_name':'Sony '+model+' Creative Base','base_mode':'provided','reader':'sony_makernote','maker_note_prefix':'SONY','maker_note_skip':12,'style_tag':45088,'fields':{'contrast':8196,'highlights':8243,'shadows':8242,'fade':8244,'saturation':8197,'sharpness':8198,'sharpness_range':8245,'clarity':8246},'signature_engine':None,'renderer':None,'validation':{'status':'candidate','note':'字段位置和DCP名称是候选值，须用该机型原片及本机配置验证。选择匹配的色彩生成流程后再设置base_mode和renderer。'}}
 out.mkdir(parents=True);dump(out/'adapter.json',a);dump(out/'recipes.json',{});dump(out/'profiles.json',[])
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--model',required=True);ap.add_argument('--out',required=True);args=ap.parse_args();print(create(args.model,args.out))

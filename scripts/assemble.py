#!/usr/bin/env python3
"""Create a self-contained, model-configured project. Does not install it."""
from pathlib import Path
import argparse,json,shutil,tempfile
from common import KIT,adapter_files,validate_samples,validate_profiles,dump,contained,sha
from bridge import lua

def assemble(adapter,out,samples=None,draft=False):
 folder,a,recipes=adapter_files(adapter);out=Path(out).resolve()
 if out.exists():raise ValueError('Output already exists; use a new version directory')
 if out==KIT or KIT in out.parents:raise ValueError('Generate the personal project outside the kit')
 verification=None if draft else validate_samples(folder,samples) if samples else None
 if not draft and verification is None:raise ValueError('--samples is required for a deployable project')
 profiles=[] if draft else validate_profiles(folder)
 out.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='.sony-assembly-',dir=out.parent) as td:
  stage=Path(td)/'project';shutil.copytree(KIT/'assets/project',stage,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.DS_Store'))
  plugin=stage/'SonyLooks.lrplugin';dump(plugin/'adapter.json',a);dump(plugin/'recipes.json',recipes)
  for optional in ['reader.py','base.dcp']:
   if (folder/optional).is_file():shutil.copy2(folder/optional,plugin/optional)
  (plugin/'profiles').mkdir()
  packed=[]
  for row in profiles:
   row=dict(row);src=contained(folder,row['file']);row['file']='profiles/'+row['name']+'.xmp'
   shutil.copy2(src,plugin/row['file']);packed.append(row)
  dump(plugin/'profiles.json',packed)
  info=plugin/'Info.lua';s=info.read_text(encoding='utf-8')
  s=s.replace("local.sonylooks.creatorlooks",'local.sonylooks.'+a['id'])
  # Names are JSON-quoted strings, also valid Lua string literals for camera labels.
  s=s.replace("LrPluginName='SonyLooks创作者外观'","LrPluginName="+lua('索尼创作者外观 '+a['model']))
  s=s.replace('minor=3','minor=4');info.write_text(s,encoding='utf-8')
  readme='''# 索尼创作者外观

退出LRC，运行“安装或修复.command”（macOS）或“install-windows.cmd”（Windows），完成后重新打开LRC。在“文件→增效工具管理器”中确认插件已启用。

导入照片时，“修改照片设置”选择“无”。新照片仍使用Adobe默认配置时，插件会识别配方并应用外观。

已有照片先选中，再使用“图库→增效工具额外信息→应用到选中照片”。想保留原编辑版本，选择“创建外观虚拟副本”。应用外观只替换外观和基础配置。

重装或更新后，再运行一次安装程序。旧安装保存在运行数据目录的“安装备份”中，路径可在插件的“查看运行状态”中找到。

新增外观或升级固件后，把新样本交给Agent检查。需要调整其他光照下的效果时，也提供对应照片。Agent在LRC中完成测试后，会填写安装包内的验收记录。
'''
  (stage/'使用说明.md').write_text(readme,encoding='utf-8')
  if draft:(stage/'DRAFT.json').write_text('{"purpose":"profile construction only"}\n')
  else:
   dump(stage/'样本验证.json',verification)
   dump(stage/'验收记录.json',{'metadata':'passed','lrc_import':'pending','lrc_render':'pending','existing_edits':'pending','cross_lighting':'pending'})
  shutil.copy2(KIT/'LICENSE',stage/'LICENSE');shutil.copy2(KIT/'THIRD_PARTY.md',stage/'THIRD_PARTY.md')
  hashes={str(p.relative_to(stage)):sha(p) for p in stage.rglob('*') if p.is_file()}
  dump(stage/'文件校验.json',hashes);stage.rename(out)
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--adapter',required=True);ap.add_argument('--out',required=True);ap.add_argument('--samples');ap.add_argument('--draft',action='store_true');a=ap.parse_args();print(assemble(a.adapter,a.out,a.samples,a.draft))

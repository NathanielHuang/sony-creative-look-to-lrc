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
  readme='''# 在Lightroom Classic里用索尼创意外观

## 安装

退出Lightroom Classic（LRC）。macOS运行“安装或修复.command”，Windows运行“install-windows.cmd”。装好后重新打开LRC，在“文件 → 增效工具管理器”里确认插件已启用。

## 导入和修图

平时照常导入ARW，“修改照片设置”选“无”。新照片还在用Adobe默认配置时，插件会按拍摄设置匹配外观。第一次用时，打开“修改照片”看一下外观名，再导出一张和机内JPEG比较。已装好的外观也可以在配置文件浏览器里按名称选。

给旧照片匹配外观时，先选中照片，再点“图库 → 增效工具额外信息 → 应用到选中照片”。想保留当前版本，就用同一菜单里的“创建外观虚拟副本”。

## 更新和恢复

重装LRC后再运行一次安装器。添加外观、更换相机或升级固件时，把新样片交给助手检查。

要恢复旧安装，先退出LRC。插件菜单里的“查看运行状态”会显示运行记录路径。上一级目录里有“安装备份”和安装记录。按记录把旧插件和配置放回原处，再打开LRC。
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

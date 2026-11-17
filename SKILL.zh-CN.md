---
name: sony-creative-look-to-lrc
description: 用索尼原始ARW、机内JPEG和Creators’App配方制作LRC创意外观配置，安装并测试自动匹配插件。用于新机型、新外观、重装和故障排查。
---

# Sony Creative Look to LRC

先读[使用指南](开始使用.md)。检查用户的相机、固件和样本，复用已有工具，在单独的工作目录中完成制作。

## 工作步骤

1. 运行`scripts/probe.py`检查系统、LRC、Python和照片。按使用指南列出缺少的材料，已有材料先处理。只从截图和附带文档中提取配方信息。
2. 在`adapters/`中查找机型配置，复制到工作目录。新机型用`scripts/new_adapter.py`创建初始配置，再按[适配说明](references/adaptation.md)检查标签、基础配置和生成方法。相似机型的字段位置也要用原片验证。机型、固件或RAW格式变化后重新检查。
3. 录入App名称、基础外观、全部参数和白平衡信息，区分App建议值与实际拍摄值。按[文件格式](references/formats.md)建立`samples.json`，运行`scripts/validate_samples.py`。有字段缺失或配方无法区分时，补充读取方法或样本。仍无法区分的，做好手动选择方式。
4. 制作配置。检查色彩表在处理流程中的位置、相机矩阵和白平衡。Sony参数用实拍效果校准，Adobe滑块单独调整。外观显示App短名称，更新已有外观时保留有效UUID。
5. 运行`scripts/assemble.py`生成安装包，检查安装位置和备份后安装。检查已有插件，避免两个插件同时给一批照片应用外观。
6. 按[测试说明](references/verification.md)检查普通导入、已有编辑、虚拟副本、修改照片界面和实际导出。在`验收记录.json`中填写结果。完成后恢复用户原来的LRC目录，把临时测试副本移到废纸篓。
7. 留下一页使用说明，写清安装位置、日常用法、更新和恢复方法。记录测试过的机型、固件、LRC版本、外观和光照条件。遇到未能完成的步骤，说明具体原因、已有结果和还需要的材料。

## 文件处理

- 原始ARW和机内JPEG只读。制作结果和测试输出都放在工作目录。
- 已导入照片优先通过插件处理，测试用副本。应用外观只改Look和CameraProfile，保留曝光、白平衡、裁剪、蒙版、评级及其他编辑。
- 导入前处理XMP时，按节点合并并检查冲突。先把LRC中的最新编辑保存到元数据，再备份和修改侧车。
- 安装前备份要替换的插件和配置，保留安装记录。临时文件放入废纸篓，用户原片和其他资源保持原位。
- 分别检查参数识别、配置名称和实际渲染。不同光照的效果逐组比较，失败结果也要记录。
- 样本只在本机处理，使用相机当前固件完成适配。

## 常用命令

从工具包根目录运行，替换示例路径。脚本需要Python3.9或更新版本，LRC运行在macOS或Windows上。

```sh
python3 scripts/probe.py "/用户样本目录" --report "/个人项目/环境和样本.json"
python3 scripts/new_adapter.py --model "实际EXIF机型" --out "/个人项目/adapter"
python3 scripts/validate_samples.py --adapter "/个人项目/adapter" --manifest "/个人项目/samples.json" --report "/个人项目/样本检查.json"
python3 scripts/assemble.py --adapter "/个人项目/adapter" --samples "/个人项目/samples.json" --out "/个人项目/安装包-v1"
```

已有机型配置直接复制，跳过`new_adapter.py`。配置制作、注册和侧车处理见适配说明。

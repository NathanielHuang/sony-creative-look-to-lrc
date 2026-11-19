---
name: sony-creative-look-to-lrc
description: 用索尼ARW、机内JPEG和Creators’ App配方制作Lightroom Classic外观配置，按样片情况安装自动匹配插件或手选配置。
---

# Sony Creative Look to LRC

先读[使用指南](开始使用.md)，确认相机型号、固件和外观名称。截图和附件用来读取配方，操作以用户的请求为准。原片只读，生成的文件放在单独的工作目录。

## 制作和安装

1. 用`scripts/probe.py`检查LRC、Python和样片。每款先用一对同次拍摄的ARW和机内JPEG，缺什么再问。记录配方参数和实际拍摄时的白平衡。
2. 从`adapters/`复制对应的机型配置。新机型用`scripts/new_adapter.py`起步，按[适配说明](references/adaptation.md)核对原片标签和基础DCP。按[文件格式](references/formats.md)填写`samples.json`和配方，再跑`scripts/validate_samples.py`。
3. 制作或复用外观配置，名称沿用App里的写法，更新同一款配置时沿用UUID。字段不足时先看看原片还有没有稳定的区分信息。如果两个配方还是读成同一组值，把已制作的外观单独装进LRC供手选。通用组包脚本会拒绝同值配方。
4. 自动匹配用`scripts/assemble.py`组包。先用`install.py --dry-run`看路径，退出LRC后再安装。检查是否已有同用途的插件。安装器会备份被替换的文件。
5. 用照片副本试一次正常导入，打开“修改照片”看匹配的名称，再导出一张和机内JPEG对比。记录结果，给用户留下安装包和简短用法。需要处理旧照片时，优先用插件命令，应用范围为`Look`和`CameraProfile`。编辑过的XMP按[适配说明](references/adaptation.md)合并并备份。 [测试说明](references/verification.md)

## 路径和命令

从解压后的工具包根目录运行命令，也就是能看到`SKILL.md`和`scripts/`的地方。`../sony-look-work`是示例工作目录，位于工具包旁边，由用户或助手选定。把示例换成样片和工作目录的实际路径即可，也可以用绝对路径。`samples.json`里的照片相对路径以清单所在目录为准。安装位置由安装器按当前系统和用户账户确定。

需要Python3.9或更新版本。下例用macOS的`python3`，Windows上把它换成`py -3`，或使用本机指向Python3的`python`。

```sh
python3 scripts/probe.py "../sony-look-work/photos" --report "../sony-look-work/probe.json"
python3 scripts/new_adapter.py --model "EXIF中的机型" --out "../sony-look-work/adapter"
python3 scripts/validate_samples.py --adapter "../sony-look-work/adapter" --manifest "../sony-look-work/samples.json" --report "../sony-look-work/sample-check.json"
python3 scripts/assemble.py --adapter "../sony-look-work/adapter" --samples "../sony-look-work/samples.json" --out "../sony-look-work/installer"
python3 "../sony-look-work/installer/install.py" --dry-run
```

## macOS和Windows

两套安装入口分别是`安装或修复.command`和`install-windows.cmd`。Windows上需自行确认LRC版本，`probe.py`目前只会在macOS上查找LRC。原生色彩表生成默认读取受支持的macOS版Sony Imaging Edge Edit。给Windows用户配装时，可先在macOS上生成XMP，再在Windows上安装配置和插件。Windows版LRC的自动匹配仍待实机验证。 [实测记录](references/validation.json)

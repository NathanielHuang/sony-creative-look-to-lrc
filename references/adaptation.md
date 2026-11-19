# 适配新机型

## 先读样片

用`scripts/probe.py`看ARW和JPEG里有哪些字段，再对照Creators’ App的截图。可以用本机的ExifTool看完整的元数据。新机型的MakerNote标签、偏移和Adobe配置文件名都要用原片核实。现有读取器读不到所需字段时，可以为该机型编写只读的`reader.py`。

插件用基础外观和配方参数一起匹配。以α9 III为例，澄青和都市漫游的基础外观都是FL3，机内写入的对比度、高光、饱和度等参数不同，普通导入时两款都能自动匹配。 [实测记录](validation.json)

如果连配方参数也相同，再查原片里有没有外观ID之类的区分字段。找不到时，可把做好的XMP和配套DCP分别装进Adobe Camera Raw的用户`Settings`和`CameraProfiles`目录，在LRC里按名称选。

## 制作外观

已有对应机型和配方时，复制`adapters/`中的配置，用现在的样片确认一次。新配方可以用原生色彩表生成。原生表读不到时，也可以用该机型的基础配置，对照ARW和机内JPEG调色，并把配套`base.dcp`放进适配目录，设`base_mode`为`provided`。

生成原生表需要NumPy和Sony Look Bridge支持的Sony Imaging Edge Edit版本。版本和路径见随附代码的`docs/photo.md`、`docs/pipeline.md`和`sonylook/edit_binary.py`。日常匹配只用Python标准库。 [随附代码](../assets/project/SonyLooks.lrplugin/vendor/sony-look-bridge/)

1. 在`recipes.json`填好配方，`profiles.json`先留空数组。确认该机型可走原生表流程后，设`renderer`为`sony_sr2`、`signature_engine`为`sony_sr2_v1`、`base_mode`为`linear_from_adobe`。
2. 生成制作配置用的草稿。

   ```sh
   python3 scripts/assemble.py --adapter "/项目/adapter" --draft --out "/项目/draft"
   ```

3. 把`SONYLOOK_CACHE_DIR`设到工作目录。每款先选一张ARW，用默认的64网格生成色彩表，再把XMP注册到适配目录。

   ```sh
   python3 "/项目/draft/SonyLooks.lrplugin/core/build_profiles.py" "/样片/外观一.ARW" "/样片/外观二.ARW" --out "/项目/generated"
   python3 scripts/register_profiles.py --adapter "/项目/adapter" --profiles "/项目/generated"
   ```

`profile-build.json`记录生成的配置和色彩表摘要。`register_profiles.py`按App名称保存XMP，保留生成的UUID。更新时新建一个适配目录，旧版留作回退。

## 组包和安装

```sh
python3 scripts/validate_samples.py --adapter "/项目/adapter" --manifest "/项目/samples.json" --report "/项目/sample-check.json"
python3 scripts/assemble.py --adapter "/项目/adapter" --samples "/项目/samples.json" --out "/项目/installer"
python3 "/项目/installer/install.py" --dry-run
```

退出LRC后再运行安装器。重开LRC，在“增效工具管理器”里确认插件已启用。插件每5秒看一次图库有没有新照片，只自动处理仍在用Adobe默认配置的ARW。已有照片可以用“图库 → 增效工具额外信息”中的“应用到选中照片”或“创建外观虚拟副本”。

## 导入前写入XMP

```sh
python3 "/项目/installer/SonyLooks.lrplugin/core/prepare_sidecars.py" "/照片文件夹"
python3 "/项目/installer/SonyLooks.lrplugin/core/prepare_sidecars.py" "/照片文件夹" --write
```

第一条只列出计划，第二条写入XMP。照片已有显影设置时，先把LRC里的编辑保存到元数据并退出LRC。确认要换外观后再加`--replace-look`，脚本会备份已有XMP并合并外观和基础配置。要逐张生成原生色彩表时，可在装好对应依赖后加`--native`。

# 适配说明

## 检查原片

运行probe后，对照配方截图核对字段。新建机型配置里的标签、偏移和Adobe文件名都要检查。可以用本机ExifTool读取ARW和JPEG的完整元数据，再作比较。现有读取器不适用时，编写该机型的只读`reader.py`。

用同场景、不同外观的照片寻找稳定的配方标识或参数组合。曝光和白平衡等拍摄设置单独处理。作者名称、唯一ID、槽位等信息，以该机型和固件的实拍结果为准。

## 选择制作方法

已有相同机型和配方的配置时，复制到个人项目，用本次样本检查后再使用。

如果能读取原生色彩表，且工具包所附的Sony Look Bridge版本能处理该机型，按下文生成RGBTable。检查配套DCP、白平衡处理和实际颜色。

如果能读取参数，但无法生成原生表，就用该机型的基础配置，对照ARW和机内JPEG拟合颜色或逐项校准。将`base_mode`设为`provided`，把配套DCP放入工作目录。输出的XMP和DCP需要能被插件正确读取和应用。

自动识别所需的信息不足时，先制作可手动选择的外观。补齐可靠的区分字段后，再启用自动匹配。安装包生成器要求配方指纹唯一，手动模式需要Agent另行配置。

锐化、降噪、DRO、清晰度和局部细节单独比较。黑白外观还要检查灰阶分离和对比度。

## 生成原生色彩表

代码位于`assets/project/SonyLooks.lrplugin/vendor/sony-look-bridge`，附有上游许可证和提交号。先读其中的`docs/photo.md`、`docs/pipeline.md`及`sonylook/edit_binary.py`，确认Sony Edit版本和本机路径。

日常匹配只用Python标准库。生成原生表还需要NumPy和该版本支持的Sony Imaging Edge Edit，缺少的依赖由Agent在隔离环境中准备。

1. 在`recipes.json`中录入配方，`profiles.json`先填空数组。验证读取和色彩处理方法后，设置`renderer=sony_sr2`、`signature_engine=sony_sr2_v1`、`base_mode=linear_from_adobe`。
2. 生成用于制作配置的草稿。草稿不能直接安装。

```sh
python3 scripts/assemble.py --adapter "/个人项目/adapter" --draft --out "/个人项目/制作草稿"
```

3. 将`SONYLOOK_CACHE_DIR`设在个人项目内，用准备好的Python环境运行。每款先选一张代表照片，正式输出使用默认64网格。

```sh
python3 "/个人项目/制作草稿/SonyLooks.lrplugin/core/build_profiles.py" "/样本/外观一.ARW" "/样本/外观二.ARW" --out "/个人项目/生成配置"
python3 scripts/register_profiles.py --adapter "/个人项目/adapter" --profiles "/个人项目/生成配置"
```

`profile-build.json`保存配方和色彩表摘要。注册脚本保留生成器的UUID，按App名称保存XMP。注册到空目录，旧版本留作备份。

4. 检查成对样本，再生成安装包并查看安装计划。

```sh
python3 scripts/validate_samples.py --adapter "/个人项目/adapter" --manifest "/个人项目/samples.json" --report "/个人项目/样本检查.json"
python3 scripts/assemble.py --adapter "/个人项目/adapter" --samples "/个人项目/samples.json" --out "/个人项目/安装包-v1"
python3 "/个人项目/安装包-v1/install.py" --dry-run
```

5. 退出LRC，运行安装器，再打开LRC。检查是否有其他插件重复处理同一批照片。插件每5秒检查一次新照片，稍作等待后应用外观。切换目录时，已有照片保留原样，需要处理的从菜单中手动应用。

## 处理已有照片

LRC里已有的照片，用“应用到选中照片”或“创建外观虚拟副本”处理。新导入照片只有在仍使用Adobe默认配置时才自动匹配。安装后重启LRC，让它加载完整色彩表。

需要在导入前写入侧车时，运行：

```sh
python3 "/个人项目/安装包-v1/SonyLooks.lrplugin/core/prepare_sidecars.py" "/照片文件夹"
python3 "/个人项目/安装包-v1/SonyLooks.lrplugin/core/prepare_sidecars.py" "/照片文件夹" --write
```

默认只检查，添加`--write`才写入。已有显影设置会提示冲突。`--replace-look`会备份侧车，再替换外观和基础配置。操作前先保存LRC中的最新元数据并退出LRC。合并后检查曝光、裁剪、蒙版、评级及XML命名空间。

需要逐张生成原生表时添加`--native`，并准备好该机型所需的依赖。

## 更新配置

- 新外观：补充配方和样本，制作配置，生成新版本安装包。
- 新固件：重新检查元数据和色彩表，运行样本测试和LRC测试，保留旧版记录。
- 新相机：创建该机型配置，使用对应的基础DCP，重新检查颜色。
- 重装LRC：运行个人安装包，检查Python路径和插件启用状态。

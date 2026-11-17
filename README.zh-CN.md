# Sony Creative Look to LRC

[English](README.md)

把Sony Creators’App中的创意外观接入LRC，用户提供相机信息、配方截图和实拍照片，由AI Agent制作配置、安装插件并检查效果。

用户观看[使用指南](开始使用.md)，Agent按[SKILL.md](SKILL.md)操作。

|目录|内容|
|---|---|
|`scripts/`|检查环境和样本、制作机型配置、生成安装包|
|`assets/project/`|插件、安装器和色彩处理工具的模板|
|`adapters/`|机型配置，附A9III实测示例|
|`references/`|技术说明和测试方法|
|`tests/`|测试代码|

可以直接把整个文件夹交给Agent，使用支持Skill的工具时，将它作为`sony-creative-look-to-lrc`安装到该工具的Skill目录。

版本：0.4.0。[查看测试记录](references/validation.json)。

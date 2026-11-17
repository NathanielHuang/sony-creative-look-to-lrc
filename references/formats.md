# 文件格式

每个机型目录有三个配置文件：`adapter.json`、`recipes.json`和`profiles.json`。XMP外观放在`profiles/`中。需要自定义读取方法时添加`reader.py`，使用现成基础配置时添加`base.dcp`。

## adapter.json

运行`scripts/new_adapter.py`创建初始配置，再根据原片和本机资源填写。

|字段|用途|
|---|---|
|id|由小写字母、数字和短横线组成，用于插件安装目录，更新时保持不变|
|model|原片EXIF中的准确型号|
|dcp_model|DCP的UniqueCameraModel和XMP的机型限制值|
|adobe_profile_filename|本机Adobe基础配置的文件名|
|base_name|XMP引用的基础DCP名称|
|base_mode|`linear_from_adobe`或`provided`|
|reader|`sony_makernote`或`custom`|
|maker_note_prefix、maker_note_skip|MakerNote头和偏移|
|style_tag|基础外观字段的标签地址，填JSON整数|
|fields|参与匹配的参数名及标签地址，顺序与配方values一致|
|signature_engine|验证后可填`sony_sr2_v1`，未使用时填null|
|renderer|验证后可填`sony_sr2`，其他方法填null并另行实现|
|validation|样本来源、固件、测试环境、结果和光照条件|

`linear_from_adobe`生成与本工具原生表流程配套的线性基础配置。`provided`使用机型目录中的`base.dcp`，安装时检查机型和名称。基础DCP要与色彩生成方法配套。

选择`custom`时，`reader.py`需实现`read_metadata(path, adapter)`，返回`model`、`style`、`date`和fields中的各项参数。函数只读文件，缺少的字段填null。作者标识、白平衡微调等字段经过ARW/JPEG验证后，也可加入匹配条件。

## recipes.json

每款外观使用一个固定ID，填写名称、基础外观和参数。`english`为可选字段。

```json
{
  "my_look": {
    "name": "App中的外观名称",
    "style": "实际基础外观",
    "values": [0, 0, 0, 0, 0, 4, 3, 0]
  }
}
```

默认8项参数依次为对比度、高光、阴影、褪色、饱和度、锐度、锐度范围、清晰度。修改fields后，values也要按相同顺序调整。

名称用于显示，自动匹配使用原片中读到的字段。如果两款配方的这些值完全相同，需要补充区分条件。

## samples.json

```json
{
  "pairs": [
    {
      "recipe": "my_look",
      "arw": "samples/my-look/DSC00001.ARW",
      "jpeg": "samples/my-look/DSC00001.JPG",
      "lighting": "日光"
    }
  ]
}
```

照片路径相对于samples.json，也可以填写绝对路径。每款至少一对同次拍摄的ARW/JPEG。

验证脚本检查机型、配方参数、可读取的拍摄时间和文件SHA-256，并确认每款都有样本。两张照片是否来自同一次拍摄，由用户确认。结果保存在个人项目中。

## profiles.json

每款包含`recipe`、`name`、`file`、`base`、`signature`和`uuid`。文件路径相对于机型目录，用`register_profiles.py`从制作结果生成。

插件目前使用含RGBTable的XMP外观。CameraModelRestriction、基础配置、名称和UUID要相互对应，色彩表也要完整嵌入。使用其他Adobe配置格式时，需要同时调整读取、安装和SDK应用代码，并在LRC中测试。

`signature`保存拍摄色彩表的摘要，可留空。它用来区分同一配方下不同的色彩表。遇到新光照时，可先按完整配方参数应用固定配置，运行记录会标为`recipe_profile`。

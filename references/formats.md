# 适配文件格式

每个机型目录有`adapter.json`、`recipes.json`和`profiles.json`。XMP放进`profiles/`。自定义读取器用`reader.py`，自带的基础DCP用`base.dcp`。

## adapter.json

`scripts/new_adapter.py`会生成一份初始配置。以相机原片和本机DCP为准核对字段。

| 字段 | 填什么 |
| --- | --- |
| `id` | 安装用的固定ID，由小写字母、数字和短横线组成 |
| `model` | 原片EXIF中的机型 |
| `dcp_model` | DCP的`UniqueCameraModel`，也用作XMP的机型限制 |
| `adobe_profile_filename` | 本机Adobe Standard DCP的文件名 |
| `base_name` | XMP引用的基础DCP名称 |
| `base_mode` | `linear_from_adobe`从本机Adobe配置生成线性DCP，`provided`使用附带的`base.dcp` |
| `reader` | `sony_makernote`用内置读取器，`custom`用`reader.py` |
| `maker_note_prefix`、`maker_note_skip` | MakerNote前缀及跳过的字节数 |
| `style_tag` | 基础外观的标签编号，填整数 |
| `fields` | 用于识别配方的参数名和标签编号，顺序要与`values`一致 |
| `signature_engine`、`renderer` | 原生表流程分别用`sony_sr2_v1`和`sony_sr2`，其他方案可填`null` |
| `validation` | 记录样片、固件、LRC版本和测试结果 |

自定义`reader.py`实现`read_metadata(path, adapter)`，返回`model`、`style`、`date`及`fields`列出的参数。缺失字段返回`None`。

## recipes.json

为每款外观取一个固定ID。`name`用App里的名称。`english`可选。

```json
{
  "my_look": {
    "name": "App里的外观名",
    "style": "相机记录的基础外观",
    "values": [0, 0, 0, 0, 0, 4, 3, 0]
  }
}
```

默认8项依次是对比度、高光、阴影、褪色、饱和度、锐度、锐度范围、清晰度。调整`fields`时，对应调整`values`。自动匹配用`style`和`values`，显示名称可以单独改。

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

每款至少一对同次拍摄的ARW和机内JPEG。照片路径可以相对于`samples.json`，也可以用绝对路径。`lighting`可省略。脚本检查机型、配方、可用的拍摄时间和样片覆盖，并计算文件的SHA-256。

## profiles.json

每条记录包含`recipe`、`name`、`file`、`base`、`signature`和`uuid`。`file`是相对于机型目录的XMP路径。运行`register_profiles.py`生成这些记录。XMP须嵌入RGBTable，机型限制、基础DCP名称和UUID要对得上。

`signature`是拍摄色彩表的摘要，可以留空。摘要匹配时，记录为`capture_table`。只有配方匹配时，插件会应用这款外观已有的配置，记录为`recipe_profile`。

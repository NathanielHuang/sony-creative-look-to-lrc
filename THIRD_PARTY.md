# 第三方代码和色彩资产

原生色彩表的读取和生成使用[Sony Look Bridge](https://github.com/751K/sony-look-bridge)，版本为`71a7422bff2a9ce921b747ea126d58445af8b242`。基础DCP生成器参考了其中的`acr_profiles.py`和`dcp.py`。上游MIT许可证随代码保存在`vendor/sony-look-bridge/LICENSE`。

本项目原创代码采用[MIT许可证](LICENSE)。α9 III示例中的外观名称和配方来自Sony Creators’ App，XMP中的色彩表由实拍样本生成。

安装时，基础DCP由本机的Adobe配置生成，也可以使用用户提供的配套DCP。

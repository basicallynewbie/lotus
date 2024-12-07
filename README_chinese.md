# 注意

莲花v3更改了json的格式。但是你可以用https://github.com/basicallynewbie/bamboo来新建或将v2转换陈v3。

# 如何使用

下载源代码。

## 依赖:

python >=3.11.0

## 使用方法:

在unix中，请使用python3指令，路径符号为/。

有3个[action]可供选择：test, hardlink, softlink。--recursive应需使用。
    
因为权限问题，你不能在windows中使用softlink。

    python lotus.py [action] "source path" "reference json" --recursive

## 示范:

原文件夹是这样的:

    test
    └── windows
        ├── example.json
        └── tv
            ├── [somegroup] exampletv 1 [1920x1080p][AAC][AVC][JA][CHS].txt
            ├── [somegroup] exampletv 2 [1920x1080p][AAC][AVC][JA][CHS].txt
            ├── ...
            ├── [somegroup] exampletv 9 [1920x1080p][AAC][AVC][JA][CHS].txt
            └── 100+
                └── [somegroup] exampletv 110 [1920x1080p][AAC][AVC][JA][CHS].txt
                └── [somegroup] exampletv 111 [1920x1080p][AAC][AVC][JA][CHS].txt
                └── [somegroup] exampletv 112 [1920x1080p][AAC][AVC][JA][CHS].txt

进入你下载源代码的文件夹。并将lotus.py复制到test\windows里。

    cd somewhere\lotus\test\windows

当然你需要对原路径有可读权限，对目标路径有写入权限。

运行以下命令:

    python lotus.py hardlink "tv" "example.json" -r

结果如下:

    test\windows\exampletv
    └── season02
        ├── exampletv.S02.E001.Japanese.Chinese.WebRip.1080P.AAC.H264.8Bit.somegroup.txt
        ├── exampletv.S02.E002.Japanese.Chinese.WebRip.1080P.AAC.H264.8Bit.somegroup.txt
        ├── ...
        └── exampletv.S02.E112.Japanese.Chinese.WebRip.1080P.AAC.H264.8Bit.somegroup.txt

阅读aboutjson.txt以获取更多信息。
jsonfile必须为UTF-8编码。如果你的文字编辑器不支持UTF-8编码，则使用createJson.py创建jsonfile。

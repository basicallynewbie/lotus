# 什么是莲花

莲花是个用于批量重命名创建硬/软链接的命令行软件。

## 什么是硬链接或软链接

unix:

    https://www.redhat.com/en/blog/linking-linux-explained

windows:

硬链接：

    https://learn.microsoft.com/zh-cn/windows/win32/fileio/hard-links-and-junctions

软链接：

    https://learn.microsoft.com/zh-cn/windows/win32/fileio/symbolic-links

## 注意

莲花v3更改了json的格式。但是你可以用https://github.com/basicallynewbie/bamboo 来新建或将v2转换成v3。

## 依赖:

python >= 3.11.0

## 如何使用

下载源代码或执行软件。

## 使用方法

在unix中，请使用python3指令，路径符号为/。

有4个[action]可供选择：test, hardlink, softlink, rename。--recursive应需使用。 --encode应需使用。 

因为权限问题，你不能在windows中以正常用户使用softlink。但是能以管理员身份使用softlink。

    python lotus.py [action] "source path" "reference json" --recursive --encode whatever

## 其它

示范存在于test文件夹。

阅读aboutjson_chinese.txt以获取更多信息。

jsonfile现在不需要为UTF-8编码，但还是推荐。你可以选择任何编码，只要不混合使用。

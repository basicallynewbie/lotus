# how to use

Download the  source code.

## require:

python >=3.11.0

## usage:

    ./hardlink.py 'source path' 'reference json' recursive=Ture/False

## example:

origin folder look like this:

    /mnt/examplefolder/
    └── exampletv
        └── season01
            ├── example.json
            ├── [somegroup] exampletv 01 [1920x1080p][AAC][AVC][JA][CHS].mp4
            ├── [somegroup] exampletv 02 [1920x1080p][AAC][AVC][JA][CHS].mp4
            ├── [somegroup] exampletv 03 [1920x1080p][AAC][AVC][JA][CHS].mp4
            └── pv
                └── [somegroup] exampletv PV [1920x1080p][AAC][AVC][JA][CHS].mp4

go to the directory where you downloaded the source code.

    cd /somewhere/rename-hardlink

of course, you need read access to source path and write access to link path.

run cmd below:

    ./hardlink.py '/mnt/examplefolder/exampletv/' '/mnt/examplefolder/exampletv/season01/example.json' True

the output below:

    /mnt/TV/exampletv/
    └── season01
        ├── example.json
        ├── exampletv.S01.E01.Japanese.Chinese.1080P.AAC.H264.somegroup.mp4
        ├── exampletv.S01.E02.Japanese.Chinese.1080P.AAC.H264.somegroup.mp4
        ├── exampletv.S01.E03.Japanese.Chinese.1080P.AAC.H264.somegroup.mp4
        └── exampletv.S01.Japanese.Chinese.1080P.AAC.H264.somegroup.PV.mp4

## notice

json file must use UTF-8 encode.
read aboutjson.txt to get more information.

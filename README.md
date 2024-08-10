# how to use

Download the source code.

## require:

python >=3.11.0

## usage:

    replace python with python3 in unix, the symbol of path is /. 

    there are 3 [action] for choose: test, hardlink, softlink. --recursive is option.
    
    you can't use softlink in windows due to PermissionError.

    python lotus.py [action] "source path" "reference json" --recursive

## example:

origin folder look like this:

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

go to the directory where you downloaded the source code. and copy lotus.py into test\windows.

    cd somewhere\lotus\test\windows

of course, you need read access to source path and write access to target path.

run cmd below:

    python lotus.py hardlink "tv" "example.json" -r

the output below:

    test\windows\exampletv
    └── season02
        ├── exampletv.S02.E001.Japanese.Chinese.WebRip.1080P.AAC.H264.8Bit.somegroup.txt
        ├── exampletv.S02.E002.Japanese.Chinese.WebRip.1080P.AAC.H264.8Bit.somegroup.txt
        ├── ...
        └── exampletv.S02.E112.Japanese.Chinese.WebRip.1080P.AAC.H264.8Bit.somegroup.txt

read aboutjson.txt to get more information.

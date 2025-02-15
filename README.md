# What is lotus

lotus is a cli tool for creating hardlink or softlink file/s with another name in another path in batch.

## What is hardlink or softlink

unix:

    https://www.redhat.com/en/blog/linking-linux-explained

windows:

hardlink:

    https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions

softlink:

    https://learn.microsoft.com/en-us/windows/win32/fileio/symbolic-links


## notice

lotus v3 changed json format. but you can use https://github.com/basicallynewbie/bamboo to convert v2 to v3 or generate.


## requirement

python >= 3.11.0

## how to use

Download the source code or compiled program.

## usage

replace python with python3 in unix, the symbol of path is /. 

there are 4 [action] for choose: test, hardlink, softlink, rename. --recursive is option. --encode is option.

you can't use softlink in windows due to PermissionError.

    python lotus.py [action] "source path" "reference json" --recursive --encode whatever

## more

see test folder for examples.

read aboutjson.txt to get more information.

jsonfile doesn't need to use UTF-8 encode now, but it's still recommended. you can choose whatever encode you want as long as you don't mix use.

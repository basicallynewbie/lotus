# How to use:


  For example:

origin file in the folder look like this:

    /mnt/unsorted/somevideo
      ├subfolder
        └somefile.txt
      ├[somegroup]somevideo 01 [1920x1080][AAC][AVC][JA][CHS].mp4
      ├[somegroup]somevideo 02 [1920x1080][AAC][AVC][JA][CHS].mp4
      ├example.json

after run this cmd:

    python3 /pwd/nonerecursivelink.py '/mnt/unsorted/somevideo' '/mnt/unsorted/somevideo/example.json'

new folder will be created, and hard link will be created too.

    /mnt/download/somevideo
      ├somevideo.S01.E01.Japanese.Chinese.1080P.AAC.H264.somegroup.mp4
      ├somevideo.S01.E02.Japanese.Chinese.1080P.AAC.H264.somegroup.mp4
      ├example.json

use recursivelink.py if you want to hard link somefile.txt too.

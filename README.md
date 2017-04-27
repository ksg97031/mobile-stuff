# mobile-stuff
Handy scripts for mobile security test

## adb-sync

Sync images from a running android process for remote debugging. Files can be found under `rom/deviceid/`.

No requirement for this script except enabling USB debug and of course have adb command installed on your computer.

Example:

```
$ adb shell ps | grep com.example.app
1234
$ python3 adb-sync.py 1234
138 files to sync
pulling /system/lib/libandroid.so
pulling /system/lib/libqservice.so
...
$ find rom
rom
rom/808c29e0a3b005a8
rom/808c29e0a3b005a8/data
...
```

## ios-checksec

Dead simple checksec utility for ios executables. Requires [lief framework](https://github.com/lief-project/LIEF). You need to  `pip install lief` before running the script.

Usage: `python3 ios-checksec.py path/to/executable`


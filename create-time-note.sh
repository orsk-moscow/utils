#!/usr/bin/env sh

arg0=$1 # directory where text note should be placed

if [ "$arg0" == '' ];
    then arg0="/Users/$(whoami)/Yandex.Disk.localized/-text-notes/"
fi

dt1=$(date '+%Y-%m-%d-%H:%M')
filename=$arg0$dt1.txt
dt2=$(date '+%Y-%m-%d %H:%M')
echo $dt2 > $filename && open $filename

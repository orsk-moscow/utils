#!/usr/bin/env sh
test "$1" == '' && (echo WARN please set keyword for process should be killed; exit 1)
pids_this_proc=$(ps aux | grep $0 | awk '{print $2}')
pids_other="$(ps aux | grep $1 | grep -v "$pids_this_proc" | awk '{print $2}')"; kill $pids_other

#!/usr/bin/env sh

ARG0=$1 # prefix: `work` or `mine` or etc
ARG1=$2 # key for repository, for example: `zvq-etl`

FSYNC_PATH="Yandex.Disk.localized/computer-sciense" #path for all-in-one folder file syncing (usually via Yandex Disk). Helps do not lost any usefull additional files like debug jsons, test data etc

if [ "$ARG0" == 'cotwo' ];
    then ARG3='cotwo-project'
elif [ "$ARG0" == 'mine' ];
    then ARG3='orsk-moscow'
else 
    echo "please set correct ARG0: one of 'mine' or 'cotwo'"; 
    exit 1;
fi

test "$ARG1" == '' && echo "please set an ARG1: key for repository, like 'FinancialRepo'" && exit 1

REPO='git@github.com:'$ARG3'/'$ARG1'.git'
SRC='/Users/'$(whoami)'/'$FSYNC_PATH'/'$ARG0'-'$ARG1
DEST1='/Users/'$(whoami)'/'$ARG0'-'$ARG1'.lnk'
DEST2='/Users/'$(whoami)'/Desktop/'$ARG0'-'$ARG1'.lnk'

echo "cloning repo into path: '$SRC'\n" && git clone $REPO $SRC
echo "linking cloned repo into path: '$DEST1'\n" && ln -s $SRC $DEST1
echo "linking cloned repo into path: '$DEST2'\n" && ln -s $SRC $DEST2

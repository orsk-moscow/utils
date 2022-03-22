#!/usr/bin/env sh

arg0=$1 # prefix: `work` or `mine` or etc
arg1=$2 # key for repository, for example: `zvq-etl`

if [ "$arg0" == 'cotwo' ];
    then arg3='cotwo-project'
elif [ "$arg0" == 'mine' ];
    then arg3='orsk-moscow'
else 
    echo "please set correct arg0: one of 'mine' or 'cotwo'"; 
    exit 1;
fi

test "$arg1" == '' && echo "please set an arg1: key for repository, like 'FinancialRepo'" && exit 1

repo='git@github.com:'$arg3'/'$arg1'.git' 
src='/Users/'$(whoami)'/'$arg0'-'$arg1
dest='/Users/'$(whoami)'/'$arg0'-'$arg1'.lnk'

git clone $repo $src

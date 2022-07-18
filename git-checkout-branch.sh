#!/usr/bin/env bash

ARG0=$1

if [ "$ARG0" == 'rc' ];
    then BRANCH='rc'
elif [ "$ARG0" == 'master' ];
    then BRANCH='master'
elif [ "$ARG0" == 'ma' ];
    then BRANCH='master'
else 
    echo "please set a branch to checkout, one of: rc | master | ma"; 
    echo "example: ./file.sh ma or ./file.sh rc"; 
    exit 1;
fi

cd ~
DIRS=$(ls|grep work)
echo $DIRS
for dir in $(ls|grep work)
do
cd $dir
git checkout $BRANCH
git pull
cd ~
done

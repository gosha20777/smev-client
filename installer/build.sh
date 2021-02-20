#!/bin/bash
echo "1. Check environment"
version=$(python -V 2>&1 | grep -Po '(?<=Python )(.+)')
if [[ -z "$version" ]]
then
    echo "[ERR] No python!"
    exit -1
fi
parsedVersion=$(echo "${version//./}")
if [[ "$parsedVersion" -gt "370" ]]
then 
    echo "[OK] Python $version"
else
    echo "[ERR] Invalid python $version < 3.7.0"
    exit -1
fi

version=$(go version 2>&1 | grep -Po '(?<=go version go)(.+)')
if [[ -z "$version" ]]
then
    echo "[ERR] No python!"
    exit -1
fi
parsedVersion=$(echo "${version//./}")
parsedVersion=$(echo "${parsedVersion// linux\/amd64/}")
if [[ "$parsedVersion" -gt "1130" ]]
then 
    echo "[OK] Go $version"
else
    echo "[ERR] Invalid go $version < 1.13.0"
    exit -1
fi

echo "2. Build app"
if [ -d "./bin/" ]
then
    rm -rf ./bin
fi
mkdir ./bin
echo "2.1 xml-signer"


#python -m venv -v
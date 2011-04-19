#!/bin/bash

machine=$(uname -m)
os=$(uname -s)

DARWIN_BINARY="omadarwin.linux32"

install_prefix="/usr/local"
if [ $# -eq 1 ]
then
    if [ $1 = "--help" -o $1 = "-h" -o $1 = "-help" ]
    then
        echo "usage: ./install.sh [install_prefix]"
        exit 0
    fi
    install_prefix=$(dirname $1)/$(basename $1)
fi
mkdir -p $install_prefix/omaesprit/bin

if [ $os = "Linux" ]
then
    if [ $machine = "x86_64" ]
    then
        DARWIN_BINARY="omadarwin.linux64"
    fi
elif [ $os = "Darwin" ]
then
    if [ $machine = "x86_64" ]
    then
        DARWIN_BINARY="omadarwin.mac64"
    else
        DARWIN_BINARY="omadarwin.mac32"
    fi
else
    echo "Operating system not supported!"
fi

echo "installing darwin binary..."
cp bin/omadarwin bin/$DARWIN_BINARY bin/omaesprit $install_prefix/omaesprit/bin/
echo "installing oma..."
cp OMA.drw $install_prefix/omaesprit/
echo "installing libraries..."
cp -rf lib $install_prefix/omaesprit/
cp -rf darwinlib $install_prefix/omaesprit/
echo "installation complete."
echo "Make sure $install_prefix/omaesprit/bin is in your PATH."

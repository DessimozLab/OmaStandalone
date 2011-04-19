#!/bin/bash

machine=$(uname -m)
os=$(uname -s)

DARWIN_BINARY="omadarwin.linux32"
install_prefix="/usr/local"
current_dir=`dirname $0`

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
cp $current_dir/bin/omadarwin $current_dir/bin/$DARWIN_BINARY $current_dir/bin/omaesprit $install_prefix/omaesprit/bin/
echo "installing oma..."
cp $current_dir/OMA.drw $current_dir/README.omaesprit $current_dir/parameters.drw $install_prefix/omaesprit/
echo "installing libraries..."
cp -rf $current_dir/lib $install_prefix/omaesprit/
cp -rf $current_dir/darwinlib $install_prefix/omaesprit/
echo "installation complete."
echo "Make sure $install_prefix/omaesprit/bin is in your PATH."

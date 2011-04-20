#!/bin/bash

machine=$(uname -m)
os=$(uname -s)

DARWIN_BINARY="omadarwin.linux32"
install_prefix="/usr/local"
current_dir=`dirname $0`
versionnr="[VERSIONNR]"

if [ $# -eq 1 ]
then
    if [ $1 = "--help" -o $1 = "-h" -o $1 = "-help" ]
    then
        echo "usage: ./install.sh [install_prefix]"
        exit 0
    fi
    install_prefix=$(dirname $1)/$(basename $1)
fi
omadir=$install_prefix/oma$versionnr
if ! mkdir -p $omadir/bin 2>/dev/null
then
    echo "Could not create $omadir . 
Please try again either with a different install prefix or with 'sudo ./install.sh [install_prefix]'."
    exit
fi

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

echo "Installing darwin binary..."

if ! cp $current_dir/bin/omadarwin $current_dir/bin/$DARWIN_BINARY $current_dir/bin/oma $omadir/bin/ 2>/dev/null
then
    echo "Could not write to $install_prefix. Please try again either with a different install prefix or with 'sudo ./install.sh [install_prefix]."
    exit
fi
echo "Installing oma..."
cp $current_dir/OMA.drw $current_dir/README.oma $current_dir/parameters.drw $omadir/
echo "Installing libraries..."
cp -rf $current_dir/lib $omadir/
cp -rf $current_dir/darwinlib $omadir/
echo "Installation complete."
echo "Make sure $omadir/bin is in your PATH."

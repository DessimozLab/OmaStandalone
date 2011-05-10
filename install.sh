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
omadir=$install_prefix/OMA/OMA.$versionnr
linkdir=$install_prefix/OMA/bin
if ! mkdir -p $omadir/bin 2>/dev/null
then
    echo "Could not create $omadir . 
Please try again either with a different install prefix or with 'sudo ./install.sh [install_prefix]'."
    exit
fi
mkdir -p $linkdir

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
echo "Creating symlinks to current version..."
if [ -s $linkdir/OMA ]
then
    rm $linkdir/OMA
fi
ln -s $omadir/bin/oma $linkdir/OMA.$versionnr
ln -s $omadir/bin/oma $linkdir/OMA
echo "Installation complete."
echo "Make sure $linkdir is in your PATH, e.g by adding the line"
echo "  export PATH=\$PATH:$linkdir"
echo "to your ~/.profile file (under bash)"

#!/bin/bash

machine=$(uname -m)
os=$(uname -s)

DARWIN_BINARY="omadarwin.linux32"
install_prefix="${1:-/usr/local}"
data_dir="${2:-DEFAULT}"
not_create_venv="$3"

current_dir=`dirname $0`
versionnr="[VERSIONNR]"
if [ "$data_dir" == "DEFAULT" ] ; then
    data_dir="$HOME/.cache/oma"
    data_dir_str="getenv('HOME').'/.cache/oma'"
else
    data_dir_str="'$data_dir'"
fi

if [ $# -ge 1 ]
then
    if [ $1 = "--help" -o $1 = "-h" -o $1 = "-help" ]
    then
        echo "usage: ./install.sh [install_prefix]"
        exit 0
    fi
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
        (>&2 echo "32-bit mac systems are not supported anymore")
        exit 1
    fi
else
    (>&2 echo "Operating system not supported!")
    exit 1
fi

echo "Installing darwin binary..."

if ! cp $current_dir/bin/omadarwin $current_dir/bin/$DARWIN_BINARY $current_dir/bin/oma current_dir/bin/oma-* $current_dir/bin/warthog $omadir/bin/ 2>/dev/null
then
    echo "Could not write to $install_prefix. Please try again either with a different install prefix or with 'sudo ./install.sh [install_prefix]."
    exit
fi
echo "Installing oma..."

cp $current_dir/OMA.drw $current_dir/README.oma $current_dir/parameters.drw $omadir/
echo "Installing libraries..."
cp -rf $current_dir/lib $omadir/
cp -rf $current_dir/darwinlib $omadir/
cp -rf $current_dir/hog_bottom_up $omadir/

if [ -z "$not_create_venv" ] ; then 
    echo "creating virtualenv for hog_bottom_up"
    if ! $current_dir/bin/create_warthog_venv.sh $omadir/.venv $omadir/hog_bottom_up ; then
        (>&2 echo "cannot create virtual environment for hog_bottom_up")
        exit 1
    fi
fi

echo "installing package data..."
mkdir -p $data_dir
[ -d $current_dir/data ] && cp -r $current_dir/data/ $data_dir
if [ "$USER" == "root" ] ; then
    chown -R $SUDO_USER $data_dir
fi
sed -i.se "s|datadirname := .*|datadirname := $data_dir_str:|" $omadir/darwinlib/darwinit && rm $omadir/darwinlib/darwinit.se

echo "Creating symlinks to current version..."
[ -L $linkdir/OMA ] && unlink $linkdir/OMA
[ -L $linkdir/oma ] && unlink $linkdir/oma
[ -L $linkdir/OMA.$versionnr ] && unlink $linkdir/OMA.$versionnr
for lnk in $linkdir/oma-* ; do 
    [ -L $lnk ] && unlink $lnk
done
ln -s $omadir/bin/oma $linkdir/OMA.$versionnr
ln -s $omadir/bin/oma $linkdir/OMA
ln -s $omadir/bin/oma $linkdir/oma 2>/dev/null  #osx is caseinsensitive
for util in $omadir/bin/oma-*; do 
    [ -x $util ] && ln -s $util $linksir/$(basename $util)
done

echo "Installation complete."
echo "Make sure $linkdir is in your PATH, e.g by adding the line"
echo "  export PATH=\$PATH:$linkdir"
echo "to your ~/.profile file (under bash)"

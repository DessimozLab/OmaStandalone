#!/bin/bash

venv_path="$1"
package="$2"

if ! python3 -m venv $venv_path ; then 
    if ! python -m virtualenv $venv_path ; then
        (>&2 echo "Neither python2 nor python3 seem to be available on this system.")
        exit 1
    fi
fi
source "$venv_path/bin/activate"
if ! pip install -r $package/requirements.txt ; then
    (>&2 echo "Cannot install python dependencies for hog-bottom-up inference algorithm")
    exit 1
fi
if ! pip install $package ; then 
    (>&2 echo "Cannot install hog-bottom-up python package")
    exit 1
fi
deactivate

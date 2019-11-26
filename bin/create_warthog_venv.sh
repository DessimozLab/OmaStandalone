#!/bin/bash

venv_path="$1"
requirements="$2"
add_args="$3"

if ! python3 -m venv $venv_path $add_args; then 
    if ! python -m virtualenv $venv_path $add_args; then
        (>&2 echo "Neither python2 nor python3 seem to be available on this system.")
        exit 1
    fi
fi
source "$venv_path/bin/activate"
if ! pip install -r $requirements ; then
    (>&2 echo "Cannot install python dependencies for hog-bottom-up inference algorithm")
    exit 1
fi
deactivate

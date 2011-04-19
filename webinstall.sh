#!/bin/bash

echo "downloading omaesprit..."
curl -s -o omaesprit.tgz http://localhost/omaesprit.tgz
tar xvzf omaesprit.tgz
rm omaesprit.tgz

install_prefix=`pwd`

echo "installation complete."
echo "Make sure $install_prefix/omaesprit/bin is in your PATH."

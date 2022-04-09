#!/bin/bash
# Simple script to create symbolic links for snowbudget programs.
#
#   Connor Shugg

# get path of the repository
fullpath=$(dirname $(dirname $(realpath $0)))

# get optional install path location
ipath=${fullpath}
if [ $# -ge 1 ]; then
    ipath=$1
fi

# make sure the installation directory exists
if [ ! -d ${ipath} ]; then
    echo "Error: couldn't find the install directory: ${ipath}"
    exit 1
fi

# now, create symbolic links
ln -s ${fullpath}/src/cli/main.py ${ipath}/sb


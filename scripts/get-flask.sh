#!/bin/bash
# Simple script to install Flask, a Python web server framework.

# look for pip or pip3
pip=$(which pip 2> /dev/null)
if [ -z "${pip}" ]; then
    pip=$(which pip3 2> /dev/null)
fi

echo -e "\033[33mInstalling Flask...\033[0m"
${pip} install --user -U Flask


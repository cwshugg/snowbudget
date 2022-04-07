#!/bin/bash
# Simple script to install Flask and a few dependencies.

# look for pip or pip3
pip=$(which pip3 2> /dev/null)

C_ACC="\033[36m"
C_NONE="\033[0m"

echo -e "${C_ACC}Installing setup tools...${C_NONE}"
${pip} install --user -U pip setuptools
echo -e "${C_ACC}Installing flask...${C_NONE}"
${pip} install --user -U Flask
echo -e "${C_ACC}Installing jwt...${C_NONE}"
${pip} install --user -U jwt


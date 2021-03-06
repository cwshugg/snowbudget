#!/bin/bash
# Simple script to install Flask and a few dependencies.

# look for pip or pip3
pip="python3 -m pip"

C_ACC="\033[36m"
C_NONE="\033[0m"

echo -e "${C_ACC}Installing setup tools...${C_NONE}"
${pip} install --user -U pip setuptools
echo -e "${C_ACC}Installing flask...${C_NONE}"
${pip} install --user -U Flask
echo -e "${C_ACC}Installing jwt...${C_NONE}"
${pip} uninstall --user -U JWT
${pip} uninstall --user -U PyJWT
${pip} install --user -U PyJWT
echo -e "${C_ACC}Installing openpyxl...${C_NONE}"
${pip} install --user -U openpyxl


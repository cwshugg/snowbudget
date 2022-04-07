#!/usr/bin/python3
# Super small main file that invokes 'app.run()' to run the server.
#
#   Connor Shugg

# Imports
import os
import sys

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
from server.app import app

# Globals
flask_addr = "0.0.0.0"
flask_port = 7669

# Main function
def main():
    app.run(flask_addr, port=flask_port)

# Runner code
if (__name__ == "__main__"):
    main()

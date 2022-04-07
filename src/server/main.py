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
from server.auth import auth_init
import server.config as config

# Main function
def main():
    # initialize any needed functionality then run the flask app
    auth_init()
    app.run(config.server_addr, port=config.server_port)

# Runner code
if (__name__ == "__main__"):
    main()

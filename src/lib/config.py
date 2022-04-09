# Module responsible for reading the configuration file.
#
#   Connor Shugg

# Imports
import json
import os
import sys

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Main configuration class.
class Config:
    # Takes in the file path.
    def __init__(self, fpath):
        self.fpath = fpath
        # set up basic config fields to hold default values
        self.name = None            # configuration name
        self.classes = []           # budget class list
        self.save_location = None   # path to save directory
    
        # -------------------- Main Parsing Functionality -------------------- #
        # open the file, slurp the entire content (should be small), then close
        fp = open(self.fpath)
        content = fp.read()
        fp.close()

        # attempt to convert to JSON and make sure the expected fields are
        # present in the JSON data
        jdata = json.loads(content)
        fields = [
            ["name", str],
            ["save_location", str]
        ]
        for f in fields:
            fname = f[0]
            ftype = f[1]
            assert fname in jdata and type(jdata[fname]) == ftype, \
                   "expected JSON field '%s' of type '%s'" % (fname, ftype)

        # extract the fields and save
        self.name = jdata["name"]
        self.save_location = jdata["save_location"]


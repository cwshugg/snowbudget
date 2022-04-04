# Responsible for interacting with files saved to disk.
#
#   Connor Shugg

# Imports
import os
import json

# Local imports
from bclass import BudgetClass

class Disk:
    # Takes in the main directory path to save the budget to.
    def __init__(self, spath):
        self.spath = spath
        # attempt to set up the save location
        assert not os.path.isfile(self.spath), \
               "the save location must be a path to a directory"
        if not os.path.exists(self.spath):
            os.mkdir(self.spath)

    # Wrapper for os.path.exists() that checks of a class's file exists.
    def check_class(self, bclass): 
        fpath = os.path.join(self.spath, bclass.to_file_name())
        return os.path.exists(fpath)
    
    # Used to write a budget class to disk.
    def write_class(self, bclass):
        fpath = os.path.join(self.spath, bclass.to_file_name())
        # open the file for writing
        fp = open(fpath, "w")
        fp.write(json.dumps(bclass.to_json(), indent=4))
        fp.close()
    
    # Attempts to load a file as JSON and parse it as a budget class.
    def load_class(self, fname):
        fpath = os.path.join(self.spath, fname)
        fp = open(fpath, "r")       # open file
        data = fp.read()            # slurp whole file in
        fp.close()                  # close file
        jdata = json.loads(data)    # convert to JSON
        # attempt to convert from JSON and return the object
        return BudgetClass.from_json(jdata)


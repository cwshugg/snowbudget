# Module responsible for reading the configuration file.
#
#   Connor Shugg

# Imports
import json
import os

# Local imports
from bclass import BudgetClass, BudgetClassType

# Globals
uncategorized_name = "Uncategorized"    # used as a default expense/income class

# Main configuration class.
class Config:
    # Takes in the file path.
    def __init__(self, fpath):
        self.fpath = fpath
        # set up config fields as None (initialized in 'parse()')
        self.name = None    # configuration name
        self.classes = []   # budget class list
        self.spath = None   # path to save directory
    
    # Attempts to parse the config file given in the constructor. Throws an
    # exception on failure.
    def parse(self):
        # ------------------------- Helper Functions ------------------------- #
        # define a quick helper function (used for checking for the presence of
        # expected JSON fields
        def parse_check_fields(jd, fs):
            for f in fs:
                fname = f[0]
                ftype = f[1]
                assert fname in jd and type(jd[fname]) == ftype, \
                       "expected JSON field '%s' of type '%s'" % (fname, ftype)
        
        # Used to parse a budget class from within the JSON data. Checks for
        # the presence of the correct fields and saves the data to an internal
        # list.
        def parse_class(jd):
            # check for the correct fields
            fs = [
                ["name", str],
                ["type", str],
                ["description", str],
                ["keywords", list]
            ]
            parse_check_fields(jd, fs)

            # parse out the type of class
            typestr = jd["type"].lower()
            ctype = None
            if typestr == "income":
                ctype = BudgetClassType.INCOME
            elif typestr == "expense":
                ctype = BudgetClassType.EXPENSE
            assert ctype != None, "each class's type must be \"expense\" or \"income\""

            # extract the list of keywords (as strings)
            keywords = []
            for entry in jd["keywords"]:
                keywords.append(str(entry).lower())

            # add the new class
            c = BudgetClass(jd["name"], ctype, jd["description"], keywords)
            self.classes.append(c)

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
            ["classes", list],
            ["save_location", str]
        ]
        parse_check_fields(jdata, fields)
        self.name = jdata["name"]
        self.spath = jdata["save_location"]

        # parse each budget class
        for entry in jdata["classes"]:
            parse_class(entry)

        # add two default classes - one "uncategorized" for both expenses and
        # income
        keywords = ["uncategorized", "default"]
        self.classes.append(BudgetClass("Uncategorized Expenses",
                            BudgetClassType.EXPENSE, "Default expense category.",
                            keywords))
        self.classes.append(BudgetClass("Uncategorized Income",
                            BudgetClassType.INCOME, "Default income category.",
                            keywords))
     

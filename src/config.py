# Module responsible for reading the configuration file.
#
#   Connor Shugg

# Imports
import json

# Local imports
from classes import ExpenseClass, IncomeClass

# Main configuration class.
class Config:
    # Takes in the file path.
    def __init__(self, fpath):
        self.fpath = fpath
        # set up config fields as None (initialized in 'parse()')
        self.name = None    # configuration name
        self.eclasses = []  # expense class list
        self.iclasses = []  # income class list
    
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
        
        # Used to parse an expense class from within the JSON data. Checks for
        # the presence of the correct fields and saves the data to an internal
        # list.
        def parse_eclass(jd):
            # check for the correct fields
            fs = [["name", str], ["description", str]]
            parse_check_fields(jd, fs)
            self.eclasses.append(ExpenseClass(jd["name"], jd["description"]))
        
        # Used to parse an income class from within the JSON data. Checks for
        # the presence of the correct fields and saves the data to an internal
        # list.
        def parse_iclass(jd):
            # check for the correct fields
            fs = [["name", str], ["description", str]]
            parse_check_fields(jd, fs)
            self.iclasses.append(IncomeClass(jd["name"], jd["description"]))

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
            ["expense_classes", list],
            ["income_classes", list],
            ["save_location", str]
        ]
        parse_check_fields(jdata, fields)
        self.name = jdata["name"]
        self.sdpath = jdata["save_location"]

        # parse each expense class
        for entry in jdata["expense_classes"]:
            parse_eclass(entry)
        # parse each incoem class
        for entry in jdata["income_classes"]:
            parse_iclass(entry)
    
    # Performs initialization procedures *after* parse() has been successfully
    # invoked.
    def init(self):
        # first, attempt
        pass

# TEST CODE
c = Config("./config/example.json")
c.parse()
print("Budget: %s" % c.name)
print("Expense classes:")
for ec in c.eclasses:
    print("\t%s" % ec)
print("Income classes:")
for ic in c.iclasses:
    print("\t%s" % ic)



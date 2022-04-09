# This module defines expense and income classes for my budget.
#
#   Connor Shugg

# Imports
import os
import sys
import json
from enum import Enum
from datetime import datetime
import hashlib

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
from lib.transaction import Transaction

# ================================ Type Enum ================================= #
# Simple enum to differentiate between the *types* of budget classes.
class BudgetClassType(Enum):
    EXPENSE = 0,
    INCOME = 1

# =============================== Budget Class =============================== #
# Represents a single "category"/"class" of budgeting.
class BudgetClass:
    # Constructs a new expense class given a name, type, and description.
    def __init__(self, name, ctype, desc, keywords=[], history=[], bcid=None):
        self.name = name            # name of the class
        self.ctype = ctype          # type of class (EXPENSE, INCOME, etc.)
        self.desc = desc            # description of this class
        self.keywords = keywords    # keywords to identify this class
        self.history = history      # transaction history
        # we'll generate a unique ID string for this budget class if one wasn't
        # passed into the function
        self.bcid = bcid
        if self.bcid == None:
            # combine name, description, type, and keywords into one big string
            self.bcid = self.name + self.desc + str(self.ctype)
            for word in self.keywords:
                self.bcid += word
            # throw in the current datetime as well
            self.bcid += "%d" % datetime.now().timestamp()
            # now, hash the string to form the ID
            self.bcid = hashlib.sha256(self.bcid.encode("utf-8")).hexdigest().lower()
    
    # Used to create a string representation of the budget class object.
    def __str__(self):
        typestr = "INC" if self.ctype == BudgetClassType.INCOME else "EXP"
        return "%s (%s): %s" % (self.name, typestr, self.desc)
    
    # Used to iterate across a class's transaction history.
    def __iter__(self):
        for t in self.all():
            yield t

    # --------------------------------- JSON --------------------------------- #
    # Used to convert the class into a JSON object.
    def to_json(self):
        # iterate through the history and generate a list of JSON objects
        hdata = []
        for t in self.history:
            hdata.append(t.to_json())

        # generate the final JSON
        jdata = {
            "id": self.bcid,
            "name": self.name,
            "type": "income" if self.ctype == BudgetClassType.INCOME else "expense",
            "description": self.desc,
            "keywords": self.keywords,
            "history": hdata,
        }
        return jdata
    
    # Used to create a BudgetClass object from raw JSON data.
    @staticmethod
    def from_json(jdata):
        # build a list of expected JSON fields and assert they exist
        expected = [
            ["id", str, "each class file must have a unique \"id\" string."],
            ["name", str, "each class file must have a \"name\" string."],
            ["type", str, "each class file must have a \"type\" string."],
            ["description", str, "each class file must have a \"description\" string."],
            ["keywords", list, "each class file must have \"keywords\" list."],
            ["history", list, "each class file must have a \"history\" list."],
        ]
        for f in expected:
            assert f[0] in jdata and type(jdata[f[0]]) == f[1], f[2]

        # check the correct type
        typestr = jdata["type"].lower()
        assert typestr in ["expense", "income"], \
               "a class's \"type\" must be either \"expense\" or \"income\""
        ctype = BudgetClassType.INCOME if typestr == "income" else BudgetClassType.EXPENSE

        # create the budget class object
        c = BudgetClass(jdata["name"], ctype, jdata["description"],
                        keywords=jdata["keywords"], history=[],
                        bcid=jdata["id"])
        
        # try to extract the list of history objects and add them to the new
        # budget class object
        for entry in jdata["history"]:
            c.add(Transaction.from_json(entry))
        return c
    
    # ------------------------------- File IO -------------------------------- #
    # Writes this budget class out to disk as a JSON file.
    def save(self, fpath):
        # first, convert the object to JSON
        jdata = self.to_json()
        # open the file, write it all out, then close
        fp = open(fpath, "w")
        fp.write(json.dumps(jdata, indent=4))
        fp.close()

    # Used to load a budget class JSON file from disk. Returns a new BudgetClass
    # object on success. Throws some exception on failure.
    @staticmethod
    def load(fpath):
        # open, read entire content, try to convert to a dictionary, then close
        fp = open(fpath, "r")
        jdata = json.loads(fp.read())
        fp.close()
        # invoke the 'from_json' function and return
        return BudgetClass.from_json(jdata)

    # Turns the category's name in to a Linux-friendly file name.
    def to_file_name(self):
        fname = self.name.lower()
        fname = fname.replace(" ", "_")
        return fname + ".json"
    
    # ------------------------------ Operations ------------------------------ #
    # Takes in a class ID and returns True if this object's ID matches.
    def match_id(self, bcid):
        return self.bcid == bcid

    # Takes in a string and attempts to match it against the class's ID or one
    # of the class's keywords. If it loosely matches ('text' is either contained
    # in or equal to one of the keywords), True is returned.
    # Otherwise, False is returned.
    def match(self, text):
        text = text.lower()
        # check all keywords
        for word in self.keywords:
            if text in word:
                return True
        return False

    # Adds an 'transaction' object that represents a single transaction. Also
    # sets the transaction's 'owner' field to point at this class.
    def add(self, transaction):
        transaction.owner = self
        self.history.append(transaction)
    
    # Removes the given transaction from the list. Returns True if the removal
    # succeeded, False otherwise.
    def remove(self, transaction):
        idx = self.history.index(transaction)
        if idx < 0:
            return False
        self.history.pop(idx)
        transaction.owner = None
        return True
    
    # Returns a list of all the class's transactions in sorted order by
    # timestamp (with the most recent transactions appearing first)
    def all(self):
        return sorted(self.history, key=lambda t: t.timestamp, reverse=True)
    
    # Makes a shallow copy of the budget class with the same ID.
    def copy(self):
        return BudgetClass(self.name, self.ctype, self.desc,
                           keywords=self.keywords, history=self.history,
                           bcid=self.bcid)


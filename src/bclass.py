# This module defines expense and income classes for my budget.
#
#   Connor Shugg

# Imports
from enum import Enum

# ================================ Type Enum ================================= #
# Simple enum to differentiate between the *types* of budget classes.
class BudgetClassType(Enum):
    EXPENSE = 0,
    INCOME = 1

# =============================== Budget Class =============================== #
# Represents a single "category"/"class" of budgeting.
class BudgetClass:
    # Constructs a new expense class given a name, type, and description.
    def __init__(self, name, ctype, desc, keywords=[]):
        self.name = name
        self.ctype = ctype
        self.desc = desc
        self.keywords = keywords
        self.history = []
    
    # Used to create a string representation of the budget class object.
    def __str__(self):
        typestr = "INC" if self.ctype == BudgetClassType.INCOME else "EXP"
        return "%s (%s): %s" % (self.name, typestr, self.desc)

    # Used to convert the class into a JSON object.
    def to_json(self):
        # iterate through the history and generate a list of JSON objects
        hdata = []
        for t in self.history:
            hdata.append(t.to_json())

        # generate the final JSON
        jdata = {
            "name": self.name,
            "type": "income" if self.ctype == BudgetClassType.INCOME else "expense",
            "description": self.desc,
            "keywords": self.keywords,
            "history": hdata
        }
        return jdata
    
    # Turns the category's name in to a Linux-friendly file name.
    def to_file_name(self):
        fname = self.name.lower()
        fname = fname.replace(" ", "_")
        return fname + ".json"
    
    # Takes in a string and attempts to match it against one of the class's
    # keywords. If it loosely matches ('text' is either contained or equal to
    # one of the keywords), True is returned. Otherwise, False is returned.
    def match(self, text):
        text = text.lower()
        for word in self.keywords:
            if text in word:
                return True
        return False

    # Adds an 'transaction' object that represents a single transaction.
    def add(self, transaction):
        self.history.append(transaction)    


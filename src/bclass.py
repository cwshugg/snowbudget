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
    def __init__(self, name, ctype, desc):
        self.name = name
        self.ctype = ctype
        self.desc = desc
        self.history = []
    
    # Used to create a string representation of the budget class object.
    def __str__(self):
        typestr = "INC" if self.ctype == BudgetClassType.INCOME else "EXP"
        return "%s (%s): %s" % (self.name, typestr, self.desc)

    # Adds an 'transaction' object that represents a single transaction.
    def add(self, transaction):
        self.history.append(transaction)


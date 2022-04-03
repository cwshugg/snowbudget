# This module defines expense and income classes for my budget.
#
#   Connor Shugg

# =============================== Parent Class =============================== #
class BudgetClass:
    # Constructs a new expense class given a name and description.
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc
        self.history = []
    
    # Used to create a string representation of the budget class object.
    def __str__(self):
        return "%s: %s" % (self.name, self.desc)

    # Adds an 'transaction' object that represents a single transaction.
    def add(self, transaction):
        self.history.append(transaction)

# ================================= Expenses ================================= #
class ExpenseClass(BudgetClass):
    # Computes the sum of all the class's transactions. Returns the total as a
    # NEGATIVE integer.
    def sum(self):
        total = 0.0
        for t in self.history:
            total += float(t.price)
        return -total
    
# ================================== Income ================================== #
class IncomeClass(BudgetClass):
    # Computes the sum of all the class's transactions. Returns the total as a
    # POSITIVE integer.
    def sum(self):
        total = 0.0
        for t in self.history:
            total += float(t.price)
        return total


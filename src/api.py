# This module defines API to retrieve, update, and manage the budget. This
# should be used after setting up configurations through a Config object.
#
#   Connor Shugg

# Local imports
import config
from bclass import BudgetClassType
from transaction import Transaction

class API:
    # Takes in the Config object that was parsed prior to this object's
    # creation.
    def __init__(self, conf):
        # copy references to the config's classes
        self.classes = conf.classes
        
        # locate the default category for expenses
        self.eclass_default = None
        self.iclass_default = None
        for c in self.classes:
            # first, check if the names match
            if config.uncategorized_name.lower() in c.name.lower():
                # if the names match, check the expense type 
                if c.ctype == BudgetClassType.EXPENSE:
                    self.eclass_default = c
                elif c.ctype == BudgetClassType.INCOME:
                    self.iclass_default = c

        # assert that both were found
        assert self.eclass_default != None, \
               "failed to find a default class for expenses."
        assert self.iclass_default != None, \
               "failed to find a default class for income."

    # ------------------------------ Retrieval ------------------------------- #
    # Takes in a name and searches the expense classes for a matching one.
    # Returns the ExpenseClass object, or None if one isn't found.
    # This does a "loose" search; all strings are compared in lowercase and a
    # match succeeds if 'name' is IN a class's name, not necessarily EQUAL.
    # The type is optional. If a type is given, *only* those classes with the
    # matching type will be searched. If a type isn't given, they will all be
    # searched, and the first match will be returned.
    # The expense class is returned as a JSON object.
    def get_class(self, name, ctype=None):
        name = name.lower()
        for c in self.classes:
            # if a type was given, only consider the ones with a matching type
            if ctype != None and c.ctype != ctype:
                continue
            # if the query is contained by the class's name, we'll take it
            if name in c.name.lower():
                return c.to_json()
        return None
    
    # ------------------------------- Updates -------------------------------- #
    # Takes in information about a transaction and adds it to one expense class
    # or income class.
    #   - If 'price' is negative, it's assumed to be an income.
    #   - If 'category' is blank, it's added to a default "nameless" income or
    #     expense class.
    def add_transaction(self, price, category=None, vendor=None, description=None):
        t = Transaction(price, vendor, description)

        # find the correct category to place this transaction into (only
        # consider income categories if the price is negative)
        ctype = BudgetClassType.INCOME if price < 0.0 else None
        c = self.get_class(category, ctype)
        print("FOUND CATEGORY: %s" % c)
        
# TEST CODE
import sys
c = config.Config("./config/example.json")
c.parse()
print("Budget: %s" % c.name)
print("Expense classes:")
for ec in c.classes:
    print("\t%s" % ec)
c.init()

print("\nAPI STUFF:")
api = API(c)
print("Search: %s" % api.get_class(sys.argv[1]))


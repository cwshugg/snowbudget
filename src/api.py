# This module defines API to retrieve, update, and manage the budget. This
# should be used after setting up configurations through a Config object.
#
#   Connor Shugg

# Imports
import os

# Local imports
import config
from bclass import BudgetClassType
from transaction import Transaction
from disk import Disk

class API:
    # Takes in the Config object that was parsed prior to this object's
    # creation.
    def __init__(self, conf):
        # locate the default category for expenses
        self.eclass_default = None
        self.iclass_default = None
        for c in conf.classes:
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

        # set up a disk object, then initialize files (if not already existing)
        # for each budget class
        self.disk = Disk(os.path.realpath(conf.spath))
        for c in conf.classes:
            if not self.disk.check_class(c):
                self.disk.write_class(c)

        # now, attemp to load each file into memory (for each class)
        self.classes = []   # master list of classes
        for c in conf.classes:
            bclass = self.disk.load_class(c.to_file_name())
            bclass.dirty = False # mark as NOT dirty to start
            self.classes.append(bclass)

    # ------------------------------ Retrieval ------------------------------- #
    # Takes in text and searches the expense classes for a matching one.
    # Returns the BudgetClass object, or None if one isn't found.
    # This does a "loose" search; all strings are compared in lowercase and a
    # match succeeds if 'text' is IN a class's keywords, not necessarily EQUAL.
    # The type is optional. If a type is given, *only* those classes with the
    # matching type will be searched. If a type isn't given, they will all be
    # searched, and the first match will be returned.
    def get_class(self, text, ctype=None):
        text = text.lower()
        for c in self.classes:
            # if a type was given, only consider the ones with a matching type
            if ctype != None and c.ctype != ctype:
                continue
            # attempt to match the class - return on true
            if c.match(text):
                return c
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
        # consider income categories if the price is negative). If no category
        # was given, we'll put it in the 'default expenses' bucket
        c = self.iclass_default if price < 0.0 else self.eclass_default
        if category != None:
            ctype = BudgetClassType.INCOME if price < 0.0 else None
            c = self.get_class(category, ctype)

        # add the new transaction to the category and mark the class as dirty
        c.add(t)
        c.dirty = True

    # ------------------------------- Storage -------------------------------- #
    # Saves all modified classes to disk. Returns True if *something* was
    # written to disk. False otherwise
    def save(self):
        count = 0
        # iterate across the number of classes we have
        for c in self.classes:
            # if the class hasn't been marked as 'dirty', skip it (since nothing
            # has been changed yet)
            if not c.dirty:
                continue
            # otherwise, write it out to disk
            self.disk.write_class(c)
            count += 1
        return count > 0


# TEST CODE
import sys
c = config.Config("./config/example.json")
c.parse()
#print("Budget: %s" % c.name)
#print("Expense classes:")
#for ec in c.classes:
#    print("\t%s (%s)" % (ec, ec.keywords))

#print("\nAPI STUFF:")
api = API(c)
api.save()
print("Search: %s" % api.get_class(sys.argv[1]).to_json())


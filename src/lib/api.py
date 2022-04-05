# This module defines API to retrieve, update, and manage the budget. This
# should be used after setting up configurations through a Config object.
#
#   Connor Shugg

# Imports
import os
import sys

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
import lib.config as config
from lib.bclass import BudgetClassType
from lib.transaction import Transaction
from lib.disk import Disk

class API:
    # Takes in the Config object that was parsed prior to this object's
    # creation.
    def __init__(self, conf):
        # locate the default category for expenses
        self.eclass_default = None
        self.iclass_default = None
        assert len(conf.classes) > 0, "found no classes in the config."
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
    # Takes in an optional class type and returns all budget classes that are of
    # the same class type (or *all* classes if no type is given).
    def get_classes(self, ctype=None):
        result = []
        for bclass in self.classes:
            # skip those with the wrong type, if applicable
            if ctype != None and bclass.ctype != ctype:
                continue
            result.append(bclass)
        return result

    # Takes in text and searches the expense classes for a matching one.
    # Returns the BudgetClass object, or None if one isn't found.
    # This does a "loose" search; all strings are compared in lowercase and a
    # match succeeds if 'text' is IN a class's keywords, not necessarily EQUAL.
    # The type is optional. If a type is given, *only* those classes with the
    # matching type will be searched. If a type isn't given, they will all be
    # searched, and the first match will be returned.
    def find_class(self, text, ctype=None):
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
            c = self.find_class(category, ctype)

        # add the new transaction to the category and mark the class as dirty
        c.add(t)
        c.dirty = True
    
    # Used to search for a transaction given some sort of information about it.
    # Returns a list with this content:
    #       [transaction_object, budget_class_object_it_belongs_to]
    # OR returns None if nothing matching is found.
    def find_transaction(self, price=None, vendor=None, description=None,
                         category=None):
        # make sure we were given *something* to go off of
        assert price != None or vendor != None or description != None or \
               category != None, \
               "some sort of information about the transaction must be given."
        # if a category was given, search for the correct budget class
        bclass = None
        if category != None:
            bclass = self.find_class(category)
        
        # before searching, compare all strings to lowercase
        vendor = vendor.lower() if vendor != None else None
        description = description.lower() if description != None else None

        # now, build an array (either of length 1 or the entire set) and iterate
        # through it to check all the appropriate classes
        bcs = [bclass] if bclass != None else self.classes
        for bc in bcs:
            # search through each transaction in reverse order (most recent
            # will be checked first)
            for t in bc.sort():
                if t.match(price=price, vendor=vendor, description=description):
                    return [t, bc]
        # if we get here, then nothing suitable was found
        return None
    
    # Takes in a Transaction and its current budget class, as well as a new
    # budget class, and moves the transaction from one to the other.
    # Returns True if a move occurred, False otherwise.
    def move_transaction(self, transaction, bclass_old, bclass_new):
        # if the classes are the same, there's no move to do
        if bclass_old == bclass_new:
            return False
        
        # attempt to remove (check for failure)
        if not bclass_old.remove(transaction):
            return False
        
        # push onto the new budget class, then mark both classes as dirty
        bclass_new.add(transaction)
        bclass_old.dirty = True
        bclass_new.dirty = True
        return True
    
    # Takes in a transaction and its budget class and removes it from the class.
    # Returns True on a successful deletion, false otherwise.
    def delete_transaction(self, transaction, bclass):
        # attempt to remove
        if not bclass.remove(transaction):
            return False
        bclass.dirty = True
        return True

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
            # otherwise, write it out to disk (after sorting) and reset the
            # class's dirty flag
            c.sort()
            self.disk.write_class(c)
            c.dirty = False
            count += 1
        return count > 0


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
from lib.bclass import BudgetClass, BudgetClassType
from lib.transaction import Transaction
from lib.disk import Disk

# API class
class API:
    # Takes in the Config object that was parsed prior to this object's
    # creation.
    def __init__(self, conf):
        assert len(conf.classes) > 0, "found no classes in the config."
        # search through each class and make sure there's only ONE default
        # class for each type (EXPENSE, INCOME)
        edefaults = []
        idefaults = []
        for c in conf.classes:
            if c.default:
                if c.ctype == BudgetClassType.INCOME:
                    idefaults.append(c)
                else:
                    edefaults.append(c)
        assert len(edefaults) <= 1, "there cannot be more than one default expense class."
        assert len(idefaults) <= 1, "there cannot be more than one default income class."

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
    # Returns a list of matching BudgetClass objects.
    def find_class(self, text, ctype=None):
        text = text.lower()
        result = []
        for c in self.classes:
            # if a type was given, only consider the ones with a matching type
            if ctype != None and c.ctype != ctype:
                continue
            # attempt to match the class - return on true
            if c.match(text):
                result.append(c)
        return result
    
    # Used to search for a transaction given some sort of information about it.
    # Returns a list of transaction objects that matched the text in one way
    # or another. Returns an empty list if no match is found.
    def find_transaction(self, text):
        text = text.lower()
        result = []

        # search through all budget classes
        for bc in self.classes:
            # search through each transaction in sorted order (most recent
            # will be checked first)
            for t in bc.sort():
                if t.match(text):
                    result.append(t)
        # return the resulting list
        return result

    # ------------------------------- Updates -------------------------------- #
    # Takes in a transaction object and adds it to the budget class.
    def add_transaction(self, transaction, bclass):
        # add the new transaction to the category and mark the class as dirty
        bclass.add(transaction)
        bclass.dirty = True
        
    # Takes in a Transaction and a new budget class to assign it to. The
    # transaction is removed from its current class and re-assigned to the
    # new one.
    # Returns True if a move occurred, False otherwise.
    def move_transaction(self, transaction, bclass):
        old_bclass = transaction.owner
        # if the current owner is the same as this bclass, there's nothing to do
        if old_bclass == bclass:
            return False
        
        # attempt to remove (check for failure)
        if not old_bclass.remove(transaction):
            return False
        
        # add the transaction to the new class, then mark both classes as dirty
        bclass.add(transaction)
        old_bclass.dirty = True
        bclass.dirty = True
        return True
    
    # Takes in a transaction and deletes it from the class.
    # Returns True on a successful deletion, false otherwise.
    def delete_transaction(self, transaction):
        # retrieve the transaction's owner
        bclass = transaction.owner
        assert bclass != None, "the given transaction has no owner"

        # attempt to remove, then mark the class as dirty
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

    # ----------------------------- JSON Helpers ----------------------------- #
    # Creates one monolithic JSON struct containing all budget classes and
    # all transactions within them.
    def to_json(self):
        jdata = []
        # iterate through all classes and add their JSON to the data
        for c in self.classes:
            jdata.append(c.to_json())
        return jdata


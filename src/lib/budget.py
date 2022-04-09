# This module defines the class that represents a single budget. Takes in a
# parsed Config object and does the rest of the work.
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
from lib.bclass import BudgetClass, BudgetClassType
from lib.transaction import Transaction

# Budget class
class Budget:
    # Takes in the Config object that was parsed prior to this object's
    # creation.
    def __init__(self, conf):
        self.conf = conf
        self.classes = []
        # get the config's save location and iterate through the directory's
        # files to load in each budget class
        for root, dirs, files in os.walk(conf.save_location):
            for f in files:
                # if the file has the JSON extension, we'll try to load it as a
                # budget class object
                if f.lower().endswith(".json"):
                    bc = BudgetClass.load(os.path.join(root, f))
                    self.classes.append(bc)
    
    # Used to iterate through the budget's classes.
    def __iter__(self):
        for bc in self.all():
            yield bc

    # ------------------------------ Additions ------------------------------- #
    # Takes in a BudgetClass object and adds it to the budget. Upon calling this
    # function, the budget is written out to a file.
    def add_class(self, bclass):
        # before appending to the array, make sure there are no name conflicts
        for bc in self.classes:
            assert bclass.name.lower() != bc.name.lower(), \
                   "duplicate budget class name detected"
        self.classes.append(bclass)

        # write out to a file
        fpath = os.path.join(self.conf.save_location, bclass.to_file_name())
        bclass.save(fpath)
    
    # Takes in a transaction and a budget class and adds it to the budget class,
    # then saves the budget class out to disk.
    def add_transaction(self, bclass, transaction):
        bclass.add(transaction)
        fpath = os.path.join(self.conf.save_location, bclass.to_file_name())
        bclass.save(fpath)

    # ------------------------------ Searching ------------------------------- #
    # Expects a class ID string and searches the class list for it. Returns the
    # first matching budget class, or None if nothing was found.
    def get_class(self, class_id):
        for bc in self.classes:
            if bc.match_id(class_id):
                return bc
        return None
    
    # Expects a transaction ID string and searches all classes for it. Returns
    # the transaction object if one is found, or None if nothing is found.
    def get_transaction(self, transaction_id):
        for bc in self.classes:
            for t in bc:
                if t.match_id(transaction_id):
                    return t
        return None

    # Takes in text and searches the expense classes for a matching one.
    # Returns a list of matching BudgetClass objects.
    def search_class(self, text):
        result = []
        # search through all budget classes (sorted)
        for c in self.all():
            # if the class matches the text in one way or another, add it
            if c.match(text):
                result.append(c)
        return result
    
    # Used to search for a transaction given some sort of information about it.
    # Returns a list of transaction objects that matched the text in one way
    # or another. Returns an empty list if no match is found.
    def search_transaction(self, text):
        result = []
        # search through all budget classes (sorted)
        for bc in self.all():
            # search through each transaction in sorted order (most recent
            # will be checked first)
            for t in bc.all():
                if t.match(text):
                    result.append(t)
        # return the resulting list
        return result
    
    # ------------------------------ Removals -------------------------------- #
    # Takes in a budget class and does two things:
    #   1. Deletes its file on disk
    #   2. Removes the class from the Budget object's internal list
    # This throws an exception if the class isn't found within.
    def delete_class(self, bclass):
        # use the given class's ID to find the equivalent object stored in the
        # Budget object, then use it to get the index
        bc = self.get_class(bclass.bcid)
        idx = self.classes.index(bc)
        self.classes.pop(idx)

        # now, build the file path and delete the file
        fpath = os.path.join(self.conf.save_location, bc.to_file_name())
        os.remove(fpath)

    # Takes in a transaction and deletes it from its corresponding budget class.
    # Throws an exception if the transaction isn't inside the budget.
    def delete_transaction(self, transaction):
        # locate the true transaction object stored within the budget object AND
        # the true budget class that's storing the transaction
        t = self.get_transaction(transaction.tid)
        bc = self.get_class(transaction.owner.bcid)
        
        # remove the transaction from the class, then save the budget class
        bc.remove(t)
        fpath = os.path.join(self.conf.save_location, bc.to_file_name())
        bc.save(fpath)

    # ---------------------------- Manual Saving ----------------------------- #
    # Takes in a class and saves it to the correct location.
    def update_class(self, bclass):
        # first, delete the old version of the same budget class. Then, save the
        # new one with its updated fields
        self.delete_class(bclass)
        self.add_class(bclass)

    # ------------------------------ Retrieval ------------------------------- #
    # Returns *all* budget classes within the budget, in sorted order by name.
    def all(self):
        return sorted(self.classes, key=lambda bc: bc.name.lower())
    
    # ----------------------------- JSON Helpers ----------------------------- #
    # Creates one monolithic JSON struct containing all budget classes and
    # all transactions within them.
    def to_json(self):
        jdata = []
        # iterate through all classes and add their JSON to the data
        for c in self.classes:
            jdata.append(c.to_json())
        return jdata


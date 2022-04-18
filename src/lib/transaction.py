# This module defines a Transaction object, used to represent a single expense
# or income event.
#
#   Connor Shugg

# Imports
import os
import sys
from datetime import datetime
import hashlib

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

class Transaction:
    # Takes in the vendor of the transaction, the price (absolute value), and
    # one or two more optional fields.
    def __init__(self, price, vendor="", description="", timestamp=datetime.now(),
                 tid=None, owner=None, recur=False):
        self.price = price
        self.vendor = vendor
        self.desc = description
        self.timestamp = timestamp
        self.recurring = recur      # whether or not this repeats each cycle
        self.owner = owner # backwards reference to owner budget class

        # if one wasn't given, we'll generate a unique transaction ID
        self.tid = tid
        if self.tid == None:
            self.tid = str(self.price) + str(self.vendor) + str(self.desc) + \
                       str(self.timestamp)
            self.tid = hashlib.sha256(self.tid.encode("utf-8")).hexdigest().lower()
    
    # Used to build a string representation of a transaction.
    def __str__(self):
        return "%s %s%s%s" % (self.to_date_string(),
               self.to_dollar_string(),
               "" if self.vendor == None else " (%s)" % self.vendor,
               "" if self.desc == None else ": %s" % self.desc)
    
    # Converts the transaction's timestamp to a date string and returns it.
    def to_date_string(self):
        return self.timestamp.strftime("%Y-%m-%d")
    
    # Converts the transaction's price to a dollar string.
    def to_dollar_string(self):
        return "$%.2f" % self.price

    # --------------------------------- JSON --------------------------------- #
    # Used to convert this object into a JSON object.
    def to_json(self):
        jdata = {
            "id": self.tid,
            "price": self.price,
            "vendor": self.vendor,
            "description": self.desc,
            "timestamp": self.timestamp.timestamp(),
            "recurring": self.recurring
        }
        return jdata
    
    # Used to create a Transaction object from raw JSON data.
    @staticmethod
    def from_json(jdata):
        # build a list of expected JSON fields and assert they exist
        expected = [
            ["id", str, "each transaction JSON must have a unique \"id\" string."],
            ["price", float, "each transaction JSON must have a \"price\" float."],
            ["vendor", str, "each transaction JSON must have a \"vendor\" string."],
            ["description", str, "each transaction JSON must have a \"description\" list."],
            ["timestamp", float, "each transaction JSON must have a \"timestamp\" float."],
            ["recurring", bool, "each transaction JSON must have a \"recurring\" boolean."]
        ]
        for f in expected:
            assert f[0] in jdata and type(jdata[f[0]]) == f[1], f[2]

        # attempt to parse the timestamp
        ts = datetime.fromtimestamp(jdata["timestamp"])
            
        # create the object
        t = Transaction(jdata["price"], vendor=jdata["vendor"],
                        description=jdata["description"], timestamp=ts,
                        tid=jdata["id"], recur=jdata["recurring"])
        return t
    
    # ------------------------------ Operations ------------------------------ #
    # Takes in a transaction ID and returns true if this object's ID matches.
    def match_id(self, tid):
        return self.tid == tid
    
    # Attempts to match this transaction based on information given. Returns
    # True if a match is detected and False otherwise. Primarily checks the ID
    # of the transaction, then checks other fields.
    def match(self, text):
        text = text.lower()
        # check the timestamp
        try:
            if int(text) == int(self.timestamp.timestamp()):
                return True
        except Exception as e:
            pass

        # check price
        if text in str(self.price):
            return True

        # check description
        if text in self.desc.lower():
            return True
        # check vendor
        if text in self.vendor.lower():
            return True
        
        # otherwise, we'll return false
        return False


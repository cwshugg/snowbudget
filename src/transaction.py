# This module defines a Transaction object, used to represent a single expense
# or income event.
#
#   Connor Shugg

# Imports
from datetime import datetime

class Transaction:
    # Takes in the vendor of the transaction, the price (absolute value), and
    # one or two more optional fields.
    def __init__(self, price, vendor=None, description=None, timestamp=datetime.now()):
        self.price = price
        self.vendor = vendor
        self.desc = description
        self.timestamp = timestamp
    
    # Used to build a string representation of a transaction.
    def __str__(self):
        return "%s %s%s%s" % (self.to_date_string(),
               self.to_dollar_string(),
               "" if self.vendor == None else " (%s)" % self.vendor,
               "" if self.desc == None else ": %s" % self.desc)
    
    # Converts the transaction's timestamp to a date string and returns it.
    def to_date_string(self):
        return self.timestamp.strftime("%Y-%M-%d")
    
    # Converts the transaction's price to a dollar string.
    def to_dollar_string(self):
        return "$%.2f" % self.price

    # ----------------------------- JSON Helpers ----------------------------- #
    # Used to convert this object into a JSON object.
    def to_json(self):
        jdata = {
            "price": self.price,
            "vendor": self.vendor,
            "description": self.desc,
            "timestamp": self.timestamp.timestamp()
        }
        return jdata
    
    # Used to create a Transaction object from raw JSON data.
    @staticmethod
    def from_json(jdata):
        # build a list of expected JSON fields and assert they exist
        expected = [
            ["price", float, "each transaction JSON must have a \"price\" float."],
            ["vendor", str, "each transaction JSON must have a \"vendor\" string."],
            ["description", str, "each transaction JSON must have a \"description\" list."],
            ["timestamp", float, "each transaction JSON must have a \"timestamp\" float."]
        ]
        for f in expected:
            assert f[0] in jdata and type(jdata[f[0]]) == f[1], f[2]

        # attempt to parse the timestamp
        ts = datetime.fromtimestamp(jdata["timestamp"])
            
        # create the object
        t = Transaction(jdata["price"], vendor=jdata["vendor"],
                        description=jdata["description"], timestamp=ts)
        return t

    # ------------------------------ Operations ------------------------------ #
    # Attempts to match this transaction based on information given. Returns
    # True if a match is detected and False otherwise.
    def match(self, price=None, vendor=None, description=None, timestamp=None):
        assert price != None or vendor != None or description != None or timestamp != None, \
               "at least one piece of information must be given to match a transaction"
        # count the number of fields given versus the number of correct matches
        given = 0
        matched = 0
        expect = [self.price, self.vendor, self.desc, timestamp]
        actual = [price, vendor, description, timestamp]
        for i in range(len(expect)):
            f1 = expect[i]
            f2 = actual[i]
            # if the given field isn't None, we'll compare it
            if f2 != None:
                # determine if the strings match
                match = f2 == f1
                if type(f2) == str:
                    match = match or f2.lower() in f1.lower()
                # increment counters
                given += 1
                matched = matched + 1 if match else matched
        # return whether or not everything compared was matched
        return given == matched


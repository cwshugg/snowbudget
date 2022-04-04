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


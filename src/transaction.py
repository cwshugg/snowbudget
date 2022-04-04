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

    # Used to convert this object into a JSON object.
    def to_json(self):
        jdata = {
            "price": self.price,
            "vendor": self.vendor,
            "description": self.desc
        }
        return jdata


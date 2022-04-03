# This module defines a Transaction object, used to represent a single expense
# or income event.
#
#   Connor Shugg

class Transaction:
    # Takes in the vendor of the transaction, the price (absolute value), and
    # one or two more optional fields.
    def __init__(self, vendor, price, description=None):
        self.vendor = vendor
        self.price = price
        self.description = description


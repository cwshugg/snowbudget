# This module defines a Transaction object, used to represent a single expense
# or income event.
#
#   Connor Shugg

class Transaction:
    # Takes in the vendor of the transaction, the price (absolute value), and
    # one or two more optional fields.
    def __init__(self, price, vendor=None, description=None):
        self.price = price
        self.vendor = vendor
        self.description = description


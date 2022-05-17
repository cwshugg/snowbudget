# This module defines structures used to keep track of budget targets (total
# amounts to aim for or not exceed) during a budget cycle.
#
#   Connor Shugg

# Imports
import os
import sys
from enum import Enum

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)


# ======================== Budget Target Class Types ========================= #
class BudgetTargetType(Enum):
    DOLLAR = 0,             # straight dollar value
    PERCENT_INCOME = 1,     # percentage of the month's total income


# =========================== Budget Target Class ============================ #
# Simple class used to represent the *target* for a budget class (i.e. a total
# spending amount to aim for through the current budget cycle).
class BudgetTarget:
    # Constructor. Takes in the value and the type of target this represents.
    def __init__(self, value, ttype=BudgetTargetType.DOLLAR):
        self.value = value
        self.ttype = ttype
        # if the type is a percentage, ensure it's between [0%, 100%]
        if ttype == BudgetTargetType.PERCENT_INCOME:
            assert self.value >= 0.0 and self.value <= 1.0
    
    # Takes in an optional 'total' field (representing the total income for the
    # budget cycle) and computes the target's value.
    def get_value(self, total_income=None):
        # first case: PERCENT_INCOME. Multiply by total income
        if self.ttype == BudgetTargetType.PERCENT_INCOME:
            assert total_income != None
            return float(total_income * self.value)
        # other case: DOLLAR amount. Simply return the value
        return self.value

    # --------------------------------- JSON --------------------------------- #
    # Returns a simple JSON object representation of the target.
    def to_json(self):
        # convert the type to a string
        tstr = "dollar" if self.ttype == BudgetTargetType.DOLLAR else "percent_income"
        return {"value": self.value, "type": tstr}
    
    # Used to parse a given JSON object and return an initialized BudgetTarget.
    @staticmethod
    def from_json(jdata):
        # check for the expected fields
        expected = [
            ["value", [int, float], "each budget target JSON must have a \"value\" float"],
            ["type", [str], "each budget target JSON must have a \"type\" string"]
        ]
        for e in expected:
            assert e[0] in jdata and type(jdata[e[0]]) in e[1], e[2]

        # check for the correct type string
        tstr = jdata["type"].lower()
        expected_type = ["dollar", "percent_income"]
        assert tstr in expected_type, \
               "each budget target JSON's \"type\" must be one of: %s" % expected_type
        tt = BudgetTargetType.DOLLAR
        if tstr == "percent_income":
            tt = BudgetTargetType.PERCENT_INCOME

        # invoke the constructor and return the object
        return BudgetTarget(float(jdata["value"]), ttype=tt)


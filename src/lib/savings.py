# This module defines a class used to keep track of savings categories.
#
#   Connor Shugg

class SavingsCategory:
    # Simple constructor that takes in a name and a percentage.
    def __init__(self, name, percent):
        self.name = name
        self.percent = percent

    # ----------------------------- JSON Helpers ----------------------------- #
    # Takes in JSON and and attempts to use it to create a new SavingsCategory
    # object. The object is returned.
    @staticmethod
    def from_json(jdata):
        # make sure our fields are what we expect
        assert "category" in jdata and type(jdata["category"]) == str and \
               "percent" in jdata and type(jdata["percent"]) == float, \
               "each 'surplus_savings' entry much have a \"category\" string " \
               "and a 'percent' float"
        return SavingsCategory(jdata["category"], jdata["percent"])
    
    # Converts the current object to a JSON object and returns it.
    def to_json(self):
        return {"category": self.name, "percent": self.percent}


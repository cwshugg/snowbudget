# Module responsible for reading the configuration file.
#
#   Connor Shugg

# Imports
import json
import os
import sys
from datetime import datetime

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
from lib.savings import SavingsCategory

# Main configuration class.
class Config:
    # Takes in the file path.
    def __init__(self, fpath, dt=datetime.now()):
        self.fpath = fpath
        # set up basic config fields to hold default values
        self.name = None            # configuration name
        self.classes = []           # budget class list
        self.save_location = None   # path to save directory
    
        # -------------------- Main Parsing Functionality -------------------- #
        # open the file, slurp the entire content (should be small), then close
        fp = open(self.fpath)
        content = fp.read()
        fp.close()

        # attempt to convert to JSON and make sure the expected fields are
        # present in the JSON data
        jdata = json.loads(content)
        fields = [
            ["name", str, "missing 'name' string"],
            ["save_location", str, "missing 'save_location' path"],
            ["backup_location", str, "missing 'backup_location' path"],
            ["reset_dates", list, "missing 'reset_dates' list"],
            ["surplus_savings", list, "missing 'surplus_savings' list"]
        ]
        # for each expected entry, assert its existence then set it as a global
        for f in fields:
            key = f[0]
            assert key in jdata and type(jdata[key]) == f[1], f[2]
            setattr(self, key, jdata[key])
        
        # --------------------------- Reset Dates ---------------------------- #
        # for each entry in the reset dates, we'll try to parse out the month
        # and day for each month
        assert len(self.reset_dates) >= 1, "must have at least one reset date"
        rdates = self.reset_dates.copy()
        self.reset_dates = []
        for rd in rdates:
            # convert to a string, trim whitespace, then split by "-"
            rd = str(rd).strip()
            pieces = rd.split("-")
            assert len(pieces) == 2, "each date in 'reset_dates' must have two numbers " \
                                     "split by a dash (\"-\"): \"MONTH-DAY\""
            # extract the month
            month = int(pieces[0].strip())
            assert month > 0 and month < 13, "each month must be between [1, 12]"
            # extract the day
            day = int(pieces[1].strip())
            assert day > 0 and day < 32, "each day must be a valid [1, 31] day of the month"

            # get the given date - we'll use this to set up our reset dates
            # accordingly based on the current month/day
            now = dt
            nmonth = now.month
            nday = now.day
            
            # if this reset date already occurred this year, we'll build its
            # datetime object using *next* year
            already_happened = nmonth > month or \
                               (nmonth == month and nday > day)
            year = now.year
            if already_happened:
                year = year + 1
            self.reset_dates.append(datetime(year, month, day))
        
        # finally, sort the reset dates chronologically
        self.reset_dates = sorted(self.reset_dates)

        # ------------------------- Surplus Savings -------------------------- #
        # for each of the surplus saving categories, we'll parse to verify
        # everything looks good. This allows the user to specify how his/her
        # savings will be split up at the end of each budget cycle
        scs = []
        ss_total = 0.0
        for ss in self.surplus_savings:
            scs.append(SavingsCategory.from_json(ss))
            ss_total += ss["percent"]
        # make sure the total percentages don't reach higher than 100%
        assert ss_total <= 1.0, "the total surplus savings percentages can't be " \
                                "higher than 100% (1.0)"
        self.surplus_savings = scs


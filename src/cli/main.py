#!/usr/bin/python3
# This module implements a command-line interface for interacting with the API
# to add/remove/view transactions.
#
#   Connor Shugg

# Imports
import sys
import os
import argparse

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
from lib.config import Config
from lib.api import API
from lib.bclass import BudgetClassType

# Globals
config = None
api = None

# Pretty-printing globals
STAB = "    "
STAB_TREE1 = " \u2514\u2500 "
STAB_TREE2 = " \u251c\u2500 "
STAB_TREE3 = " \u2503  "
C_NONE = "\033[0m"
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"


# ============================= Helper Functions ============================= #
# Used to print a fatal error and exit.
def fatality(msg=None, exception=None):
    message = "%sFatal error%s%s" % \
              (C_RED,
               ":" if msg != None or exception != None > 0 else ".",
               C_NONE)
    message = message + " %s" % msg if msg != None else message
    message = message + " (%s)" % exception if exception != None else message
    sys.stderr.write(message + "\n")
    sys.exit(1)

# Used to convert a float to a dollar string
def dollar_to_string(value):
    return "$%.2f" % value

# ============================= Argument Parsing ============================= #
# Responsible for parsing command-line arguments.
def parse_args():
    # build a description string to pass into ArgumentParser
    argv0 = os.path.basename(sys.argv[0])
    desc = "Interact with the snowbudget."

    # set up an argument parser and build our list of arguments
    p = argparse.ArgumentParser(description=desc,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", metavar="CONFIG_JSON", required=True,
                   help="Takes in the path to your snowbudget configuration file.",
                   default=None, nargs=1, type=str)
    p.add_argument("--list",
                   help="Lists all budget classes and basic statistics for each.",
                   default=False, action="store_true")

    return vars(p.parse_args())


# ============================ Main Functionality ============================ #
# Prints basic information about each budget class to the terminal.
def list_budget_classes():
    # get all expense and income classes
    eclasses = api.get_classes(ctype=BudgetClassType.EXPENSE)
    iclasses = api.get_classes(ctype=BudgetClassType.INCOME)

    # Helper function for printing a budget class
    def list_budget_class(c, prefix):
        # print the name and description
        color = C_GREEN if c.ctype == BudgetClassType.INCOME else C_YELLOW
        print("%s%s%s%s: %s" % (prefix, color, c.name, C_NONE, c.desc))

        # compute some basic numbers for the class
        stat_total = 0.0
        transactions = c.sort()
        for t in transactions:
            stat_total += t.price
        latest = None if len(transactions) == 0 else transactions[-1]

        # build a list of statistic lines to print
        prefix2 = STAB_TREE3 if prefix == STAB_TREE2 else STAB
        lines = []
        lines.append("Total: %s" % dollar_to_string(stat_total))
        if latest != None:
            lines.append("%d transactions" % len(transactions))
            lines.append("Latest: %s" % latest)

        # print the line of statistics
        llen = len(lines)
        for i in range(llen):
            prefix3 = STAB_TREE2 if i < llen - 1 else STAB_TREE1
            print("%s%s%s" % (prefix2, prefix3, lines[i]))

        # return the total value for this class
        return stat_total

    # process all expense classes
    eclen = len(eclasses)
    ectotal = 0.0
    print("%d Expense Classes:" % eclen)
    for i in range(eclen):
        pfx = STAB_TREE2 if i < eclen - 1 else STAB_TREE1
        ectotal += list_budget_class(eclasses[i], pfx)
    print("Total expenses: %s\n" % dollar_to_string(ectotal))
    
    # process all income classes
    iclen = len(iclasses)
    ictotal = 0.0
    print("%d Income Classes:" % iclen)
    for i in range(iclen):
        pfx = STAB_TREE2 if i < iclen - 1 else STAB_TREE1
        ictotal += list_budget_class(iclasses[i], pfx)
    print("Total income: %s\n" % dollar_to_string(ictotal))

# Main function.
def main():
    # parse the arguments, then parse the config file
    args = parse_args()
    global config
    try:
        config = Config(args["config"][0])
        config.parse()
    except Exception as e:
        fatality(msg="failed to initialize config", exception=e)

    # now, initialize an API object
    global api
    try:
        api = API(config)
    except Exception as e:
        fatality(msg="failed to initialize API", exception=e)

    # if '--list' was given, we'll list basic budget information
    if "list" in args and args["list"]:
        list_budget_classes()
        sys.exit(0)

# =============================== Runner Code ================================ #
if __name__ == "__main__":
    main()


#!/usr/bin/python3
# This module implements a command-line interface for interacting with the API
# to add/remove/view transactions.
#
#   Connor Shugg

# Imports
import sys
import os
import argparse
import json

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
from lib.config import Config
from lib.api import API
from lib.bclass import BudgetClassType
from lib.transaction import Transaction

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
C_CYAN = "\033[36m"

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

# Used when detecting SIGINTs and EOFs.
def abrupt_exit():
    sys.stdout.write("\n")
    sys.stdout.flush()
    sys.exit(0)

# Used to convert a float to a dollar string
def dollar_to_string(value):
    if value < 0.0:
        return "-$%.2f" % abs(value)
    return "$%.2f" % value


# ============================== Input Reading =============================== #
# Takes a prompt and gets a string input from the user. By default, blanks are
# not allowed, but they can be by toggling the switch.
def input_wrapper(prompt, blank_ok=False, color=C_YELLOW):
    # we'll read input until something is given (or EOF)
    while True:
        try:
            result = input("%s%s%s " % (color, prompt, C_NONE))
            if result != "" or blank_ok:
                return result
        except EOFError as e:
            abrupt_exit()
    return None

# Used to get a price value from stdin. Returns None on a failed parse.
def input_price(prompt="Price:", blank_ok=False):
    while True:
        price = input_wrapper(prompt, blank_ok=blank_ok).strip()
        if price == "" and blank_ok:
            return None
        try:
            price = float(price)
            assert price > 0.0
            return price
        except Exception as e:
            print("Please enter a price.")

# Reads from stdin to get a budget class from the user. If a match isn't found
# then None is returned. Otherwise, the BudgetClass object is returned.
def input_budget_class(prompt="[SEARCH] Budget class:"):
    while True:
        bcname = input_wrapper(prompt, color=C_CYAN).strip()
        classes = api.find_class(bcname)
        clen = len(classes)
        # if nothing was found, say so and loop again
        if clen == 0:
            print("Couldn't find anything.")
            continue

        # otherwise we'll have the user pick one out
        print("Found %d budget classes. Please choose one:" % clen)
        for i in range(clen):
            print("%d. %s" % ((i + 1), classes[i]))
        idx = input_number("Class number:", upper=clen, lower=1) - 1
        return classes[idx]

# Asks the user a yes/no question.
def input_boolean(prompt):
    while True:
        val = input_wrapper(prompt).lower().strip()
        if val in ["y", "yes"]:
            return True
        elif val in ["n", "no"]:
            return False
        print("Please enter y/yes or n/no.")

# Prompts the user for an integer, enforcing an optional upper/lower bound.
def input_number(prompt, upper=None, lower=None):
    has_bound = lower != None and upper != None
    while True:
        val = input_wrapper(prompt).strip()
        try:
            # try to convert to an integer and assert it's in range
            val = int(val)
            assert val >= lower and val <= upper
            return val
        except Exception as e:
            print("Please enter a number%s." %
                  (" between %d and %d" % (lower, upper) if has_bound else ""))

# Reads user input to get a specific transaction.
def input_transaction(prompt="[SEARCH] Transaction:"):
    while True:
        # prompt the user to supply some sort of text to search for a transaction
        text = input_wrapper(prompt, color=C_CYAN)
        if text == None:
            sys.stderr.write("You didn't enter any text.\n")
            sys.exit(1)
    
        # now, invoke the API to search for a transaction loop back around if
        # nothing was found
        ts = api.find_transaction(text)
        tlen = len(ts)
        if tlen == 0:
            print("Couldn't find anything.")
            continue
    
        # print and ask for the user to choose a transaction
        print("Found %d transactions. Please choose one:" % tlen)
        for i in range(tlen):
            print("%d. %s" % ((i + 1), ts[i]))
        idx = input_number("Transaction number:", upper=tlen, lower=1) - 1
        return ts[idx]


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
    p.add_argument("--json",
                   help="Prints a JSON representation of all budget classes.",
                   default=False, action="store_true")
    p.add_argument("--add",
                   help="Add a new transaction.",
                   default=False, action="store_true")
    p.add_argument("--remove",
                   help="Remove an existing transaction.",
                   default=False, action="store_true")
    p.add_argument("--edit",
                   help="Edit an existing transaction.",
                   default=False, action="store_true")

    return vars(p.parse_args())


# ============================ Main Functionality ============================ #
# Prints basic information about each budget class to the terminal.
def summarize():
    # get all expense and income classes
    eclasses = api.get_classes(ctype=BudgetClassType.EXPENSE)
    iclasses = api.get_classes(ctype=BudgetClassType.INCOME)

    # Helper function for printing a budget class
    def summarize_budget_class(c, prefix):
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
        ectotal += summarize_budget_class(eclasses[i], pfx)
    
    # process all income classes
    iclen = len(iclasses)
    ictotal = 0.0
    print("%d Income Classes:" % iclen)
    for i in range(iclen):
        pfx = STAB_TREE2 if i < iclen - 1 else STAB_TREE1
        ictotal += summarize_budget_class(iclasses[i], pfx)
    
    # compute and print totals
    net = ictotal - ectotal
    sys.stdout.write("\n")
    print("Total expenses:  %s" % dollar_to_string(ectotal))
    print("Total income:    %s" % dollar_to_string(ictotal))
    print("----")
    print("Net:             %s" % dollar_to_string(net))

# Handles the '--json' option.
def list_json():
    print(json.dumps(api.to_json(), indent=4))

# Prompts the user for information to add a new transaction.
def add_transaction():
    price = input_price()
    if price == None:
        sys.stderr.write("The price must be a positive integer or float.\n")
        sys.exit(1)

    # read the vendor, description, and category as input
    vendor = input_wrapper("Vendor:", blank_ok=True).strip()
    desc = input_wrapper("Description:", blank_ok=True).strip()

    # get the budget class
    bclass = None
    while bclass == None:
        bclass = input_budget_class()
        if bclass == None:
            print("Couldn't find a matching budget class.")
            continue
        # ask the user if this is the class they want
        print("Found class: %s" % bclass)
        if not input_boolean("Is this correct?"):
            bclass = None
            continue

    # add a transaction object to the correct bclass and save it
    t = Transaction(price, vendor=vendor, description=desc)
    api.add_transaction(t, bclass)
    api.save()

# Prompts the user for information to delete an existing transaction.
def remove_transaction():
    # get a transaction as input, then invoke the API to delete the transaction
    # and write out to disk
    t = input_transaction()
    api.delete_transaction(t)
    api.save()

# Handles the '--edit' option.
def edit_transaction():
    t = input_transaction()
    updates = []

    # prompt the user to edit the price
    print("Current price: %s" % dollar_to_string(t.price))
    price = input_price("New price:", blank_ok=True)
    if price != None:
        t.price = price
        updates.append("Price updated to %s." % dollar_to_string(t.price))

    # prompt the user to edit the vendor
    print("Current vendor: %s" % ("(none" if t.vendor == None else t.vendor))
    vendor = input_wrapper("New vendor:", blank_ok=True)
    if vendor != "":
        t.vendor = vendor
        updates.append("Vendor updated to \"%s\"." % t.vendor)
    
    # prompt user to edit the description
    print("Current description: %s" % ("(none)" if t.desc == None else t.desc))
    desc = input_wrapper("New description:", blank_ok=True)
    if desc != "":
        t.desc = desc
        updates.append("Description updated to \"%s\"." % t.desc)
    
    # ask if the user wants to move it to a new class
    if input_boolean("Move to a different class?"):
        bclass_new = input_budget_class()
        bclass_old = t.owner
        # move the transaction between classes
        if api.move_transaction(t, bclass_new):
            updates.append("Moved to a new class: '%s' --> '%s'." %
                           (bclass_old.name, bclass_new.name))
    
    # display updates to the user
    if len(updates) == 0:
        print("\nNo changes made.")
    else:
        print("\nChanges made:")
        ulen = len(updates)
        for i in range(ulen):
            prefix = STAB_TREE1 if i == ulen - 1 else STAB_TREE2
            print("%s%s" % (prefix, updates[i]))
        # save to disk
        api.save()
    
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

    # if '--json' was given, we'll dump json
    if "json" in args and args["json"]:
        list_json()
        sys.exit(0)

    # if '--add' was given, we'll try to add, then exit
    if "add" in args and args["add"]:
        add_transaction()
        sys.exit(0)

    # if '--remove' was given, we'll try to remove, then exit
    if "remove" in args and args["remove"]:
        remove_transaction()
        sys.exit(0)

    # if '--edit' was given, we'll try to edit, then exit
    if "edit" in args and args["edit"]:
        edit_transaction()
        sys.exit(0)

    # if nothing else was provided, we'll print a summary
    summarize()

# =============================== Runner Code ================================ #
if __name__ == "__main__":
    main()


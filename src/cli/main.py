#!/usr/bin/python3
# This module implements a command-line interface for interacting with the Budget
# API to add/remove/view transactions.
#
#   Connor Shugg

# Imports
import sys
import os
import argparse
import json
from datetime import datetime
import shutil
import signal

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
from lib.config import Config
from lib.budget import Budget
from lib.bclass import BudgetClass, BudgetClassType
from lib.transaction import Transaction
from lib.btarget import BudgetTarget, BudgetTargetType

# Globals
config = None
budget = None

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
# Simple SIGINT handler for graceful interruptions.
def sigint_handler(sig, frame):
    abrupt_exit()

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

# Prints a success message.
def success(msg):
    print("%s%s%s" % (C_GREEN, msg, C_RED))

# Exits, optionally printing a message.
def exit(msg=None):
    if msg != None:
        sys.stderr.write("%s\n" % msg)
    sys.exit(0)

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

# Used to convert a float to a percent string.
def percent_to_string(value):
    if value < 0.0:
        return "-%.2f%%" % abs(value * 100.0)
    return "%.2f%%" % (value * 100.0)


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
            assert price >= 0.0
            return price
        except Exception as e:
            print("Please enter a positive float value.")

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
def input_number(prompt, upper=None, lower=None, color=C_YELLOW):
    has_bound = lower != None and upper != None
    while True:
        val = input_wrapper(prompt, color=color).strip()
        try:
            # try to convert to an integer and assert it's in range
            val = int(val)
            assert val >= lower and val <= upper
            return val
        except Exception as e:
            print("Please enter a number%s." %
                  (" between %d and %d" % (lower, upper) if has_bound else ""))

# Prompts the user for a date string. Returns a datetime object.
def input_date(prompt="Timestamp:", blank_ok=False):
    while True:
        text = input_wrapper(prompt, blank_ok=blank_ok)
        if blank_ok and text == None:
            return None
        
        # attempt to parse as YYYY-MM-DD
        try:
            dt = datetime.strptime(text, "%Y-%m-%d")
            return dt
        except Exception as e:
            print("Please enter a date in this format: YYYY-MM-DD")
            continue

# Takes in either "e"/"expense" or "i"/"income" and returns a BudgetClassType
# object depending on what was entered.
def input_class_type(prompt="Class type:", blank_ok=False):
    while True:
        text = input_wrapper(prompt, blank_ok=blank_ok)
        if blank_ok and text == "":
            return None
        text = text.strip().lower()

        # return based on what was given
        if text in "expenses":
            return BudgetClassType.EXPENSE
        elif text in "income":
            return BudgetClassType.INCOME
        # otherwise, print and continue
        print("Please enter either \"expense\" or \"income\".")

# Reads from stdin to get a budget class from the user. If a match isn't found
# then None is returned. Otherwise, the BudgetClass object is returned.
def input_class(prompt="[SEARCH] Budget class:"):
    while True:
        text = input_wrapper(prompt, color=C_CYAN).strip()
        result = budget.search_class(text)
        if not result.success:
            print("Failed: %s" % result.message)
            return None
        classes = result.data
        clen = len(classes)
        # if nothing was found, say so and loop again
        if clen == 0:
            print("Couldn't find anything.")
            continue

        # otherwise we'll have the user pick one out
        print("Found %d budget classes. Please choose one:" % clen)
        for i in range(clen):
            print("%d. %s" % ((i + 1), classes[i]))
        idx = input_number("Class number:", upper=clen, lower=1, color=C_CYAN) - 1
        return classes[idx]

# Reads user input to get a specific transaction.
def input_transaction(prompt="[SEARCH] Transaction:"):
    while True:
        # prompt the user to supply some sort of text to search for a transaction
        text = input_wrapper(prompt, color=C_CYAN)
        # now, invoke the Budget to search for a transaction loop back around if
        # nothing was found
        result = budget.search_transaction(text)
        if not result.success:
            print("Failed: %s" % result.message)
            return None
        ts = result.data
        tlen = len(ts)
        if tlen == 0:
            print("Couldn't find anything.")
            continue
    
        # print and ask for the user to choose a transaction
        print("Found %d transactions. Please choose one:" % tlen)
        for i in range(tlen):
            print("%d. %s" % ((i + 1), ts[i]))
        idx = input_number("Transaction number:", upper=tlen, lower=1, color=C_CYAN) - 1
        return ts[idx]

# Reads user input to create a new BudgetTarget object.
def input_budget_target():
    while True:
        # first, input the target type
        tstr = input_wrapper(prompt="Target type:").lower()
        if tstr not in ["dollar", "percent_income"]:
            print("The target type must be either \"dollar\" or \"percent_income\"")
            continue
        tt = BudgetTargetType.DOLLAR if tstr == "dollar" else BudgetTargetType.PERCENT_INCOME

        # next, input the target value
        tval = input_price(prompt="Target value:")
        if tt == BudgetTargetType.PERCENT_INCOME and (tval < 0.0 or tval > 1.0):
            print("The target percentage value must be between 0.0 and 1.0.")
            continue
        elif tt == BudgetTargetType.DOLLAR and tval < 0.0:
            print("The target dollar value must be greater than zero.")
            continue
        
        # finally, construct the object and return it
        return BudgetTarget(tval, ttype=tt)


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
    p.add_argument("--list",
                   help="Prints a full listing of all budget classes and transactions.",
                   default=False, action="store_true")
    p.add_argument("--backup", metavar="BACKUP_DIR",
                   help="Copies the current configuration file and all associated files to the specified location.",
                   default=None, nargs=1, type=str)
    p.add_argument("--to-excel", metavar="EXCEL_OUTPUT_PATH",
                   help="Converts the budget to an Excel spreadsheet and writes it out to disk.",
                   default=None, nargs=1, type=str)
    # adding options
    p.add_argument("--add-class",
                   help="Add a new budget class.",
                   default=False, action="store_true")
    p.add_argument("--add-transaction",
                   help="Add a new transaction.",
                   default=False, action="store_true")
    # removal options
    p.add_argument("--delete-class",
                   help="Remove an existing budget class.",
                   default=False, action="store_true")
    p.add_argument("--delete-transaction",
                   help="Remove an existing transaction.",
                   default=False, action="store_true")
    # edit options
    p.add_argument("--edit-class",
                   help="Edit an existing budget class.",
                   default=False, action="store_true")
    p.add_argument("--edit-transaction",
                   help="Edit an existing transaction.",
                   default=False, action="store_true")

    return vars(p.parse_args())


# =========================== Listing/Summarizing ============================ #
# Prints basic information about each budget class to the terminal.
def summarize():
    ictotal = 0.0
    ectotal = 0.0

    # Helper function for printing a budget class
    def summarize_budget_class(c, prefix):
        # print the name and description
        color = C_GREEN if c.ctype == BudgetClassType.INCOME else C_YELLOW
        print("%s%s%s%s: %s" % (prefix, color, c.name, C_NONE, c.desc))

        # compute some basic numbers for the class
        stat_total = 0.0
        transactions = c.all()
        for t in transactions:
            stat_total += t.price
        latest = None if len(transactions) == 0 else transactions[0]
            
        # with the class's target, put together a string to print
        c_target_val = None if c.target == None else c.target.get_value(total_income=ictotal)
        c_target_str = ""
        if c_target_val != None:
            # first, come up with an appropriate color depending on the total
            c_target_color = C_YELLOW
            if stat_total < c_target_val:
                c_target_color = C_GREEN if c.ctype == BudgetClassType.EXPENSE else C_RED
            elif stat_total > c_target_val:
                c_target_color = C_RED if c.ctype == BudgetClassType.EXPENSE else C_GREEN
            # create a string formatted with the color and the target value
            c_target_str = " / %s%s%s" % (c_target_color, dollar_to_string(c_target_val), C_NONE)

        # build a list of statistic lines to print
        prefix2 = STAB_TREE3 if prefix == STAB_TREE2 else STAB
        lines = []
        lines.append("Total: %s%s" % (dollar_to_string(stat_total), c_target_str))
        if latest != None:
            lines.append("%d transactions" % len(transactions))
            recur_str = "(%sR%s) " % (C_CYAN, C_NONE) if latest.recurring else ""
            lines.append("Latest: %s%s" % (recur_str, latest))

        # print the line of statistics
        llen = len(lines)
        for i in range(llen):
            prefix3 = STAB_TREE2 if i < llen - 1 else STAB_TREE1
            print("%s%s%s" % (prefix2, prefix3, lines[i]))

        # return the total value for this class
        return stat_total 
    
    # ----------------------------- Runner Code ------------------------------ #
    # get all classes and separate them into expense and income
    classes = budget.all()
    eclasses = []
    iclasses = []
    for c in classes:
        if c.ctype == BudgetClassType.INCOME:
            iclasses.append(c)
        else:
            eclasses.append(c)

    # process all income classes
    iclen = len(iclasses)
    print("%d Income Classes:" % iclen)
    for i in range(iclen):
        pfx = STAB_TREE2 if i < iclen - 1 else STAB_TREE1
        ictotal += summarize_budget_class(iclasses[i], pfx)
    
    # process all expense classes
    eclen = len(eclasses)
    print("%d Expense Classes:" % eclen)
    for i in range(eclen):
        pfx = STAB_TREE2 if i < eclen - 1 else STAB_TREE1
        ectotal += summarize_budget_class(eclasses[i], pfx)
            
    # compute and print totals
    net = ictotal - ectotal
    sys.stdout.write("\n")
    print("Total income:    %s" % dollar_to_string(ictotal))
    print("Total expenses:  %s" % dollar_to_string(ectotal))
    print("----")
    print("Net:             %s" % dollar_to_string(net))

    # print surplus savings
    sslen = len(budget.savings)
    print("\n%d Surplus Savings Categories" % sslen)
    for i in range(sslen):
        pfx = STAB_TREE2 if i < sslen - 1 else STAB_TREE1
        # if we have a positive net value we can do some savings! So we'll print
        # an extra value that shows how much savings should go into each
        # surplus category
        extra = ""
        if net > 0.0:
            save_amount = budget.savings[i].percent * net
            extra = " (%s%s%s)" % (C_GREEN, dollar_to_string(save_amount), C_NONE)
        # print the summary string
        print("%s%s%s%s: %s%s" % (pfx, C_CYAN, budget.savings[i].name,
                                C_NONE, percent_to_string(budget.savings[i].percent),
                                extra))


# Handles the '--list' option.
def list_all():
    # Helper function for listing full budget class details.
    def list_budget_class(c):
        # print the name and description
        color = C_GREEN if c.ctype == BudgetClassType.INCOME else C_YELLOW
        print("%s%s%s: %s" % (color, c.name, C_NONE, c.desc))

        # now iterate through all transactions and print them out
        allts = c.all()
        atlen = len(allts)
        for j in range(atlen):
            prefix = STAB_TREE1 if j == atlen - 1 else STAB_TREE2
            recur_str = "(%sR%s) " % (C_CYAN, C_NONE) if allts[j].recurring else ""
            print("%s%s%s" % (prefix, recur_str, allts[j]))
    
    # get all classes within the budget (separate by type)
    classes = budget.all()
    eclasses = []
    iclasses = []
    for c in classes:
        if c.ctype == BudgetClassType.INCOME:
            iclasses.append(c)
        else:
            eclasses.append(c)
    allclasses = eclasses + iclasses
    alen = len(allclasses)

    # for each expense class, list it
    for i in range(alen):
        list_budget_class(allclasses[i])

# Handles the '--json' option.
def list_json():
    print(json.dumps(budget.to_json(), indent=4))


# ================================== Adding ================================== #
# Handles '--add-class'.
def add_class():
    # prompt the user for a few things: name, type, description, and keywords
    ctype = input_class_type()
    name = input_wrapper("Class name:").strip()
    desc = input_wrapper("Class description:").strip()
    words = input_wrapper("Class key words:").strip().lower().split()
    
    # if the user wants to, we'll add a target value to this class
    bt = None
    if input_boolean(prompt="Add a target?"):
        bt = input_budget_target()
    
    # construct a budget class and add it to the budget
    bc = BudgetClass(name, ctype, desc, keywords=words, target=bt)
    result = budget.add_class(bc)
    if not result.success:
        print("Failed to add a new class: %s" % result.message)
        return
    success("Budget class added.")

# Handles '--add-transaction'.
def add_transaction():
    # make sure we actually have budget classes first
    if len(budget.all()) == 0:
        exit(msg="You have no budget classes.")

    # get the price as input from the user
    price = input_price()
    if price == None:
        exit(msg="The price must be a positive integer or float.")

    # read the vendor, description, and budget class
    vendor = input_wrapper("Vendor:", blank_ok=True).strip()
    desc = input_wrapper("Description:", blank_ok=True).strip()
    bclass = input_class()
    if bclass == None:
        print("Failed to find a budget class.")
        return
    
    # get the datetime on which the transaction occurred
    ts = input_date("Timestamp (skip to use *now* as the timestamp):", blank_ok=True)
    if ts == None:
        ts = datetime.now()

    # ask if it's a recurring transaction
    recur = input_boolean("Recurring?")

    # add a transaction object to the correct bclass and save it
    t = Transaction(price, vendor=vendor, description=desc, timestamp=ts, recur=recur)
    result = budget.add_transaction(bclass, t)
    if not result.success:
        print("Failed to add a new transaction: %s" % result.message)
        return
    success("Transaction added.")


# ================================= Deletion ================================= #
# Handles '--delete-class'.
def delete_class():
    # make sure we actually have budget classes first
    if len(budget.all()) == 0:
        exit(msg="You have no budget classes.")

    # get the class from input, then try to delete
    bclass = input_class()
    if bclass == None:
        print("Failed to find a budget class.")
        return
    result = budget.delete_class(bclass)
    if not result.success:
        print("Failed to delete the specified class: %s" % result.message)
        return
    success("Budget class deleted.")
    
# Prompts the user for information to delete an existing transaction.
def delete_transaction():
    # get the transaction from input, then try to delete
    t = input_transaction()
    if t == None:
        print("Failed to find a transaction.")
        return
    result = budget.delete_transaction(t)
    if not result.success:
        print("Failed to delete the specified transaction: %s" % result.message)
        return
    success("Transaction deleted.")


# ================================= Updates ================================== #
def edit_class():
    # make sure we actually have budget classes first
    if len(budget.all()) == 0:
        exit(msg="You have no budget classes.")
    
    # get the class from input and make a shallow copy
    bc = input_class()
    if bc == None:
        print("Failed to find a budget class.")
        return
    bc = bc.copy()
    updates = []

    # prompt to enter a new type
    tstr = "income" if bc.ctype == BudgetClassType.INCOME else "expense"
    print("Current type: %s" % tstr)
    ctype = input_class_type("New type:", blank_ok=True)
    if ctype != None:
        bc.ctype = ctype
        tstr = "income" if bc.ctype == BudgetClassType.INCOME else "expense"
        updates.append("Type updated to %s." % tstr)

    # prompt to enter a new name
    print("Current name: %s" % bc.name)
    name = input_wrapper("New name:", blank_ok=True)
    if name != "":
        bc.name = name.strip()
        updates.append("Name updated to \"%s\"." % bc.name)

    # prompt to enter a new description
    print("Current description: %s" % bc.desc)
    desc = input_wrapper("New description:", blank_ok=True)
    if desc != "":
        bc.desc = desc.strip()
        updates.append("Description updated to \"%s\"." % bc.desc)

    # print all keywords in a nice format, then prompt the user for new keywords
    sys.stdout.write("Current keywords: ")
    for word in bc.keywords:
        sys.stdout.write("%s " % word)
    sys.stdout.write("\n")
    words = input_wrapper("New key words:", blank_ok=True)
    if words != "":
        bc.keywords = words.strip().lower().split()
        # create a nicely-formatted update string to print later
        ustr = "Keywords updated to: "
        for w in bc.keywords:
            ustr += "\"%s\" " % w
        updates.append(ustr)
    
    # prompt to update the target
    if input_boolean(prompt="Update the target?"):
        bc.target = input_budget_target()
        updates.append("Updated target.")
    elif input_boolean(prompt="Delete the target?"):
        bc.target = None
        updates.append("Deleted the target.")

    # update the budget backend
    result = budget.update_class(bc)
    if not result.success:
        print("Failed to update the class: %s" % result.message)
        return

    # if no updates were made, print and return
    if len(updates) == 0:
        print("No changes made.")
        return

    # otherwise, we'll print all updates
    for u in updates:
        success(u)


# Handles the '--edit' option.
def edit_transaction():
    t = input_transaction()
    if t == None:
        print("Failed to find a transaction.")
        return
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

    # prompt user to edit the timestamp
    print("Current timestamp: %s" % t.to_date_string())
    ts = input_date("New timestamp:", blank_ok=True)
    if ts != None:
        t.timestamp = ts
        updates.append("Timestamp updated to %s." % t.to_date_string())
    
    # ask if the user wants to move it to a new class
    owner = t.owner
    if input_boolean("Move to a different class?"):
        owner = input_class()
        if owner == None:
            print("Failed to find a budget class.")
            return
        updates.append("Moved to a new class: '%s' --> '%s'." %
                           (t.owner.name, owner.name))

    # invoke the API to remove the transaction then re-add it
    result = budget.delete_transaction(t)
    if not result.success:
        print("Failed to update the transaction (delete): %s" % result.message)
        return
    result = budget.add_transaction(owner, t)
    if not result.success:
        print("Failed to update the transaction (add): %s" % result.message)
        return
    
    # if no updates were made, say so and return
    if len(updates) == 0:
        print("No changes made.")
        return
    
    # otherwise, print all updates
    for u in updates:
        success(u)


# ============================== Backup/File IO ============================== #
# Takes in a directory path and copies the given configuration file and all
# associated files to the given backup path. If the directory needs to be
# created, it is done within this function.
def backup_budget(bpath):
    # make sure the given path isn't to a file
    if os.path.isfile(bpath):
        exit(msg="The given backup path points to a file, not a directory.")

    # if the path isn't a directory, we'll create it now
    if not os.path.isdir(bpath):
        os.mkdir(bpath)

    # take a quick glance inside the directory. If there are files and dirs
    # stored within, we don't want to risk overwriting anything.
    for root, dirs, files in os.walk(bpath):
        if len(dirs) > 0 or len(files) > 0:
            exit(msg="The given backup path already contains files. "
                        "Please choose another.")

    # finally, we're ready to copy files over. We'll start by copying over the
    # configuration file
    shutil.copyfile(config.fpath, os.path.join(bpath, "config.json"))

    # now, we'll copy every file within the budget's save directory into the
    # backup directory
    shutil.copytree(config.save_location, os.path.join(bpath, "budget"))
    success("Successfully copied budget.")

# Handles the '--to-excel' option.
def save_to_excel(epath):
    # invoke the budget's internal function and call it a day
    budget.write_to_excel(epath)
    success("Wrote Excel workbook to: %s" % epath)


# ============================ Main Functionality ============================ #
# Main function.
def main():
    # install the SIGINT handler
    signal.signal(signal.SIGINT, sigint_handler)

    # parse the arguments, then parse the config file
    args = parse_args()
    global config
    try:
        config = Config(args["config"][0])
    except Exception as e:
        fatality(msg="failed to initialize config", exception=e)

    # now, initialize a Budget object
    global budget
    try:
        budget = Budget(config)
    except Exception as e:
        fatality(msg="failed to initialize budget", exception=e)

    # if '--json' was given, we'll dump json
    if "json" in args and args["json"]:
        list_json()
        exit()

    # if '--list' was given, we'll write out a full list
    if "list" in args and args["list"]:
        list_all()
        exit()
    
    # if a backup path was given, we'll try to copy all files
    if "backup" in args and args["backup"] != None:
        backup_budget(args["backup"][0])
        exit()

    # if an excel path is specified, we'll try to convert, then exit
    if "to_excel" in args and args["to_excel"] != None:
        save_to_excel(args["to_excel"][0])
        exit()

    # if '--add-class' was given, we'll try to add, then exit
    if "add_class" in args and args["add_class"]:
        add_class()
        exit()

    # if '--add-transaction' was given, we'll try to add, then exit
    if "add_transaction" in args and args["add_transaction"]:
        add_transaction()
        exit()

    # if '--delete-class' was given, we'll try to remove, then exit
    if "delete_class" in args and args["delete_class"]:
        delete_class()
        exit()

    # if '--delete-transaction' was given, we'll try to remove, then exit
    if "delete_transaction" in args and args["delete_transaction"]:
        delete_transaction()
        exit()

    # if '--edit-class' was given, we'll try to edit, then exit
    if "edit_class" in args and args["edit_class"]:
        edit_class()
        exit()

    # if '--edit-class' was given, we'll try to edit, then exit
    if "edit_transaction" in args and args["edit_transaction"]:
        edit_transaction()
        exit()

    # if nothing else was provided, we'll print a summary
    summarize()

# =============================== Runner Code ================================ #
if __name__ == "__main__":
    main()


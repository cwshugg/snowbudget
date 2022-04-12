# Simple logging module for the server.
#
#   Connor Shugg

# Imports
import sys

# Globals
log_prefix = "sbserv"

# Initializes the global server log.
def log_init(prefix):
    global log_prefix
    log_prefix = prefix

# Takes in a message and writes to the log.
def log_write(message):
        sys.stdout.write("[%s] %s\n" % (log_prefix, message))


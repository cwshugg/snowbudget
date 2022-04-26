#!/usr/bin/python3
# Super small main file that invokes 'app.run()' to run the server.
#
#   Connor Shugg

# Imports
import os
import sys
import threading
import time
import signal

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
from server.app import app
from server.auth import auth_init
from server.config import Config
from server.log import log_init, log_write
from server.notif import notif_init, notif_send_email
import lib.config
from lib.budget import Budget

# Colors and pretty-printing
C_NONE = "\033[0m"
C_LOG = "\033[36m"

# Other globals
rthread = None


# ================================= Helpers ================================== #
# Simple SIGINT handler.
def sigint_handler(sig, frame):
    # join the renewer thread
    log_write("\nSIGINT detected. Joining renewer thread.")
    global rthread
    with rthread.cond:          # acquire condition variable lock
        rthread.kill = True     # set kill switch
        rthread.cond.notify()   # wake up the thread
    rthread.join()              # join thread
    
    # exit
    log_write("Exiting.")
    sys.exit(0)


# ============================== Renewer Thread ============================== #
# The renewer thread is spawned simply to refresh the budget periodically to
# make sure it doesn't miss important dates (such as reset dates). It's also
# used to notify users of certain periodic events.
class RenewerThread(threading.Thread):
    # Constructor. Takes in the server's config object.
    def __init__(self, conf, tick_rate=43200, notif_threshold=172800):
        self.conf = conf
        self.tick_rate = tick_rate          # rate at which thread renews
        self.notif_threshold = notif_threshold # time after which notifs occur

        # set up synchronization fields
        self.kill = False                   # master thread kill switch
        self.cond = threading.Condition()   # condition variable

        # invoke the parent constructor
        threading.Thread.__init__(self, target=self.run)

    # Used to notify all users via email.
    def notify_users(self, message, subject):
        for user in self.conf.users:
            notif_send_email(user.email, message, subject)
            log_write("Notified user '%s': '%s'" % (user.username, message))

    # Main runner function for the thread.
    def run(self):
        log_write("Renewer thread spawned.")

        # enter the main loop
        while True:
            # check the kill switch
            with self.cond:
                if self.kill:
                    break

            # get a new configuration and budget object
            conf = lib.config.Config(self.conf.sb_config_fpath)
            b = Budget(conf)
            
            # compute the time-to-reset
            ttr = b.time_to_reset()
            log_write("Renewer thread tick. [ttr: %d]" % ttr)

            # if the time-to-reset is less than our threshold, notify all users
            if ttr < self.notif_threshold:
                subject = "[savings]"
                # compute the number of days/hours/minutes until the reset
                rdays = int(float(ttr) / 86400.0)
                rhours = int(float(ttr - (rdays * 86400)) / 3600.0)
                rmins = int(float(ttr - (rdays * 86400) - (rhours * 3600)) / 60.0)
                # create the final message and send the emails
                msg = "Reset occurring in %d days, %d hours, %d minutes. Check savings." % \
                        (rdays, rhours, rmins)
                self.notify_users(msg, subject)

            # go to sleep and wait for the next tick
            with self.cond:
                self.cond.wait(timeout=self.tick_rate)
        
        log_write("Renewer thread exiting.")


# ============================== Server Startup ============================== #
# Main function
def main():
    # expect the first argument to be a config file path
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: %s /path/to/server-config.json\n" % sys.argv[0])
        sys.exit(0)

    # initialize any needed functionality
    config = Config(sys.argv[1])
    app.config["server_config_obj"] = config
    app.secret_key = config.server_secret_key
    log_init("%ssbserv%s" % (C_LOG, C_NONE))
    auth_init(config)
    notif_init(config)

    # set up the SIGINT handler
    signal.signal(signal.SIGINT, sigint_handler)

    # create the renwer thread
    global rthread
    rt = RenewerThread(config,
                       tick_rate=config.rthread_tick_rate,
                       notif_threshold=config.rthread_notif_threshold)
    rthread = rt
    rt.start()

    # run the flask app, with or without HTTPS
    if config.certs_enabled:
        app.run(config.server_addr, port=config.server_port,
                ssl_context=(os.path.join(config.certs_dpath, config.certs_cert_fname),
                             os.path.join(config.certs_dpath, config.certs_key_fname)))
    else:
        app.run(config.server_addr, port=config.server_port)

# Runner code
if (__name__ == "__main__"):
    main()


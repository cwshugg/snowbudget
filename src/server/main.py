#!/usr/bin/python3
# Super small main file that invokes 'app.run()' to run the server.
#
#   Connor Shugg

# Imports
import os
import sys

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
from server.app import app
from server.auth import auth_init
from server.config import Config
from server.log import log_init
from server.notif import notif_init

# Colors and pretty-printing
C_NONE = "\033[0m"
C_LOG = "\033[36m"

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


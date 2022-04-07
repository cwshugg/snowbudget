# Module that allows the flask app to reference an instance of the budget API.
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
from lib.config import Config
from lib.api import API
import server.config as config

# Globals
sb_config = None
sb_api = None
 
# Retrieves a new (or existing) API instance.
def backend_get_api():
    # if the globals aren't set, we'll create new objects
    global sb_config, sb_api
    if sb_config == None or sb_api == None:
        # get a path to the server config's snowbudget configuration file and
        # initialize the Config instance
        sb_config = Config(config.sb_config_fpath)
        sb_config.parse()
    
        # pass the config into a new API object
        sb_api = API(sb_config)
        return sb_api

    # otherwise, return the existing API object
    return sb_api


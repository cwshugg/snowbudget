# Python module responsible for handling user authentication.
#
#   Connor Shugg

# Imports
import json
import jwt
from datetime import datetime
import os
import sys

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
from server.log import log_write

# Globals
config = None
auth_password = None            # authentication password
auth_secret = None              # JWT decode/encode key
auth_cookie_name = "sb_auth"    # name of cookie


# ============================= Helper Functions ============================= #
# Takes in a file path and opens it up, returning its contents.
def read_file(fpath):
    fp = open(fpath)
    contents = fp.read()
    fp.close()
    return contents

# ============================== Initialization ============================== #
# Initialization function for authentication functionality.
def auth_init(conf):
    global config
    config = conf
    # retrieve the correct config entries
    global auth_password, auth_secret
    auth_password = conf.auth_key
    auth_secret = conf.auth_jwt_key

    log_write("Authentication password:   '%s'" % auth_password)
    log_write("JWT password:              '%s'" % auth_secret)

# ========================= Authentication Checking ========================= #
# Checks a login attempt and returns the User object corresponding to the
# user the just logged in. Returns None if the login failed.
def auth_check_login(data):
    data = data.decode()
    # attempt to decode the data
    try:
        result = json.loads(data)
        
        # check for the correct field in the JSON structure
        key = "password"
        if key not in result:
            return None
        # check the field's value against the known password and return
        # accordingly
        global auth_password
        if result[key] != auth_password:
            return None

        # the password matches, so we'll return the username
        if "username" not in result:
            return None

        # make sure the username is in our database
        for u in config.users:
            if result["username"] == u.username:
                log_write("User \"%s\" logged in." % u.username)
                return u
        # if no matching user was found, return
        return None
    # on exception, print and return
    except Exception as e:
        log_write("Failed to parse JSON contents: %s" % e)
        return None

# Checks for a specific cookie as proof of authentication. Returns the User
# object representing the user that's making the request.
def auth_check_cookie(cookie):
    if cookie == None:
        return None
    
    # split into individual cookies
    cookies = cookie.split(";")
    result = None
    for c in cookies:
        c = c.strip()
        # attempt to separate out the cookie value and decode it
        pieces = c.split("=")
        # check the cookie name - if this is the one we want, break out of the
        # loop and proceed
        if pieces[0] == auth_cookie_name:
            result = auth_parse_cookie(pieces[len(pieces) - 1])
    
    # if parsing failed, or we never found the cookie, return
    if result == None:
        return None

    # check for the correct fields in the decoded JWT
    if "iat" not in result or "exp" not in result or "sub" not in result:
        return None
    # check the issued-at time for the token
    now = int(datetime.now().timestamp())
    if result["iat"] > now:
        return None
    # make sure the 'sub' is one of our registered users
    user = None
    for u in config.users:
        if result["sub"] == u.username:
            user = u
            break
    if user == None:
        return None

    # check the expiration time for the token, but only if the user doesn't
    # have special privileges
    if user.privilege > 0 and result["exp"] <= now:
        return None
    
    # if we passed all the above checks, they must be authenticated
    return user


# ================================ JWT Work ================================= #
# Creates an encoded JWT cookie and returns it.
def auth_make_cookie(user):
    global auth_secret
    # get the current datetime and compute an expiration time for the cookie
    now = int(datetime.now().timestamp())
    data = {"iat": now, "exp": now + 2592000, "sub": user.username}
    token = jwt.encode(data, auth_secret, algorithm="HS512").decode("utf-8")
    return token

def auth_parse_cookie(cookie):
    global auth_secret
    try:
        # we won't verify the expiration here - we do this manually
        return jwt.decode(cookie, auth_secret, algorithms=["HS512"],
                          options={"verify_exp": False})
    except Exception as e:
        return None


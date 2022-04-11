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

# Globals
config = None
auth_password = None            # authentication password
auth_secret = None              # JWT decode/encode key
auth_special_user = None        # special user with no cookie expiration
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
    # attempt to read the password key file
    global auth_password
    auth_password_fpath = os.path.join(config.key_dpath, config.auth_key_fname)
    auth_password = read_file(auth_password_fpath)
    
    # attempt to read the JWT encryption key file
    global auth_secret
    auth_secret_fpath = os.path.join(config.key_dpath, config.auth_jwt_key_fname)
    auth_secret = read_file(auth_secret_fpath)

    # attempt to read our special username
    global auth_special_user
    auth_special_user_fpath = os.path.join(config.key_dpath, config.auth_special_user_fname)
    auth_special_user = read_file(auth_special_user_fpath)
    
    print("Authentication password:   '%s'" % auth_password)
    print("JWT password:              '%s'" % auth_secret)
    print("Special User:              '%s'" % auth_special_user)

# ========================= Authentication Checking ========================= #
# Checks a login attempt and returns a username. Returns None if the login
# failed.
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
        return result["username"]
    # on exception, print and return
    except Exception as e:
        print("Failed to parse JSON contents: %s" % e)
        return None

# Checks for a specific cookie as proof of authentication.
def auth_check_cookie(cookie):
    if cookie == None:
        return False
    
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
        return False

    # check for the correct fields in the decoded JWT
    if "iat" not in result or "exp" not in result or "sub" not in result:
        return False
    # check the issued-at time for the token
    now = int(datetime.now().timestamp())
    if result["iat"] > now:
        return False
    # check the expiration time for the token, but only if the username isn't
    # our "special" username (if you're looking at this code online, don't try
    # figuring it out, it's *incredibly* long. Plus, you need the password too,
    # which is also crazy-long.)
    if result["sub"] != auth_special_user and result["exp"] <= now:
        return False

    if result["sub"] == auth_special_user:
        print("Special user is making a request.")

    # if we passed all the above checks, they must be authenticated
    return True


# ================================ JWT Work ================================= #
# Creates an encoded JWT cookie and returns it.
def auth_make_cookie(username):
    global auth_secret
    # get the current datetime and compute an expiration time for the cookie
    now = int(datetime.now().timestamp())
    data = {"iat": now, "exp": now + 2592000, "sub": username}
    token = jwt.encode(data, auth_secret, algorithm="HS512").decode("utf-8")
    return token

def auth_parse_cookie(cookie):
    global auth_secret
    try:
        return jwt.decode(cookie, auth_secret, algorithms=["HS512"])
    except Exception as e:
        return None


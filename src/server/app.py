# Main module for the snowbudget flask server.
# A few links:
#   - Flask quickstart: https://pypi.org/project/Flask/
#   - Deploying to production: https://flask.palletsprojects.com/en/2.0.x/tutorial/deploy/
#   - Allowed requests: https://pythonbasics.org/flask-http-methods/
#   - Flas requests: https://flask.palletsprojects.com/en/2.0.x/quickstart/#accessing-request-data
#
#   Connor Shugg

# Includes and Flask setup
from flask import Flask, request, Response, send_from_directory, session
import csv
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
from server.auth import auth_check_login, auth_make_cookie, auth_check_cookie, \
                        auth_cookie_name
from server.log import log_write
from server.users import User
from server.notif import notif_send_email
from lib.config import Config
from lib.budget import Budget
from lib.bclass import BudgetClass, BudgetClassType
from lib.transaction import Transaction

# Flask setup
app = Flask(__name__)
config = None   # main server config

# ============================= Helper Functions ============================= #
# Used to retrieve a fresh Budget object from the configuration path stored in
# the server's config module.
def get_budget():
    conf = Config(config.sb_config_fpath)
    return Budget(conf)

# Takes a dictionary of data and adds an optional message to it, then packs it
# all into a Flask Response object.
def make_response_json(jdata={}, msg="", success=True, rstatus=200, rheaders={}):
    # if the message isn't set, come up with a default one based on the status
    if msg == "":
        if rstatus == 404:
            msg = "File not found."
        elif rstatus == 400:
            msg = "Bad request."

    # the given JSON data will become our "payload". Put together a wrapper
    # JSON object to contain the message and success indicator
    alldata = {"message": msg}
    if rstatus == 200:
        alldata["success"] = success
    if jdata != {}:
        alldata["payload"] = jdata
    resp = Response(response=json.dumps(alldata), status=rstatus)
    
    # store the JSON data in the session for post-processing
    session["response_jdata"] = alldata
    
    # set all given headers, as well as the content type
    for key in rheaders:
        resp.headers[key] = rheaders[key]
    resp.headers["Content-Type"] = "application/json"
    # return given completed response
    return resp

# Takes in a request's URL arguments and attempts to find an entry with the
# given key value. Returns None on failure to find and the value on success.
def get_url_parameter(args, key):
    p = args.get(key, "")
    if (p == ""):
        return None
    return p

# Returns true if all key-type pairs are present in the given JSON data.
# Returns false otherwise.
def check_json_fields(jdata, expects):
    for e in expects:
        if e[0] not in jdata or type(jdata[e[0]]) != e[1]:
            return False
    return True

# Returns request JSON data, None if none was provided, or an Exception if
# something went wrong trying to parse the data.
def parse_request_json(request):
    try:
        rdata = request.get_data()
        if len(rdata) == 0:
            return None
        return json.loads(rdata.decode())
    except Exception as e:
        return Exception("FAILURE: %s" % e)

# References the pre-processed session field.
def get_request_json():
    return session["jdata"]

# Takes in a file path local to the server's root directory and appends it to
# the path tot he root directory before passing it into send_file()
def serve_file(fpath):
    return send_from_directory(config.server_root_dpath, fpath, etag=False)

# Takes in the given session and retrieves the user object. Returns None if one
# isn't found or valid.
def get_user(ses):
    if "user" in ses:
        return User.from_json(ses["user"])
    return None

# =============================== Notification =============================== #
# Searches through the JSON data and determines if a special "notify" field is
# set to 'true'. If so, this function returns true and sets the the correct
# field in in the given session.
def update_notify(session, jdata):
    should_notify = "notify" in jdata and jdata["notify"]
    session["user_notify"] = should_notify
    return should_notify

# Returns true if the session's notify field is set to true.
def check_notify(session):
    return "user_notify" in session and session["user_notify"]


# ============================== Pre-Processing ============================== #
@app.before_first_request
def server_init():
    # retrieve the config from the app's config and set up the log
    global config
    config = app.config["server_config_obj"]

# Invoked before an endpoint handler is called.
# Resource: https://pythonise.com/series/learning-flask/python-before-after-request
@app.before_request
def pre_process():
    pass
    # extract JSON data, if any
    jdata = parse_request_json(request)
    session["jdata"] = jdata
    
    # check for authentication
    user = auth_check_cookie(request.headers.get("Cookie"))
    session["user"] = None if user == None else user.to_json()
    if user != None:
        log_write("User \"%s\" is making a request (privilege: %d)." %
                  (user.username, user.privilege))

    # initialize the "notify" field
    if jdata != None:
        update_notify(session, session["jdata"])


# ============================= Post-Processing ============================== #
# Used to post-process successful requests.
@app.after_request
def post_process(response):
    jdata = None
    if "response_jdata" in session:
        jdata = session["response_jdata"]
    #print(type(jdata))

    if check_notify(session):
        user = get_user(session)
        # retrieve response JSON data and build a message string
        msg = "Handled a request."
        if jdata != None:
            msg = ""
            if "success" in jdata:
                msg += "[%s] " % ("success" if jdata["success"] else "failure")
            if "message" in jdata:
                msg += "%s" % jdata["message"]
        # send the notification
        log_write("Notification requested. Sending message \"%s\" to %s." % (msg, user.email))
        notif_send_email(user.email, msg)
    return response

# Used to post-process failed requests. (Typically triggered when an exception
# is thrown.)
@app.teardown_request
def post_process_error(error=None):
    if error != None:
        log_write("ERROR: %s" % error)


# ==================== Root and Authentication Endpoints ===================== #
# Defines the behavior of the root '/' endpoint. Returns a simple status/hello
# message to the client.
@app.route("/")
def endpoint_root():
    user = get_user(session)
    # if the user is authenticated, we'll serve them the authenticated home
    # page. If not, we'll serve them the public one
    if user != None:
        return serve_file(config.server_home_auth_fname)
    return serve_file(config.server_home_fname)

# Static file handling.
@app.route("/<path:fpath>")
def endpoint_static_file(fpath):
    user = get_user(session)
    is_auth = user != None
    # special case: if index.html was requested, check authentication and
    # replace it with the authenticated version
    if fpath == config.server_home_fname and is_auth:
        fpath = config.server_home_auth_fname

    # if the path is one of our public files, serve it without question
    if fpath in config.server_public_files:
        return serve_file(fpath)

    # otherwise, check authentication before serving the file
    if not is_auth:
        return make_response_json(rstatus=404)
    return serve_file(fpath)

# Used to attempt a login.
@app.route("/auth/login", methods=["POST"])
def endpoint_auth_login():
    # attempt to parse the login data and verify the login attempt
    username = auth_check_login(request.get_data())
    if username != None:
        # create a cookie, add it as a response header, and return
        cookie = auth_make_cookie(username)
        cookie_str = "%s=%s; Path=/" % (auth_cookie_name, cookie)
        # if HTTPS is enabled, add the 'Secure' flag to the cookie
        if config.certs_enabled:
            cookie_str += "; Secure"
        # build a response and send the cookie back
        return make_response_json(msg="Authentication succeeded. Hello, %s." % username,
                                  rheaders={"Set-Cookie": cookie_str})
    else:
        return make_response_json(success=False, msg="Authentication failed.")

# Authentication-checking endpoint.
@app.route("/auth/check", methods=["GET"])
def endpoint_auth_check():
    # look for the correct cookie
    auth = auth_check_cookie(request.headers.get("Cookie"))
    if auth:
        return make_response_json(msg="You are authenticated.")
    else:
        return make_response_json(msg="You are not authenticated.")


# ================================ Retrieval ================================= #
# Used to retrieve ALL budget classes.
@app.route("/get/all", methods = ["GET"])
def endpoint_get_all():
    user = get_user(session)
    if user == None:
        return make_response_json(rstatus=404)

    # invoke the API to retrieve *all* budget classes as a combined JSON object
    b = get_budget()
    classes = b.to_json()
    return make_response_json(jdata=classes)

# Helper function for the /get methods that takes in the ID field to expect in
# the JSON request body.
def get_helper(field):
    user = get_user(session)
    if user == None:
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json()
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # make sure the correct entry is present in the JSON field
    expect = [[field, str]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")
    
    # invoke the API to search for a matching class 
    b = get_budget()
    result = None
    if field == "class_id":
        result = b.get_class(jdata[field])
    elif field == "transaction_id":
        result = b.get_transaction(jdata[field])

    # if the search failed, return a message. Otherwise, convert the object to
    # JSON and return it
    if result == None:
        return make_response_json(success=False, msg="Couldn't find a match.")
    return make_response_json(jdata=result.to_json())

# Used to retrieve a budget class. Expects a class ID.
@app.route("/get/class", methods = ["POST"])
def endpoint_get_class():
    return get_helper("class_id")

# Used to retrieve a transaction. Expects a transaction ID.
@app.route("/get/transaction", methods = ["POST"])
def endpoint_get_transaction():
    return get_helper("transaction_id")


# ================================== Search ================================== #
# Helper function used for the searcher endpoints. Takes in the 'mode' to
# search on ("class" or "transaction")
def search_helper(mode):
    user = get_user(session)
    if user == None:
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json()
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # make sure the correct entry is present in the JSON field
    expect = [["query", str]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")
    
    # invoke the budget API to search for classes
    b = get_budget()
    matches = []
    mode = mode.lower()
    if mode == "class":
        matches = b.search_class(jdata["query"])
    elif mode == "transaction":
        matches = b.search_transaction(jdata["query"])

    # if the search failed, return an appropriate message
    if len(matches) == 0:
        return make_response_json(success=False,
                                  msg="Couldn't find any matches.")

    # build a JSON array of all matches
    jarray = []
    for c in matches:
        jarray.append(c.to_json())
    return make_response_json(jdata=jarray)
   
# Takes in some string as input and uses it to search for matching budget
# classes.
@app.route("/search/class", methods = ["POST"])
def endpoint_search_class():
    return search_helper("class")

# Takes in some string as input and uses it to search for matching transactions.
@app.route("/search/transaction", methods = ["POST"])
def endpoint_search_transaction():
    return search_helper("transaction")


# ================================= Creation ================================= #
# Used to create a new budget class.
@app.route("/create/class", methods = ["POST"])
def endpoint_create_class():
    user = get_user(session)
    if user == None:
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json()
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # we're expecting information on the new budget class - check it here
    expect = [["name", str], ["type", str], ["description", str],
              ["keywords", list]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")

    # attempt to parse the type string into an enum
    tstr = jdata["type"].lower()
    ctype = None
    if tstr in ["e", "expense", "expenses"]:
        ctype = BudgetClassType.EXPENSE
    elif tstr in ["i", "income"]:
        ctype = BudgetClassType.INCOME
    else:
        return make_response_json(success=False, msg="Invalid JSON fields.")

    # from the keyword list, convert to a list of strings (just in case the
    # sender sent a list of not-strings)
    kws = []
    for w in jdata["keywords"]:
        kws.append(str(w))
    
    # create a new budget class object and attempt to add it to the budget
    bclass = BudgetClass(jdata["name"], ctype, jdata["description"], keywords=kws)
    b = get_budget()
    try:
        b.add_class(bclass)
        return make_response_json(msg="Class created.", jdata=bclass.to_json())
    except Exception as e:
        return make_response_json(success=False,
                                     msg="Failed to create the class: %s" % e)

# Used to create a new transaction.
@app.route("/create/transaction", methods = ["POST"])
def endpoint_create_transaction():
    user = get_user(session)
    if user == None:
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json()
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # we're expecting a class ID *and* other fields within the JSON data
    expect = [["class_id", str], ["price", float], ["vendor", str],
              ["description", str], ["timestamp", int]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")

    # first, search for the class, given its ID (make a shallow copy)
    b = get_budget()
    bclass = b.get_class(jdata["class_id"])
    if bclass == None:
        return make_response_json(success=False,
                                  msg="Couldn't find the specified class.")

    # try to convert the given timestamp integer into a datetime object
    ts = None
    try:
        ts = datetime.fromtimestamp(jdata["timestamp"])
    except Exception as e:
        return make_response_json(success=False, msg="Invalid JSON fields.")

    # create a transaction struct and pass it to the API
    t = Transaction(jdata["price"], vendor=jdata["vendor"],
                    description=jdata["description"], timestamp=ts)
    b.add_transaction(bclass, t)
    return make_response_json(msg="Transaction created.", jdata=t.to_json())

# This endpoint allows a query for a budget class to be specified rather than a
# class ID itself. This searches for a class and adds a new transaction to it.
# A message is sent back if a matching class can't be found.
@app.route("/create/transaction/search", methods = ["POST"])
def endpoint_create_transaction_search():
    user = get_user(session)
    if user == None:
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json()
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # we're expecting a class query *and* other fields within the JSON data
    expect = [["query", str], ["price", float], ["vendor", str],
              ["description", str], ["timestamp", int]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")

    # first, search for the class, given its ID (make a shallow copy)
    b = get_budget()
    matches = b.search_class(jdata["query"])
    if len(matches) == 0:
        return make_response_json(success=False,
                                  msg="Couldn't find any matching classes.")
    # otherwise, we'll just take the first one
    bclass = matches[0]

    # try to convert the given timestamp integer into a datetime object
    ts = None
    try:
        ts = datetime.fromtimestamp(jdata["timestamp"])
    except Exception as e:
        raise e
        return make_response_json(success=False, msg="Invalid JSON fields.")

    # create a transaction struct and pass it to the API
    t = Transaction(jdata["price"], vendor=jdata["vendor"],
                    description=jdata["description"], timestamp=ts)
    b.add_transaction(bclass, t)
    return make_response_json(msg="Transaction created. Added to class: \"%s\"." % bclass.name,
                              jdata=t.to_json())


# ================================= Deletion ================================= #
# Helper function for the two delete endpoints.
def delete_helper(field):
    user = get_user(session)
    if user == None:
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json()
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # pass in the field as the expected ID
    expect = [[field, str]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")
    
    # search for the corresponding object with the given ID
    b = get_budget()
    result = None
    if field == "class_id":
        result = b.get_class(jdata[field])
    elif field == "transaction_id":
        result = b.get_transaction(jdata[field])

    # if the search failed, return a message
    if result == None:
        return make_response_json(success=False,
                                  msg="Couldn't find a match.")
    
    # attempt to delete the object
    if field == "class_id":
        b.delete_class(result)
    elif field == "transaction_id":
        b.delete_transaction(result)
    
    # return an appropriate message
    msg = "Deleted."
    if field == "class_id":
        msg = "Class deleted."
    elif field == "transaction_id":
        msg = "Transaction deleted."
    return make_response_json(msg=msg)

# Used to delete a class.
@app.route("/delete/class", methods = ["POST"])
def endpoint_delete_class():
    return delete_helper("class_id")

# Used to delete a transaction.
@app.route("/delete/transaction", methods = ["POST"])
def endpoint_delete_transaction():
    return delete_helper("transaction_id")


# ================================= Updates ================================== #
# Used to edit an existing budget class.
@app.route("/edit/class", methods = ["POST"])
def endpoint_edit_class():
    user = get_user(session)
    if user == None:
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json()
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # we're expecting a class ID
    expect = [["class_id", str]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")

    # search for the transaction
    b = get_budget()
    bc = b.get_class(jdata["class_id"]).copy()
    if bc == None:
        return make_response_json(success=False,
                                  msg="Couldn't find a matching class.")

    # we'll look for the following fields in the JSON data to use as updates
    expect = [["name", str], ["type", str], ["description", str],
              ["keywords", list]]
    for e in expect:
        if e[0] in jdata and type(jdata[e[0]]) != e[1]:
            return make_response_json(success=False, msg="Invalid JSON fields.")
   
    changes = 0
    # attempt to parse the type string into an enum, if applicable
    if "type" in jdata:
        tstr = jdata["type"].lower()
        if tstr in ["e", "expense", "expenses"]:
            bc.ctype = BudgetClassType.EXPENSE
        elif tstr in ["i", "income"]:
            bc.ctype = BudgetClassType.INCOME
        else:
            return make_response_json(success=False, msg="Invalid JSON fields.")
        changes += 1
   
    # parse the keywords as a list of strings
    if "keywords" in jdata:
        kws = []
        for w in jdata["keywords"]:
            kws.append(str(w))
        bc.keywords = kws
        changes += 1

    # if the name is present, update the name
    if "name" in jdata:
        bc.name = jdata["name"]
        changes += 1
    # update the description, if present
    if "description" in jdata:
        bc.desc = jdata["description"]
        changes += 1
    
    # tally up the changes, save if necessary, and send back a response
    if changes > 0:
        b.update_class(bc)
        return make_response_json(msg="Made %d changes." % changes)
    return make_response_json(msg="Made no changes.")

# Used to edit an existing transaction.
@app.route("/edit/transaction", methods = ["POST"])
def endpoint_edit_transaction():
    user = get_user(session)
    if user == None:
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json()
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # we're expecting a transaction ID
    expect = [["transaction_id", str]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")

    # search for the transaction
    b = get_budget()
    t = b.get_transaction(jdata["transaction_id"])
    if t == None:
        return make_response_json(success=False,
                                  msg="Couldn't find a matching transaction.")

    # if the user specified a class ID, we'll move the transaction to the
    # corresponding class
    bc = None
    if "class_id" in jdata:
        # make sure the class ID is the correct type in the JSON
        if type(jdata["class_id"]) != str:
            return make_response_json(success=False, msg="Invalid JSON fields.")
        # locate the class based on the class ID
        bc = b.get_class(jdata["class_id"])
        if bc == None:
            return make_response_json(success=False,
                                      msg="Couldn't find any matching classes.")
    
    # check to make sure the types of any present fields are correct
    changes = 0
    expect = [["price", float], ["vendor", str], ["description", str]]
    for e in expect:
        key = e[0]
        if key in jdata:
            if type(jdata[key]) != e[1]:
                return make_response_json(success=False, msg="Invalid JSON fields.")
        else:
            jdata[key] = None
    
    # make updates to the transaction where appropriate
    if jdata["price"] != None:
        t.price = jdata["price"]
        changes += 1
    if jdata["vendor"] != None:
        t.vendor = jdata["vendor"]
        changes += 1
    if jdata["description"] != None:
        t.desc = jdata["description"]
        changes += 1
    if bc != None:
        changes += 1

    # delete the transaction then re-add it to the correct class to force the
    # update
    if changes > 0:
        bc = t.owner if bc == None else bc
        b.delete_transaction(t)
        b.add_transaction(bc, t)
        return make_response_json(msg="Made %d changes." % changes)
    return make_response_json(msg="Made no changes.")


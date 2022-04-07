# Main module for the snowbudget flask server.
# A few links:
#   - Flask quickstart: https://pypi.org/project/Flask/
#   - Deploying to production: https://flask.palletsprojects.com/en/2.0.x/tutorial/deploy/
#   - Allowed requests: https://pythonbasics.org/flask-http-methods/
#   - Flas requests: https://flask.palletsprojects.com/en/2.0.x/quickstart/#accessing-request-data
#
#   Connor Shugg

# Includes and Flask setup
from flask import Flask, request, Response, send_from_directory
import csv
import json
import os
import sys

# Enable import from the parent directory
dpath = os.path.dirname(os.path.realpath(__file__)) # directory of this file
dpath = os.path.dirname(dpath)                      # parent directory
if dpath not in sys.path:                           # add to path
        sys.path.append(dpath)

# Local imports
from server.backend import backend_get_api
from server.auth import auth_check_login, auth_make_cookie, auth_check_cookie, \
                        auth_cookie_name
import server.config as config
from lib.transaction import Transaction

# Flask setup
app = Flask(__name__)

# Globals
api = backend_get_api()

# ============================= Helper Functions ============================= #
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
def get_request_json(request):
    try:
        rdata = request.get_data()
        if len(rdata) == 0:
            return None
        return json.loads(rdata.decode())
    except Exception as e:
        return Exception("FAILURE: %s" % e)

# Helper function that extracts the 'Cookie' header and determines if the
# request sender is authenticated.
def is_authenticated(request):
    return auth_check_cookie(request.headers.get("Cookie"))


# ==================== Root and Authentication Endpoints ===================== #
# Defines the behavior of the root '/' endpoint. Returns a simple status/hello
# message to the client.
@app.route("/")
def endpoint_root():
    # if the user is authenticated, we'll serve them the authenticated home
    # page. If not, we'll serve them the public one
    if is_authenticated(request):
        return send_from_directory(config.server_root_dpath, config.server_home_auth_fname)
    return send_from_directory(config.server_root_dpath, config.server_home_fname)

# Static file handling.
@app.route("/<path:fpath>")
def endpoint_static_file(fpath):
    # if the path is one of our public files, serve it without question
    if fpath in config.server_public_files:
        return send_from_directory(config.server_root_dpath, fpath)

    # otherwise, check authentication before serving the file
    if not is_authenticated(request):
        return make_response_json(rstatus=404)
    return send_from_directory(config.server_root_dpath, fpath)

# Used to attempt a login.
@app.route("/auth/login", methods=["POST"])
def endpoint_auth_login():
    # attempt to parse the login data and verify the login attempt
    if auth_check_login(request.get_data()):
        # create a cookie, add it as a response header, and return
        cookie = auth_make_cookie()
        cookie_str = "%s=%s; Path=/" % (auth_cookie_name, cookie)
        # if HTTPS is enabled, add the 'Secure' flag to the cookie
        if config.certs_enabled:
            cookie_str += "; Secure"
        # build a response and send the cookie back
        return make_response_json(msg="Authentication succeeded.",
                                  rheaders={"Set-Cookie": cookie_str})
    else:
        return make_response_json(success=False,
                                  msg="Authentication failed.")

# Authentication-checking endpoint.
@app.route("/auth/check", methods=["GET"])
def endpoint_auth_check():
    # look for the correct cookie
    auth = auth_check_cookie(request.headers.get("Cookie"))
    if auth:
        return make_response_json(msg="You are authenticated.")
    else:
        return make_response_json(msg="You are not authenticated.")


# ================================= Getters ================================== #
# Used to retrieve ALL budget classes.
@app.route("/get/all", methods = ["GET"])
def endpoint_bclass_all():
    if not is_authenticated(request):
        return make_response_json(rstatus=404)

    # invoke the API to retrieve *all* budget classes as a combined JSON object
    classes = api.to_json()
    return make_response_json(jdata=classes)

# Used to retrieve a budget class.
@app.route("/get/class", methods = ["GET"])
def endpoint_bclass_get():
    if not is_authenticated(request):
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json(request)
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # make sure the correct entry is present in the JSON field
    expect = [["query", str]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")
    
    # invoke the API to search for a matching class
    matches = api.find_class(jdata["query"])
    if len(matches) == 0:
        return make_response_json(success=False,
                                  msg="Couldn't find any matching classes.")
    
    # build a JSON array with our array of class objects
    jarray = []
    for bc in matches:
        jarray.append(bc.to_json())
    return make_response_json(jdata=jarray)

# Used to retrieve a transaction.
@app.route("/get/transaction", methods = ["GET"])
def endpoint_transaction_get():
    if not is_authenticated(request):
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json(request)
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")
    
    # make sure the correct entry is present in the JSON field
    expect = [["query", str]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")

    # invoke the API to search for a matching transaction
    matches = api.find_transaction(jdata["query"])
    if len(matches) == 0:
        return make_response_json(success=False,
                                  msg="Couldn't find any matching transactions.")
    
    # build a JSON array with our array of matching transactions
    jarray = []
    for bc in matches:
        jarray.append(bc.to_json())
    return make_response_json(jdata=jarray)


# ================================= Updates ================================== #
# Used to create a new transaction.
@app.route("/create/transaction", methods = ["POST"])
def endpoint_transaction_create():
    if not is_authenticated(request):
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json(request)
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # we're expecting a class ID *and* other fields within the JSON data
    expect = [["class_id", str], ["price", float], ["vendor", str],
              ["description", str]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")

    # first, search for the class, given its ID 
    matches = api.find_class(jdata["class_id"])
    if len(matches) == 0:
        return make_response_json(success=False,
                                  msg="Couldn't find any matching classes.")
    bc = matches[0] # grab first one (should only be one)

    # create a transaction struct and pass it to the API
    t = Transaction(jdata["price"], vendor=jdata["vendor"],
                    description=jdata["description"])
    api.add_transaction(t, bc)
    api.save()
    return make_response_json(msg="Transaction created.", jdata=t.to_json())

# Used to delete a transaction.
@app.route("/delete/transaction", methods = ["POST"])
def endpoint_transaction_delete():
    if not is_authenticated(request):
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json(request)
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # we're expecting a transaction ID
    expect = [["transaction_id", str]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")
    
    # retrieve the corresponding transaction object
    matches = api.find_transaction(jdata["transaction_id"])
    if len(matches) == 0:
        return make_response_json(success=False,
                                  msg="Couldn't find any matching transactions.")
    
    # delete the transaction, then save
    succ = api.delete_transaction(matches[0])
    api.save()
    msg = "Transaction deleted." if succ else "Failed to delete the transaction."
    return make_response_json(success=succ, msg=msg)

# Used to edit an existing transaction.
@app.route("/edit/transaction", methods = ["POST"])
def endpoint_transaction_edit():
    if not is_authenticated(request):
        return make_response_json(rstatus=404)

    # extract the json data in the request body
    jdata = get_request_json(request)
    if type(jdata) == Exception:
        return make_response_json(rstatus=400, msg="Failed to parse request body.")
    elif jdata == None:
        return make_response_json(rstatus=400, msg="Missing request body.")

    # we're expecting a transaction ID
    expect = [["transaction_id", str]]
    if not check_json_fields(jdata, expect):
        return make_response_json(success=False, msg="Missing JSON fields.")

    # search for the transaction
    matches = api.find_transaction(jdata["transaction_id"])
    if len(matches) == 0:
        return make_response_json(success=False,
                                  msg="Couldn't find any matching transactions.")
    t = matches[0]

    # if the user specified a class ID, we'll move the transaction to the
    # corresponding class
    bc = None
    if "class_id" in jdata and type(jdata["class_id"]) == str:
        # locate the class based on the class ID
        matches = api.find_class(jdata["class_id"])
        if len(matches) == 0:
            return make_response_json(success=False,
                                      msg="Couldn't find any matching classes.")
        bc = matches[0]

    
    # check to make sure the types of any present fields are correct
    changes = 0
    expect = [["price", float], ["vendor", str], ["description", str]]
    for e in expect:
        key = e[0]
        if key in jdata:
            if type(jdata[key]) != e[1]:
                return make_response_json(success=False, msg="Invalid request body.")
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

    # move groups if necessary
    if bc != None:
        changes += int(api.move_transaction(t, bc))

    # save and/or respond with the appropriate message
    if changes > 0:
        api.save()
        return make_response_json(msg="Made %d changes." % changes)
    else:
        return make_response_json(msg="Made no changes.")


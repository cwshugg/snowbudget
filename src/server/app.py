# Main module for the snowbudget flask server.
# A few links:
#   - Flask quickstart: https://pypi.org/project/Flask/
#   - Deploying to production: https://flask.palletsprojects.com/en/2.0.x/tutorial/deploy/
#   - Allowed requests: https://pythonbasics.org/flask-http-methods/
#   - Flas requests: https://flask.palletsprojects.com/en/2.0.x/quickstart/#accessing-request-data
#
#   Connor Shugg

# Includes and Flask setup
from flask import Flask, request, Response
import csv
import json
app = Flask(__name__)


# ============================= Helper Functions ============================= #
# Makes a 400 BAD REQUEST response message.
def make_response_400(msg):
    jdata = {"message": msg}
    resp = Response(response=json.dumps(jdata), status=400)
    resp.headers["Content-Type"] = "application/json"
    return resp

# Takes a dictionary of data and adds an optional message to it, then packs it
# all into a Flask Response object.
def make_response_json(jdata={}, msg=""):
    jdata["message"] = msg
    resp = Response(response=json.dumps(jdata), status=200)
    resp.headers["Content-Type"] = "application/json"
    return resp

# Takes in a request's URL arguments and attempts to find an entry with the
# given key value. Returns None on failure to find and the value on success.
def get_url_parameter(args, key):
    p = args.get(key, "")
    if (p == ""):
        return None
    return p

# Helper function that tries to extract a URL parameter of the appropriate name
# representing a budget class ID. Returns None if one wasn't found, or the
# string value is one *was* found.
def get_bclass_id(request):
    bcid = request.args.get("bcid", "")
    if bcid == "":
        return None
    return bcid

# Helper function to extract the transaction ID from the request URL parameters.
def get_transaction_id(request):
    tid = request.args.get("tid", "")
    if tid == "":
        return None
    return tid


# ========================== Budget Class Endpoints ========================== #
# Defines the behavior of the root '/' endpoint. Returns a simple status/hello
# message to the client.
@app.route("/")
def endpoint_root():
    return make_response_json(msg="sb functional.")

# Used to retrieve a budget class.
@app.route("/bclass/get", methods = ["GET"])
def endpoint_bclass_get():
    # get the budget class ID
    bcid = get_bclass_id(request)
    if bcid == None:
        return make_response_400("Missing required fields.")
    
    # TODO
    return make_response_json(msg="You requested a budget class: %s" % bcid)

# Used to create a new budget class.
@app.route("/bclass/create", methods = ["POST"])
def endpoint_bclass_create():
    # TODO
    return make_response_json(msg="todo: /bclass/create")

# Used to delete a budget class.
@app.route("/bclass/delete", methods = ["POST"])
def endpoint_bclass_delete():
    # get the budget class ID
    bcid = get_bclass_id(request)
    if bcid == None:
        return make_response_400("Missing required fields.")
    
    # TODO
    return make_response_json(msg="todo: /bclass/delete")

# Used to edit an existing budget class.
@app.route("/bclass/edit", methods = ["POST"])
def endpoint_bclass_edit():
    # get the budget class ID
    bcid = get_bclass_id(request)
    if bcid == None:
        return make_response_400("Missing required fields.")
    
    # TODO
    return make_response_json(msg="todo: /bclass/edit")


# ========================== Transaction Endpoints =========================== #
# Used to retrieve a transaction.
@app.route("/transaction/get", methods = ["GET"])
def endpoint_transaction_get():
    # get the transaction ID
    tid = get_transaction_id(request)
    if tid == None:
        return make_response_400("Missing required fields.")
    
    # TODO
    return make_response_json(msg="You requested a transaction: %s" % tid)

# Used to create a new transaction.
@app.route("/transaction/create", methods = ["POST"])
def endpoint_transaction_create():
    # get the budget class ID the transaction will belong to
    bcid = get_bclass_id(request)
    if bcid == None:
        return make_response_400("Missing required fields.")
    
    # TODO
    return make_response_json(msg="todo: /transaction/create")

# Used to delete a transaction.
@app.route("/transaction/delete", methods = ["POST"])
def endpoint_transaction_delete():
    # get the transaction ID
    tid = get_transaction_id(request)
    if tid == None:
        return make_response_400("Missing required fields.")
    
    # TODO
    return make_response_json(msg="todo: /transaction/delete")

# Used to edit an existing transaction.
@app.route("/transaction/edit", methods = ["POST"])
def endpoint_transaction_edit():
    # get the transaction ID
    tid = get_transaction_id(request)
    if tid == None:
        return make_response_400("Missing required fields.")
    
    # TODO
    return make_response_json(msg="todo: /transaction/edit")


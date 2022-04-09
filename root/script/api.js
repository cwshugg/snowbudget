// JS for communicating with the snowbudget backend.
//
//      Connor Shugg

// Other globals
const url = window.location.protocol + "//" + window.location.host;

// Document globals
const bclass_expense_container = document.getElementById("bclass_expenses");
const bclass_income_container = document.getElementById("bclass_income");

// ========================== Server Communication ========================== //
// Takes in an endpoint string, HTTP method, and JSON message body and sends a
// HTTP request to the server.
async function send_request(endpoint, method, jdata)
{
    // build a request body string, if JSON data was given
    request_body = null;
    if (jdata)
    { request_body = JSON.stringify(jdata); }

    // send a request to the correct server endpoint
    let response = await fetch(url + endpoint, {
        method: method, body: request_body
    });

    // retrieve the response body and attempt to parse it as JSON
    let text = await response.text();
    return JSON.parse(text);
}


// ============================ Helper Functions ============================ //
// Returns true if the given class is an expense class.
function bclass_is_expense(bclass)
{
    t = bclass.type.toLowerCase();
    return t === "e" || t === "expense";
}

// Returns true if the given class is an income class.
function bclass_is_income(bclass)
{
    t = bclass.type.toLowerCase();
    return t === "i" || t === "income";
}


// ============================= HTML Elements ============================== //
// Used to create a simply HTML error message.
function make_error_message(msg)
{
    return "<p><b style=\"color: red\">Error:</b> " + msg + "</p>";
}

// Makes a collapsible button element with the given ID and text.
function make_collapsible_button(id, text)
{
    // create the button and set all appropriate fields
    let btn = document.createElement("button");
    btn.id = id;
    btn.className = "collapsible-button font-main";
    btn.innerHTML = text;

    // create the indicator and append it
    let span = document.createElement("span");
    span.className = "collapsible-button-indicator";
    span.innerHTML = "+";
    btn.appendChild(span);
    return btn;
}

// Makes a collapsible content element with the given ID.
function make_collapsible_content(id)
{
    let div = document.createElement("div");
    div.id = id;
    div.className = "collapsible-content";
    div.innerHTML = "<p>TODO</p>";
    return div;
}

// =============================== UI Updates =============================== //
// Used to update a single budget class UI element.
async function budget_class_refresh(bclass)
{
    // take the budget class' ID and look for an element within the main div.
    // If one doesn't exist, we'll create it and add it to the correct div
    bclass_div = document.getElementById(bclass.id);
    if (!bclass_div)
    {
        bclass_div = document.createElement("div");
        bclass_div.id = bclass.id;
        // depending on the type, append to the correct child
        if (bclass_is_expense(bclass))
        { bclass_expense_container.appendChild(bclass_div); }
        else if (bclass_is_income(bclass))
        { bclass_income_container.appendChild(bclass_div); }
        else
        { console.log("Found budget class of unknown type: " + bclass.id); }
    }

    // look for the collapsible button corresponding to the bclass. If we can't
    // find it, we'll create one
    btn_id = bclass.id + "_btn";
    bclass_btn = document.getElementById(btn_id);
    if (!bclass_btn)
    {
        bclass_btn = make_collapsible_button(btn_id, bclass.name);
        bclass_div.appendChild(bclass_btn);
    }

    // look for the collapsible content corresponding to the bclass. If we
    // can't find it, we'll create one
    content_id = bclass.id + "_content";
    bclass_content = document.getElementById(content_id);
    if (!bclass_content)
    { 
        bclass_content = make_collapsible_content(content_id);
        bclass_div.appendChild(bclass_content);
        collapsible_init(bclass_btn);
    }

    // TODO: update stuff
}

// Used to update ALL budget class UI elements.
async function budget_classes_refresh()
{
    // send a request to the server to get all budget classes
    data = await send_request("/get/all", "GET", null);
    
    // if the request failed, we'll create an error element
    if (!data.success)
    {
        let message = "failed to retrieve content (" + data.message + ")."
        let emsg = make_error_message(message);
        bclass_expense_container.innerHTML = emsg;
        bclass_income_container.innerHTML = emsg;
        return
    }

    // otherise, we'll iterate through each budget class and set up the UI
    // elements
    for (let i = 0; i < data.payload.length; i++)
    { budget_class_refresh(data.payload[i]); }
}


// ============================= Initialization ============================= //
// Clears and resets the inner HTML of the budget class div.
function budget_classes_init()
{
    bclass_expense_container.innerHTML = "";
    bclass_income_container.innerHTML = "";
    budget_classes_refresh();
}

window.onload = function()
{
    budget_classes_init();
}


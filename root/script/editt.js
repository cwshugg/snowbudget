// JS for the 'edit transaction' page.
//
//      Connor Shugg

// Document globals
const editt_btn_cancel = document.getElementById("btn_cancel");
const editt_btn_delete = document.getElementById("btn_delete");
const editt_btn_update = document.getElementById("btn_update");
const editt_input_price = document.getElementById("tprice");
const editt_input_vendor = document.getElementById("tvendor");
const editt_input_desc = document.getElementById("tdesc");
const editt_input_recur = document.getElementById("trecur");
const editt_class_dropdown = document.getElementById("tclass");

let transaction = null;
let bclass_id = null;

// Invoked when the 'cancel' button is clicked.
function editt_click_cancel()
{
    window.location.replace("home.html");
}

// Invoked when the 'save' button is clicked.
function editt_click_update()
{
    diagnostics_clear();

    // retrieve all field values
    let price = editt_input_price.value;
    let vendor = editt_input_vendor.value;
    let desc = editt_input_desc.value;
    let bcid = editt_class_dropdown.value;
    let recur = editt_input_recur.checked;
    
    // if any are blank, don't proceed
    if (price === "" || vendor === "" || desc === "" || bcid === "")
    { return; }

    // attempt to convert the price to a float
    try
    { price = parseFloat(price); }
    catch (error)
    {
        diagnostics_add_error("The price must be a number.");
        return;
    }
    if (isNaN(price))
    {
        diagnostics_add_error("The price must be a number.");
        return;
    }

    // put together the JSON object, containing only the revisions
    let jdata = {"transaction_id": transaction.id}
    if (price !== transaction.price)
    { jdata.price = price; }
    if (vendor !== transaction.vendor)
    { jdata.vendor = vendor; }
    if (desc !== transaction.description)
    { jdata.description = desc; }
    if (bcid !== bclass_id)
    { jdata.class_id = bcid; }
    if (recur !== transaction.recurring)
    { jdata.recurring = recur; }

    // send a request to edit the transaction
    diagnostics_clear();
    send_request("/edit/transaction", "POST", jdata).then(
        function(response)
        {
            if (response.success)
            { diagnostics_add_success("Success. " + response.message); }
            else
            { diagnostics_add_error("Failure. " + response.message); }
        },
        function(error)
        {
            diagnostics_add_error("Failed to send the request: " + error);
        }
    );
}

// Invoked when the 'delete' button is clicked.
function editt_click_delete()
{
    // get the transaction ID and send a request to delete the transaction
    let jdata = {"transaction_id": transaction.id};
    diagnostics_clear();
    send_request("/delete/transaction", "POST", jdata).then(
        function(response)
        {
            if (response.success)
            { diagnostics_add_success("Success. " + response.message); }
            else
            { diagnostics_add_error("Failure. " + response.message); }
        },
        function(error)
        {
            diagnostics_add_error("Failed to send the request: " + error);
        }
    );
}

// Callback function for when an input box changes or the dropdown box value
// changes.
function editt_input_change()
{
    // compare each field to the existing values. If nothing has changed, we'll
    // keep the 'update' button disabled. If something HAS changed, we'll
    // instead enable it
    let price = editt_input_price.value;
    let vendor = editt_input_vendor.value;
    let desc = editt_input_desc.value;
    let bcid = editt_class_dropdown.value;
    let recur = editt_input_recur.checked;
    
    // attempt to convert the price to a float
    try
    { price = parseFloat(price); }
    catch (error)
    {
        diagnostics_add_error("The price must be a number.");
        return;
    }
    if (isNaN(price))
    {
        diagnostics_add_error("The price must be a number.");
        return;
    }

    if (price === transaction.price && vendor === transaction.vendor &&
        desc === transaction.description && bcid === bclass_id &&
        recur === transaction.recurring)
    { btn_update.disabled = true; }
    else
    { btn_update.disabled = false; }
}

// ============================= Initialization ============================= //
// Asynchronously retrieves the back-end data and updates the display.
async function editt_ui_init(tid)
{
    diagnostics_add_message("Contacting server...");
    // first, retrieve the individual transaction
    const jdata = {"transaction_id": tid};
    let data = await send_request("/get/transaction", "POST", jdata);
    if (!data)
    {
        // show an error message
        diagnostics_clear();
        diagnostics_add_error("Failed to retrieve transaction from server.");
        return;
    }
    // if we couldn't find a matching transaction, tell the user
    if (!data.success)
    {
        diagnostics_clear();
        diagnostics_add_error("Failed to retrieve transaction. " + data.message);
        return;
    }
    transaction = data.payload;

    // next, retrieve the full set of budget classes
    data = await retrieve_data();
    if (!data)
    {
        // show an error message
        diagnostics_clear();
        diagnostics_add_error("Failed to retrieve data from server.");
        return;
    }
    let bclasses = data.payload;
    bclasses.sort(function(c1, c2) { return c1.name.localeCompare(c2.name); });
    diagnostics_clear();
    
    // we'll iterate across each budget class and create dropdown options for
    // each of them in our dropdown menu. At the same time, we'll determine which
    // of the classes the transaction belongs to
    let match_idx = -1;
    for (let i = 0; i < bclasses.length; i++)
    {
        let bclass = bclasses[i];
        
        // create a dropdown option for the budget class
        let opt = document.createElement("option");
        opt.value = bclass.id;
        opt.innerHTML = bclass.name;
        editt_class_dropdown.appendChild(opt);
        
        // iterate through the class' transactions to search for ours
        for (let j = 0; j < bclass.history.length; j++)
        {
            if (tid === bclass.history[j].id)
            {
                match_idx = i;
                break;
            }
        }
    }

    // if we didn't find a matching index, tell the user
    if (match_idx == -1)
    {
        diagnostics_add_error("Failed to locate the class that owns the given transaction.");
        return;
    }
    bclass_id = bclasses[match_idx].id;

    // set the dropdown index and fill up the other input fields
    editt_class_dropdown.selectedIndex = match_idx;
    editt_input_price.value = transaction.price;
    editt_input_vendor.value = transaction.vendor;
    editt_input_desc.value = transaction.description;
}

// Window initialization function
window.onload = function()
{
    // retrieve the transaction ID from the URL
    const params = new URLSearchParams(window.location.search);
    if (!params.has("transaction_id"))
    {
        diagnostics_add_error("Failed to find the \"transaction_id\" in the URL.");
        return;
    }
    const tid = params.get("transaction_id");

    // set up button clicks and other events, then initialize the UI
    editt_btn_cancel.addEventListener("click", editt_click_cancel);
    editt_btn_update.addEventListener("click", editt_click_update);
    editt_btn_delete.addEventListener("click", editt_click_delete);
    editt_input_price.addEventListener("input", editt_input_change);
    editt_input_vendor.addEventListener("input", editt_input_change);
    editt_input_desc.addEventListener("input", editt_input_change);
    editt_input_recur.addEventListener("input", editt_input_change);
    editt_class_dropdown.addEventListener("change", editt_input_change);
    editt_ui_init(tid);
}


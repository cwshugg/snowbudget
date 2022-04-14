// JS for the 'edit transaction' page.
//
//      Connor Shugg

// Document globals
const addt_btn_cancel = document.getElementById("btn_cancel");
const addt_btn_update = document.getElementById("btn_update");
const addt_input_price = document.getElementById("tprice");
const addt_input_vendor = document.getElementById("tvendor");
const addt_input_desc = document.getElementById("tdesc");
const addt_class_dropdown = document.getElementById("tclass");

// Invoked when the 'cancel' button is clicked.
function addt_click_cancel()
{
    window.location.replace("home.html");
}

// Invoked when the 'save' button is clicked.
function addt_click_update()
{
    diagnostics_clear();

    // retrieve all field values
    let price = addt_input_price.value;
    let vendor = addt_input_vendor.value;
    let desc = addt_input_desc.value;
    let bcid = addt_class_dropdown.value;
    
    // if any are blank, don't proceed
    if (price === "" || vendor === "" || desc === "" || bcid === "")
    { return; }

    // attempt to convert the price to a float
    try
    { price = parseFloat(price); }
    catch (error)
    {
        diagnostics_clear();
        diagnostics_add_error("The price must be a number.");
    }

    // put together the JSON object
    let jdata = {
        "class_id": bcid,
        "price": price,
        "vendor": vendor,
        "description": desc,
        "timestamp": Math.round(Date.now() / 1000)
    };

    // send a request to create the transaction
    send_request("/create/transaction", "POST", jdata).then(
        function(response)
        {
            if (response.success)
            { diagnostics_add_success("Success. " + response.message); }
            else
            { diagnostics_add_error("Failure. " + response.message); }
        },
        function(error)
        {
            diagnostics_clear();
            diagnostics_add_error("Failed to send the request: " + error);
        }
    );
}

// ============================= Initialization ============================= //
// Asynchronously retrieves the back-end data and updates the display.
async function addt_ui_init(tid)
{
    diagnostics_add_message("Contacting server...");
    const jdata = {"transaction_id": tid};
    let data = await send_request("/get/transaction", "POST", jdata);
    if (!data)
    {
        // show an error message
        diagnostics_clear();
        diagnostics_add_error("Failed to retrieve data from server.");
        return;
    }
    diagnostics_clear();

    console.log(data.payload);

    // enable the buttons now that we have data
    addt_btn_update.disabled = false;
    addt_btn_cancel.disabled = false;

    return; // TODO TODO TODO TODO REMOVE

    // sort the budget classes
    let bclasses = data.payload;
    bclasses.sort(function(c1, c2) { return c1.name.localeCompare(c2.name); });

    // we'll iterate across each budget class and create dropdown options for
    // each of them in our dropdown menu
    let default_idx = -1;
    for (let i = 0; i < bclasses.length; i++)
    {
        let bclass = bclasses[i];
        
        // create a dropdown option for the budget class
        let opt = document.createElement("option");
        opt.value = bclass.id;
        opt.innerHTML = bclass.name;
        addt_class_dropdown.appendChild(opt);

        // while we're here, look to see if this budget class contains the word
        // "default" in its keywords array. If it does, we'll auto-select this
        // as the default selection
        if (default_idx == -1)
        {
            let find_result = bclass.keywords.find(function(str) {
                    return str.toLowerCase() === "default";
            });
            // if we found the keyword, update the default class
            if (find_result != undefined)
            { default_idx = i; }
        }
    }

    // if we found a default category, auto-select it
    if (default_idx > -1)
    { addt_class_dropdown.selectedIndex = default_idx; }
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

    // set up button clicks and initialize the UI
    addt_btn_cancel.addEventListener("click", addt_click_cancel);
    addt_btn_update.addEventListener("click", addt_click_update);
    addt_ui_init(tid);
}


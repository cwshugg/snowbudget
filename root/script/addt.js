// JS for the 'add transaction' page.
//
//      Connor Shugg

// Document globals
const addt_btn_cancel = document.getElementById("btn_cancel");
const addt_btn_save = document.getElementById("btn_save");
const addt_input_price = document.getElementById("tprice");
const addt_input_vendor = document.getElementById("tvendor");
const addt_input_desc = document.getElementById("tdesc");
const addt_input_date = document.getElementById("tdate");
const addt_input_recur = document.getElementById("trecur");
const addt_class_dropdown = document.getElementById("tclass");
let datetime = null;

// Invoked when the 'cancel' button is clicked.
function addt_click_cancel()
{
    const url = "home.html?" + get_datetime_url_string(datetime);
    window.location.replace(url);
}

// Invoked when the 'save' button is clicked.
function addt_click_save()
{
    diagnostics_clear();

    // retrieve all field values
    let price = addt_input_price.value;
    let vendor = addt_input_vendor.value;
    let desc = addt_input_desc.value;
    let date = addt_input_date.value;
    let bcid = addt_class_dropdown.value;
    
    // if price, class ID, or date are blank, don't proceed
    if (price === "" || bcid === "" || date === "")
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

    // attempt to convert the date to a number of seconds
    let ts = Date.now() / 1000;
    try
    { ts = new Date(date + "T00:00").getTime() / 1000; }
    catch (error)
    {
        diagnostics_add_error("Couldn't parse the given date value.");
        return;
    }

    // extract the recurring checkbox value
    const recur = addt_input_recur.checked;

    // put together the JSON object
    let jdata = {
        "class_id": bcid,
        "price": price,
        "vendor": vendor,
        "description": desc,
        "timestamp": Math.round(ts),
        "recurring": recur,
        "datetime": datetime.getTime() / 1000.0
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
async function addt_ui_init(dt)
{
    diagnostics_add_message("Contacting server...");
    let data = await retrieve_data(dt)
    if (!data)
    {
        // show an error message
        diagnostics_clear();
        diagnostics_add_error("Failed to retrieve data from server.");
        return;
    }
    diagnostics_clear();

    // enable the buttons now that we have data
    addt_btn_save.disabled = false;
    addt_btn_cancel.disabled = false;

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

    // set the date selector's value to the given datetime
    addt_input_date.value = dt.toISOString().slice(0, 10);
}

// Window initialization function
window.onload = function()
{
    datetime = get_datetime_from_url();
    addt_btn_cancel.addEventListener("click", addt_click_cancel);
    addt_btn_save.addEventListener("click", addt_click_save);
    addt_ui_init(datetime);
}


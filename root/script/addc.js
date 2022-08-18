// JS for the 'add class' page.
//
//      Connor Shugg

// Document globals
const addc_btn_cancel = document.getElementById("btn_cancel");
const addc_btn_save = document.getElementById("btn_save");
const addc_input_name = document.getElementById("cname");
const addc_input_desc = document.getElementById("cdesc");
const addc_input_words = document.getElementById("cwords");
const addc_type_dropdown = document.getElementById("ctype");
const addc_target_type_dropdown = document.getElementById("ctarget_type");
const addc_target_input_value = document.getElementById("ctarget_val");
let datetime = null;

// Invoked when the 'cancel' button is clicked.
function addc_click_cancel()
{
    const params = [{"name": "datetime", "value": "" + datetime.getTime() / 1000.0}]
    const url = "home.html" + make_url_param_string(params);
    window.location.replace(url);
}

// Invoked when the 'save' button is clicked.
function addc_click_save()
{
    diagnostics_clear();

    // retrieve class values
    let name = addc_input_name.value;
    let desc = addc_input_desc.value;
    let words = addc_input_words.value;
    let type = addc_type_dropdown.value;
    // retrieve target values
    let ttype = addc_target_type_dropdown.value;
    let tval = addc_target_input_value.value;

    // if the name, description, or keywords are blank, don't proceed
    if (name === "" || desc === "")
    { return; }

    // attempt to pick apart the string in the keywords textbox into an array
    // of strings, separated by comma
    word_list = [name.toLowerCase()];
    if (words !== "")
    {
        words = words.trim().split(",");
        for (let i = 0; i < words.length; i++)
        {
            if (words[i] !== "")
            { word_list.push(words[i].trim().toLowerCase()); }
        }
    }

    // create the JSON object to send to the server
    let jdata = {
        "name": name,
        "description": desc,
        "type": type,
        "keywords": word_list,
        "datetime": datetime.getTime() / 1000.0
    }
    
    // if a target value was given, we'll add this to the JSON payload
    if (tval !== "")
    {
        // attempt to convert the target value to a float
        try
        { tval = parseFloat(tval); }
        catch (error)
        {
            diagnostics_add_error("The target value must be a number.");
            return;
        }
        if (isNaN(tval))
        {
            diagnostics_add_error("The target value must be a number.");
            return;
        }

        // add to the payload
        jdata.target = {"type": ttype, "value": tval};
    }
    
    // send a request to create the class
    send_request("/create/class", "POST", jdata).then(
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
async function addc_ui_init(dt)
{
    addc_btn_save.disabled = false;
    addc_btn_cancel.disabled = false;

    // for each of the possible options for our target type, we'll create a
    // dropdown menu item
    const ctype_values = [
        {"name": "Expense", "value": "expense"},
        {"name": "Income", "value": "income"}
    ];
    for (let i = 0; i < ctype_values.length; i++)
    {
        let opt = document.createElement("option");
        opt.value = ctype_values[i].value;
        opt.innerHTML = ctype_values[i].name;
        addc_type_dropdown.appendChild(opt);
    }

    // for each of the possible options for our budget target type, we'll do
    // the same thing as above (create dropdown options for it)
    const ctarget_types = [
        {"name": "Dollar", "value": "dollar"},
        {"name": "Percent of Income", "value": "percent_income"}
    ]
    for (let i = 0; i < ctarget_types.length; i++)
    {
        let opt = document.createElement("option");
        opt.value = ctarget_types[i].value;
        opt.innerHTML = ctarget_types[i].name;
        addc_target_type_dropdown.appendChild(opt);
    }
}

// Window initialization function
window.onload = function()
{
    datetime = get_datetime_from_url();
    addc_btn_cancel.addEventListener("click", addc_click_cancel);
    addc_btn_save.addEventListener("click", addc_click_save);
    addc_ui_init(datetime);
}


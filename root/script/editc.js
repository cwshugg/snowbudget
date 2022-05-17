// JS for the 'edit class' page.
//
//      Connor Shugg

// Document globals
const editc_btn_cancel = document.getElementById("btn_cancel");
const editc_btn_delete = document.getElementById("btn_delete");
const editc_btn_save = document.getElementById("btn_save");
const editc_input_name = document.getElementById("cname");
const editc_input_desc = document.getElementById("cdesc");
const editc_input_words = document.getElementById("cwords");
const editc_type_dropdown = document.getElementById("ctype");
const editc_target_type_dropdown = document.getElementById("ctarget_type");
const editc_target_input_value = document.getElementById("ctarget_val");

// Globals
let bclass = null;
let class_id = null;

// Takes in an array of strings and creates a comma-separated string containing
// all of them.
function make_keyword_string(words)
{
    let keyword_str = "";
    for (let i = 0; i < words.length; i++)
    {
        keyword_str += words[i];
        if (i < words.length - 1)
        { keyword_str += ", "; }
    }
    return keyword_str;
}

// Invoked when the 'cancel' button is clicked.
function editc_click_cancel()
{
    window.location.replace("home.html");
}

// Invoked when the 'delete' button is clicked.
function editc_click_delete()
{
    // send a POST request to delete the class
    let jdata = {"class_id": bclass.id};
    diagnostics_clear();
    send_request("/delete/class", "POST", jdata).then(
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

// Invoked when the 'save' button is clicked.
function editc_click_save()
{
    diagnostics_clear();

    // retrieve class values
    let name = editc_input_name.value;
    let desc = editc_input_desc.value;
    let words = editc_input_words.value;
    let type = editc_type_dropdown.value;
    // retrieve target values
    let ttype = editc_target_type_dropdown.value;
    let tval = editc_target_input_value.value;

    // if the name, description, or keywords are blank, don't proceed
    if (name === "" || desc === "")
    { return; }
    
    // build a word string to compare against the current one
    const keyword_str = make_keyword_string(bclass.keywords);
 
    // create the JSON object to send to the server, containing only the fields
    // that were changed from the original
    let jdata = {};
    if (name !== bclass.name)
    { jdata.name = name; }
    if (desc !== bclass.description)
    { jdata.description = desc; }
    if (type.toLowerCase() !== bclass.type.toLowerCase())
    { jdata.type = type.toLowerCase(); }
    if (keyword_str.toLowerCase() !== words)
    {
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
        jdata.keywords = word_list;
    }
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

        // if no target exist or the target is somehow different, we'll add it
        // to our JSON payload
        if (!bclass.target ||
            bclass.target.type.toLowerCase() !== ttype.toLowerCase() ||
            float_to_dollar_string(bclass.target.value) !== float_to_dollar_string(tval))
        { jdata.target = {"type": ttype.toLowerCase(), "value": tval}; }
    }

    // set the class ID before sending
    jdata.class_id = bclass.id;
    
    // send a request to create the class
    send_request("/edit/class", "POST", jdata).then(
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

// Invoked when a change is made to one of the input boxes.
function editc_input_change()
{
    // retrieve class values
    let name = editc_input_name.value;
    let desc = editc_input_desc.value;
    let words = editc_input_words.value;
    let type = editc_type_dropdown.value;
    // retrieve target values
    let ttype = editc_target_type_dropdown.value;
    let tval = editc_target_input_value.value;

    // compare against the original values retrieved from the class and decide
    // whether or not to enable the 'update' button
    const keyword_str = make_keyword_string(bclass.keywords);
    let is_different = name !== bclass.name || desc !== bclass.description ||
                         keyword_str.toLowerCase() !== words.toLowerCase() ||
                         type.toLowerCase() !== bclass.type.toLowerCase();
    // account for the target
    if (tval !== "")
    {
        if (!bclass.target ||
            bclass.target.type.toLowerCase() !== ttype.toLowerCase() ||
            float_to_dollar_string(bclass.target.value) !== float_to_dollar_string(tval))
        { is_different = true; }
    }
    // if a different is detected, toggle the button
    if (is_different)
    { editc_btn_save.disabled = false; }
    else
    { editc_btn_save.disabled = true; }
}

// ============================= Initialization ============================= //
// Asynchronously retrieves the back-end data and updates the display.
async function editc_ui_init(bcid)
{
    diagnostics_add_message("Contacting server...");
    // first, retrieve the class' data
    const jdata = {"class_id": bcid};
    let data = await send_request("/get/class", "POST", jdata);
    if (!data)
    {
        // show an error message
        diagnostics_clear();
        diagnostics_add_error("Failed to retrieve class from server.");
        return;
    }
    // if we couldn't find a matching class, tell the user
    if (!data.success)
    {
        diagnostics_clear();
        diagnostics_add_error("Failed to retrieve class. " + data.message);
        return;
    }
    diagnostics_clear();
    bclass = data.payload;

    // enable delete button now that we've got data
    editc_btn_delete.disabled = false;

    // for each of the possible options for our target type, we'll create a
    // dropdown menu item
    const ctype_values = [
        {"name": "Expense", "value": "expense"},
        {"name": "Income", "value": "income"}
    ];
    let ctype_select_idx = 0;
    for (let i = 0; i < ctype_values.length; i++)
    {
        let opt = document.createElement("option");
        opt.value = ctype_values[i].value;
        opt.innerHTML = ctype_values[i].name;
        editc_type_dropdown.appendChild(opt);
        // mark this as the one to select if it matches the bclass type
        if (bclass.type.toLowerCase() === ctype_values[i].value.toLowerCase())
        { ctype_select_idx = i; }
    }

    // for each of the possible options for our budget target type, we'll do
    // the same thing as above (create dropdown options for it)
    const ctarget_types = [
        {"name": "Dollar", "value": "dollar"},
        {"name": "Percent of Income", "value": "percent_income"}
    ]
    let ctarget_type_select_idx = 0;
    for (let i = 0; i < ctarget_types.length; i++)
    {
        let opt = document.createElement("option");
        opt.value = ctarget_types[i].value;
        opt.innerHTML = ctarget_types[i].name;
        editc_target_type_dropdown.appendChild(opt);
        // mark this as the one to select if it matches the ctarget type
        if (bclass.target && bclass.target.type.toLowerCase() === ctarget_types[i].value.toLowerCase())
        { ctarget_type_select_idx = i; }
    }

    // fill in each input field with the correct value based on the information
    // in the class JSON we just retrieved from the server
    editc_input_name.value = bclass.name;
    editc_input_desc.value = bclass.description;
    const keyword_str = make_keyword_string(bclass.keywords);
    editc_input_words.value = keyword_str;
    editc_type_dropdown.selectedIndex = ctype_select_idx;
    editc_target_type_dropdown.selectedIndex = ctarget_type_select_idx;
    if (bclass.target)
    { editc_target_input_value.value = bclass.target.value; }
}

// Window initialization function
window.onload = function()
{
    // retrieve the transaction ID from the URL
    const params = new URLSearchParams(window.location.search);
    if (!params.has("class_id"))
    {
        diagnostics_add_error("Failed to find the \"class_id\" in the URL.");
        return;
    }
    const bcid = params.get("class_id");

    editc_btn_cancel.addEventListener("click", editc_click_cancel);
    editc_btn_delete.addEventListener("click", editc_click_delete);
    editc_btn_save.addEventListener("click", editc_click_save);
    editc_input_name.addEventListener("input", editc_input_change);
    editc_input_desc.addEventListener("input", editc_input_change);
    editc_input_words.addEventListener("input", editc_input_change);
    editc_type_dropdown.addEventListener("change", editc_input_change);
    editc_target_type_dropdown.addEventListener("change", editc_input_change);
    editc_target_input_value.addEventListener("input", editc_input_change);
    editc_ui_init(bcid);
}


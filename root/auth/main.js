// JS for IFTTT webhook requests.
//
//      Connor Shugg

// Other globals
const url = window.location.protocol + "//" + window.location.host;
const beacons = [
    beacon_make("c", "Connor's Beacon"),
    beacon_make("r", "Reagan's Beacon")
]


// ================================ Beacons ================================ //
// Takes in beacon information and returns a JSON object.
function beacon_make(id, name)
{
    return {"id": id, "name": name};
}

// Takes in beacon data and adds HTML to the beacon_select element to create an
// option for the given beacon.
function beacon_select_make_option(bdata)
{
    const opt = "<option value=\"" + bdata.id + "\">" + bdata.name + "</option>";
    beacon_select.innerHTML += opt;
}


// =========================== Beacon Shortcuts ============================ //
const beacon_shortcut_div = document.getElementById("beacon_shortcut_div");

// Global shortcut array
const shortcuts = [
    shortcut_make("shortcut_btn_reset", "RESET", "FFFFFF", "1"),
    shortcut_make("shortcut_btn_good_morning", "Good Morning", "FFD500", "75"),
    shortcut_make("shortcut_btn_good_night", "Good Night", "7F11E0", "15"),
    shortcut_make("shortcut_btn_call", "Let's Call", "00FFFF", "25"),
    shortcut_make("shortcut_btn_minecraft", "Minecraft?", "76BB40", "25"),
    shortcut_make("shortcut_btn_emergency", "Emergency", "FF0000", "100")
]

// Helper function that creates a single shortcut JSON object.
function shortcut_make(id, name, color, brightness)
{
    return {"id": id, "name": name, "color": color, "brightness": brightness};
}

// Takes in a shortcut JSON object and adds a new button to a specific section
// of the web page.
function shortcut_make_button(shortcut)
{
    // generate HTML for the given shortcut and add it to the shortcut div
    let btn = "<button id=\"" + shortcut.id + "\"" +
              "style=\"color: #" + shortcut.color + "\"" +
              "class=\"button-shortcut\">" + shortcut.name + "<br>" +
              "(BR: " + shortcut.brightness + "%)" + "</button>";
    beacon_shortcut_div.innerHTML += btn;
}

// Click listener for all shortcut buttons.
function shortcut_btn_click(btn)
{
    // use the button's ID to determine what parameters to pass into our
    // webhook-helper function
    let shortcut = null;
    for (let i = 0; i < shortcuts.length && shortcut == null; i++)
    {
        if (shortcuts[i].id == btn.id)
        { shortcut = shortcuts[i]; }
    }
    if (shortcut == null)
    {
        console.log("Failed to identify shortcut. Skipping.");
        return;
    }

    // make two webhook requests: one for the color, one for the brightness
    webhook_send("on.color", shortcut.color);
    webhook_send("on.brightness", shortcut.brightness);
}


// ======================= Beacon Operation Objects ======================== //
// Buttons
const beacon_btn_on = document.getElementById("beacon_btn_on");
const beacon_btn_off = document.getElementById("beacon_btn_off");
const beacon_btn_color = document.getElementById("beacon_btn_color");
const beacon_btn_brightness = document.getElementById("beacon_btn_brightness");
beacon_btn_on.addEventListener("click", beacon_btn_on_click);
beacon_btn_off.addEventListener("click", beacon_btn_off_click);
beacon_btn_color.addEventListener("click", beacon_btn_color_click);
beacon_btn_brightness.addEventListener("click", beacon_btn_brightness_click);

// Other items
const beacon_select = document.getElementById("beacon_select");
const beacon_input_color = document.getElementById("beacon_input_color");
const beacon_btn_color_hint = document.getElementById("beacon_btn_color_hint");
const beacon_input_brightness = document.getElementById("beacon_input_brightness");
const beacon_btn_brightness_hint = document.getElementById("beacon_btn_brightness_hint");
const beacon_status = document.getElementById("beacon_status");
beacon_input_color.addEventListener("input", beacon_input_color_input);
beacon_input_brightness.addEventListener("input", beacon_input_brightness_input);
beacon_select.onchange = function() { update_beacon_status(beacon_select.value); }


// ========================== Page Initialization ========================== //
window.onload = function()
{
    // toggle a few listener events to update the page
    beacon_input_color_input();
    beacon_input_brightness_input();

    // set up beacon select options
    beacons.forEach((beacon) =>
    { beacon_select_make_option(beacon); });

    // set up shortcut buttons and register the click event listener for each
    shortcuts.forEach((shortcut) =>
    { shortcut_make_button(shortcut); });
    shortcuts.forEach((shortcut) =>
    {
        const btn = document.getElementById(shortcut.id);
        btn.addEventListener("click", function() { shortcut_btn_click(this); });
    });

    update_beacon_status(beacon_select.value);
};


// ====================== Beacon Operation Listeners ======================= //
// Button event listeners
function beacon_btn_on_click()
{ return webhook_send("on", ""); }
function beacon_btn_off_click()
{ return webhook_send("off", ""); }

// Color-changing button listener.
function beacon_btn_color_click()
{
    // extract the color input value, get rid of the "#" (presumably at the
    // beginning of the string), and take only the first 6 characters. If
    // we've got less than 6 characters, don't send the request
    let color = beacon_input_color.value;
    color = color.replace("#", "");
    if (color.length < 6)
    {
        console.log("Invalid beacon color. Skipping.");
        return;
    }
    color = color.substring(0, 6);

    // make the webhook request
    return webhook_send("on.color", color);
}

// Brightness-changing button listener.
function beacon_btn_brightness_click()
{
    // grab the range input's value and attempt to convert it to an integer
    let b = beacon_input_brightness.value
    let bn = parseInt(b, 10);
    if (bn == NaN || bn < 0 || bn > 100)
    {
        console.log("Invalid beacon brightness. Skipping.");
        return;
    }

    // send the webhook request
    return webhook_send("on.brightness", bn.toString());
}

// Listener for when a new color is selected.
function beacon_input_color_input()
{
    const hint_value = beacon_input_color.value;
    beacon_btn_color_hint.firstChild.data = hint_value.toUpperCase();
    beacon_btn_color_hint.style = "color: " + hint_value;
}

// Listener for when a new brightness is selected.
function beacon_input_brightness_input()
{
    // depending on the length, we'll add some spaces for clean formatting
    let hint_value = beacon_input_brightness.value;
    let diff = 3 - hint_value.length;
    for (let i = 0; i < diff; i++)
    { hint_value = " " + hint_value; }
    // update the button's hint field
    beacon_btn_brightness_hint.firstChild.data = hint_value + "%";
}


// =========================== Helper Functions ============================ //
// Gets the beacon ID from the dropdown menu. Returns null on an invalid value.
function get_beacon_id()
{
    // grab the beacon ID from the dropdown menu and make sure it's an expected
    // value (if not, don't proceed)
    const beacon_id = beacon_select.value;
    let valid_id = false;
    for (let i = 0; i < beacons.length && !valid_id; i++)
    {
        if (beacons[i].id === beacon_id)
        { valid_id = true; }
    }
    
    // return accordingly
    if (valid_id)
    { return beacon_id; }
    return null;
}

// Given a beacon ID, this communicates with the server to get a summary of the
// beacon's last-known status.
async function update_beacon_status(id)
{
    // build the request body and send the POST request
    const request_body = '{"id": "' + id + '"}';
    let response = await fetch(url + "/light/get", {
        method: "POST", body: request_body
    });

    // retrieve the response and parse it as JSON
    let text = await response.text();
    let jdata = JSON.parse(text);

    // if it failed, indicate it
    if (!jdata.success)
    {
        beacon_status.innerHTML = "<b style=\"color: red\">Error:</b> " +
                                  jdata.message;
        return;
    }

    // pair up the ID with the beacon object
    let beacon = null;
    for (let i = 0; i < beacons.length && beacon == null; i++)
    {
        if (beacons[i].id == id)
        { beacon = beacons[i]; }
    }
    if (beacon == null)
    { return; }

    // update the status element's HTML
    const ldata = jdata.data;
    const toggle_string = ldata.toggled == true ? "ON" : "OFF";
    const color_string = "<span style=\"color: #" + ldata.color + "\">#" +
                         ldata.color.toUpperCase() + "</span>";
    const brightness_string = ldata.brightness + "%";
    const html = "<b>" + beacon.name + "</b> [" +
                 toggle_string + ", " + color_string + ", " +
                 brightness_string + "]";
    beacon_status.innerHTML = html;

    // also update the color-picker's color accordingly and the brightness
    // slider's position
    beacon_input_color.value = "#" + ldata.color;
    beacon_input_color_input();
    beacon_input_brightness.value = ldata.brightness;
    beacon_input_brightness_input();

}

// Helper function for sending a webhook request.
async function webhook_send(command, parameter)
{
    let beacon_id = get_beacon_id();
    if (beacon_id == null)
    {
        console.log("Invalid beacon ID. Skipping.");
        return;
    }

    // create a message-body JSON string
    const request_body = '{"command": "' + command +
                 '", "parameter": "' + parameter +
                 '", "light": "' + beacon_id + '"}';

    // send a POST request to the correct server endpoint
    let response = await fetch(url + "/light/set", {
        method: "POST", body: request_body
    });

    // retrieve the response body and attempt to parse it as JSON
    let text = await response.text();
    let jdata = JSON.parse(text);
    
    // on success, refresh the status element
    if (jdata.success)
    { update_beacon_status(beacon_id); }
}

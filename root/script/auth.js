// JS for authentication.
//
//      Connor Shugg

// globals
const url = window.location.protocol + "//" + window.location.host;
const btn = document.getElementById("auth_btn");
const input_username = document.getElementById("auth_input_username");
const input_password = document.getElementById("auth_input_password");
let last_attempt = "";

// add event listener(s)
btn.addEventListener("click", btn_auth_click);

// Listener function for when the authentication button is clicked.
async function btn_auth_click()
{
    // grab the input values and make sure they're non-empty
    let user = input_username.value;
    let key = input_password.value;
    if (key == "" || user == "")
    { return; }

    // if the user-entered key hasn't changed since the last button click,
    // don't do anything
    if (key == last_attempt)
    { return; }

    // send a POST request to the authentication endpoint
    let response = await fetch(url + "/auth/login", {
        method: "POST", body: "{\"username\": \"" + user + "\", \"password\": \"" + key + "\"}"
    });
    last_attempt = key;

    // retrieve the response body and attempt to parse it as JSON
    let text = await response.text();
    let jdata = JSON.parse(text);
    
    // on success, reload the home page
    if (jdata.success)
    { window.location.replace(url + "/"); }
}


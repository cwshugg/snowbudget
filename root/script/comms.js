// Communication helper functions. Used to talk with the backend.
//
//      Connor Shugg

// Get the server's URL
const url = window.location.protocol + "//" + window.location.host;

// Takes in an endpoint string, HTTP method, and JSON message body and sends a
// HTTP request to the server.
async function send_request(endpoint, method, jdata)
{
    // build a request body string, if JSON data was given
    let request_body = null;
    if (jdata)
    { request_body = JSON.stringify(jdata); }

    // send a request to the correct server endpoint
    let response = null;
    if (jdata == null)
    {
        response = await fetch(url + endpoint, {
            method: method
        });
    }
    else
    {
        response = await fetch(url + endpoint, {
            method: method, body: request_body
        });
    }

    // retrieve the response body and attempt to parse it as JSON
    let text = await response.text();
    return JSON.parse(text);
}

// Used to retrieve all budget data from the server.
async function retrieve_data()
{
    data = await send_request("/get/all", "GET", null);
    if (!data.success)
    {
        let message = "failed to retrieve content (" + data.message + ")."
        console.log(message);
    }
    return data;
}


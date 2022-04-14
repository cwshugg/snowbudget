// JS for displaying diagnostic messages to my HTML pages.
//
//      Connor Shugg

// retrieve a reference to the diagnostic div
const diagnostic_div = document.getElementById("diagnostics");

// Clears any diagnostic messages.
function diagnostics_clear(color)
{
    diagnostic_div.innerHTML = "";
}

// Adds an error diagnostic message.
function diagnostics_add_error(message)
{
    let elem = document.createElement("p");
    elem.innerHTML = "<b style=\"color: red\">" + message + "</b>";
    diagnostic_div.appendChild(elem);
}

// Creates a simple error message element to be added to the page.
function diagnostics_add_message(message)
{
    let elem = document.createElement("p");
    elem.innerHTML = "<b>" + message + "</b>";
    diagnostic_div.appendChild(elem);
}

// Creates a success message.
function diagnostics_add_success(message)
{
    let elem = document.createElement("p");
    elem.innerHTML = "<b style=\"color: green\">" + message + "</b>";
    diagnostic_div.appendChild(elem);
}


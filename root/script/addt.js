// JS for the 'add transaction' page.
//
//      Connor Shugg

// Document globals
const addt_btn_cancel = document.getElementById("btn_cancel");

// Invoked when the 'cancel' button is clicked.
function addt_click_cancel()
{
    window.location.replace("home.html");
}

// Window initialization function
window.onload = function()
{
    addt_btn_cancel.addEventListener("click", addt_click_cancel);
}


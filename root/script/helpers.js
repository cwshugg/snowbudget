// A series of helper functions.
//
//      Connor Shugg


// ============================== Conversions =============================== //
// Takes in a float value and returns a US-dollar-formatted string.
function float_to_dollar_string(value)
{
    let formatter = new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return formatter.format(value);
}

function float_to_percent_string(value)
{
    return (value * 100.0) + "%";
}

// Takes in a float/integer timestamp and returns a string formatted as a date.
function timestamp_to_date_string(value)
{
    let date = new Date(value * 1000.0);
    let str = date.getFullYear() + "-";
    str += date.getMonth() + 1 + "-";
    str += date.getDate();
    return str;
}


// ============================= Budget Classes ============================= //
// Returns a float value indicating the current target value, given the btarget.
function btarget_value(btarget, total_income)
{
    if (btarget.type == "percent_income")
    { return total_income * btarget.value; }
    return btarget.value;
}

// ============================= Budget Classes ============================= //
// Returns true if the given class is an expense class.
function bclass_is_expense(bclass)
{
    t = bclass.type.toLowerCase();
    return t === "e" || t === "expense";
}

// Returns true if the given class is an income class.
function bclass_is_income(bclass)
{
    t = bclass.type.toLowerCase();
    return t === "i" || t === "income";
}

// Computes the sum of all the bclass's transactions and returns it.
function bclass_sum(bclass)
{
    let sum = 0.0;
    for (let i = 0; i < bclass.history.length; i++)
    { sum += bclass.history[i].price; }
    return sum;
}

// ================================ Datetime ================================ //
// Returns a Date object, taken from the 'datetime' URL parameter. Returns the
// current datetime if no parameter was found.
function get_datetime_from_url()
{
    // retrieve the datetime from the URL, if it's given. If it's not given,
    // we'll just use the current datetime
    let dt = new Date();
    const params = new URLSearchParams(window.location.search);
    if (params.has("datetime"))
    { dt = new Date(params.get("datetime") * 1000.0); }
    return dt;
}

// Converts the given date to Unix epoch seconds and creates a string for the
// "datetime" URL parameter.
function get_datetime_url_string(dt)
{
    return "datetime=" + (dt.getTime() / 1000.0);
}


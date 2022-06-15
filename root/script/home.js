// JS for communicating with the snowbudget backend.
//
//      Connor Shugg

// Document globals
const bclass_expense_container = document.getElementById("bclass_expenses");
const bclass_income_container = document.getElementById("bclass_income");
const summary_container = document.getElementById("budget_summary");
const btn_add_transaction = document.getElementById("btn_add_transaction");
const btn_add_class = document.getElementById("btn_add_class");
const btn_get_spreadsheet = document.getElementById("btn_get_spreadsheet");
const savings_container = document.getElementById("savings");

// Other globals
let budget_total_income = 0.0;
let budget_rdates = null;

// ============================== Interaction =============================== //
// Invoked when a transaction row is clicked in a budget class table.
function click_transaction_row(ev)
{
    // pull out the correct table row that was clicked so we can find the
    // correct transaction
    let tr = ev.currentTarget;
    // if we couldn't find anything, log and return
    if (tr == null)
    {
        console.log("Couldn't find transaction table row.");
        return;
    }

    // put the ID as a URL parameter and navigate to the edit page
    let transaction_id = tr.id;
    let edit_url = "editt.html?transaction_id=" + transaction_id;
    window.location.replace(edit_url);
}

// Invoked when the 'add transaction' class is clicked.
function click_add_transaction(ev)
{
    window.location.replace("addt.html");
}

// Invoked when the 'add class' button is clicked
function click_add_class(ev)
{
    window.location.replace("addc.html");
}

// Invoked when the 'get spreadsheet' button is clicked.
function click_get_spreadsheet(ev)
{
    retrieve_spreadsheet();
}


// ============================= HTML Elements ============================== //
// Used to create a simply HTML error message.
function make_error_message(msg)
{
    return "<p><b style=\"color: red\">Error:</b> " + msg + "</p>";
}

// Makes a collapsible button element with the given ID and text.
function make_collapsible_button(id, text, rtext, classes, rclasses)
{
    // create the button and set all appropriate fields
    let btn = document.createElement("button");
    btn.id = id;
    btn.className = "collapsible-button " + classes;
    btn.innerHTML = text;

    // create the indicator and append it
    let span = document.createElement("span");
    span.className = "collapsible-button-indicator " + rclasses;
    span.innerHTML = rtext;
    btn.appendChild(span);
    return btn;
}

// Makes a collapsible content element with the given ID.
function make_collapsible_content(id)
{
    let div = document.createElement("div");
    div.id = id;
    div.className = "collapsible-content";
    return div;
}

// Puts together HTML to be stored in a budget class's collapsible content
// section. Acts as a menu for the budget class.
function make_bclass_menu(bclass)
{
    // create a div to contain the menu
    let div = document.createElement("div");
    div.className = "button-container";

    // add the description to the div
    let desc = document.createElement("p");
    desc.innerHTML = "<i>" + bclass.description + "</i>";
    div.appendChild(desc);

    // add another line that tells if the class is under or over target
    if (bclass.target)
    {
        let tp = document.createElement("p");
        tval = btarget_value(bclass.target, budget_total_income);
        tdiff = bclass_sum(bclass) - tval;

        // now, come up with an appropriate message
        tp.innerHTML = "This class is ";
        if (tdiff == 0.0)
        { tp.innerHTML += "<i>exactly</i> on target."; }
        else if (tdiff < 0.0)
        {
            // choose an appropriate color depending on the type of class
            let color = "var(--color-income1)";
            if (bclass_is_income(bclass))
            { color = "red"; }
            tp.innerHTML += "<span style=\"color: " + color + "\">under</span> ";
            tp.innerHTML += "the target by " + float_to_dollar_string(Math.abs(tdiff)) + ".";
        }
        else
        {
            // choose an appropriate color depending on the type of class
            let color = "red";
            if (bclass_is_income(bclass))
            { color = "var(--color-income1)"; }
            tp.innerHTML += "<span style=\"color: " + color + "\">over</span> ";
            tp.innerHTML += "the target by " + float_to_dollar_string(Math.abs(tdiff)) + ".";
        }
        div.appendChild(tp);
    }
    
    return div;
}

// Puts together HTML to be placed at the bottom of a budget class's dropdown
// content box.
function make_bclass_bottom_menu(bclass)
{
    const div = document.createElement("div");
    div.className = "button-container";

    // add a button to edit the class
    let btn_edit = document.createElement("button");
    btn_edit.id = bclass.id + "_btn_edit";
    btn_edit.className = "button-main button-light";
    btn_edit.innerHTML = "Edit Class";
    div.appendChild(btn_edit);

    // give the button a callback function
    btn_edit.addEventListener("click", function() {
        // navigate to the edit page with the correct ID
        let edit_url = "editc.html?class_id=" + bclass.id;
        window.location.replace(edit_url);
    });
    
    return div;
}

// Puts together a HTML element containing a summary of all transactions within
// the given budget class.
function make_bclass_history(bclass)
{
    // if there are no transactions recorded, make a simple element and return
    if (bclass.history.length == 0)
    {
        let msg = document.createElement("p");
        msg.innerHTML = "";
        return msg;
    }

    // sort the history by timestamp
    bclass.history.sort(function(t1, t2) { return t2.timestamp - t1.timestamp; });

    // create a div to contain the table
    let tdiv = document.createElement("div");
    tdiv.className = "ttable-container";

    // create a table and set up its class names
    let table = document.createElement("table");
    table.className = "ttable";
    if (bclass_is_expense(bclass))
    { table.className += " color-expense3"; }
    else if (bclass_is_income(bclass))
    { table.className += " color-income3"; }

    // set up the first row (the headers)
    let row1 = document.createElement("tr");
    row1.className = "ttable-row";
    let columns = ["Date", "Price", "Vendor", "Description"];
    for (let i = 0; i < columns.length; i++)
    {
        let th = document.createElement("th");
        th.className = "ttable-header";
        // set up bolded text with a specific text color for the cell
        span = document.createElement("span");
        span.className = "color-text1";
        span.innerHTML = "<b>" + columns[i] + "</b>";
        th.appendChild(span);
        // append the entry to the row
        row1.appendChild(th);
    }
    table.appendChild(row1);

    // now, iterate across each transaction in the class and add it to the table
    for (let i = 0; i < bclass.history.length; i++)
    { 
        // create a 'tr' object and set up the array of cell values
        let t = bclass.history[i];
        let row = document.createElement("tr");
        row.className = "ttable-transaction-row";
        row.id = t.id;

        // build a price string that includes whether or not the transaction is
        // a recurring transaction
        let pstr = float_to_dollar_string(t.price);
        if (t.recurring)
        { pstr += " (<span style=\"color: orange\">R</span>)"; }

        // create an array of values for this transaction's row
        let values = [timestamp_to_date_string(t.timestamp),
                      pstr, t.vendor, t.description];
        
        // add each cell value as a new 'td' element
        for (let j = 0; j < values.length; j++)
        {
            let td = document.createElement("td");
            td.className = "ttable-cell";
            // make a paragraph element with a certain text color for the cell
            span = document.createElement("span");
            span.className = "color-text1";
            span.innerHTML = values[j];
            td.appendChild(span);
            // append the entry to the row
            row.appendChild(td);
        }

        // add a click listener to the row (so we can click on the row)
        row.addEventListener("click", click_transaction_row);
        
        // append the row to the table
        table.appendChild(row);
    }
    
    // put the table into the container and return it
    tdiv.appendChild(table);
    return tdiv;
}

// Builds and returns one or more charts (with Chart.js) for a given class.
function make_bclass_charts(bclass)
{
    // create a div and make sure this budget class actually has transactions
    const div = document.createElement("div");
    if (bclass.history.length <= 1)
    { return div; }

    // sort the bclass's history and set up the div's properties
    bclass.history.sort(function(t1, t2) { return t2.timestamp - t1.timestamp; });
    div.className = "chart-container";

    // override a few chart globals
    Chart.defaults.global.defaultFontColor = "rgb(225, 225, 255)";

    // take the reset date array and compute the previous reset date that passed
    // most recently (it's at the end of the array with the year increased by
    // one)
    let rdate1 = new Date(budget_rdates[budget_rdates.length - 1] * 1000);
    rdate1.setFullYear(rdate1.getFullYear() - 1);
    rdate1 = rdate1.getTime() / 1000
    const rdate2 = budget_rdates[0];
    let now = new Date().getTime() / 1000;

    // ----------------------- Total-Over-Time Chart ------------------------ //
    let chart1_data = [];
    let chart1_labels = [];
    let chart1_total = 0.0;
    let time_idx = rdate1;
    let chart1_enddate = rdate2;
    if (now < chart1_enddate)
    { chart1_enddate = now + (3600 * 24); }
    while (timestamp_to_date_string(time_idx) !== timestamp_to_date_string(chart1_enddate))
    {
        // iterate through all transactions - if the day matches the current one
        // we'll add its price to the running total
        let total = 0.0;
        for (let i = 0; i < bclass.history.length; i++)
        {
            const transaction = bclass.history[i];
            if (timestamp_to_date_string(time_idx) === timestamp_to_date_string(transaction.timestamp))
            { total += transaction.price; }
        }
        chart1_total += total;

        // add to chart labels/data and increment the time index
        chart1_labels.push(timestamp_to_date_string(time_idx));
        chart1_data.push(chart1_total);
        time_idx += 3600 * 24; // increase by one day
    }

    // create an array of dataset JSON objects to pass to the chart object
    chart1_datasets = [{
        label: "Total Over Time",
        data: chart1_data,
        borderColor: "rgb(0, 190, 225)",
        backgroundColor: "rgba(104, 133, 232, 0.1)",
        lineTension: 0
    }];

    // if this budget class has a target, we'll compute its value and draw it
    // as a horizontal line on this graph
    if (bclass.target)
    {
        let tval = btarget_value(bclass.target, budget_total_income);
        // create an array of data points for each day, all holding the target
        let chart1_target_data = [];
        for (let i = 0; i < chart1_data.length; i++)
        { chart1_target_data.push(tval); }

        // pick out an appropriate color based on where we are relative to the
        // target
        let bcolor = "rgb(180, 180, 180)";
        const bcolor_good = "rgb(0, 215, 0)";
        const bcolor_bad = "rgb(255, 110, 110)";
        const bsum = bclass_sum(bclass);
        if (bsum < tval)
        {
            if (bclass_is_expense(bclass))
            { bcolor = bcolor_good; }
            else
            { bcolor = bcolor_bad; }
        }
        else if (bsum > tval)
        {
            if (bclass_is_expense(bclass))
            { bcolor = bcolor_bad; }
            else
            { bcolor = bcolor_good; }
        }

        // push to the chart's datasets
        chart1_datasets.push({
            label: "Target",
            data: chart1_target_data,
            borderColor: bcolor,
            lineTension: 0
        });
    }

    
    // first, we'll create the total-over-time chart
    const chart1_canvas = document.createElement("canvas");
    chart1_canvas.className = "chart-main";
    chart1_canvas.id = bclass.id + "_chart1";
    const chart1_ctx = chart1_canvas.getContext("2d");
    const chart1 = new Chart(chart1_ctx, {
        type: "line",
        data: {
            labels: chart1_labels,
            datasets: chart1_datasets
        },
        options: {
            title: {
                display: true,
                text: "Total Over Time (across current cycle)"
            },
            scales: {
                xAxes: [{
                    gridLines: {
                        display: true,
                        color: "rgb(100, 100, 100)"
                    }
                }],
                yAxes: [{
                    gridLines: {
                        display: true,
                        color: "rgb(100, 100, 100)"
                    }
                }],
            }
        }
    });
    div.appendChild(chart1_canvas);
    
    return div;
}

// Builds and returns a table containing savings information.
function make_savings_table(savings_categories)
{
    // create a div to contain the table
    let tdiv = document.createElement("div");
    tdiv.className = "ttable-container";

    // create a table and set up its class names
    let table = document.createElement("table");
    table.className = "ttable";
    table.className += " color-acc2";

    // set up the first row (the headers)
    let row1 = document.createElement("tr");
    row1.className = "ttable-row";
    let columns = ["Category", "Percentage", "Amount to Save"];
    for (let i = 0; i < columns.length; i++)
    {
        let th = document.createElement("th");
        th.className = "ttable-header";
        // set up bolded text with a specific text color for the cell
        span = document.createElement("span");
        span.className = "color-text1";
        span.innerHTML = "<b>" + columns[i] + "</b>";
        th.appendChild(span);
        // append the entry to the row
        row1.appendChild(th);
    }
    table.appendChild(row1);

    // iterate across each category and fill in each row
    for (let i = 0; i < savings_categories.length; i++)
    { 
        let row = document.createElement("tr");
        row.className = "ttable-transaction-row";

        // create an array of values for this transaction's row
        let values = [savings_categories[i].category,
                      float_to_percent_string(savings_categories[i].percent),
                      float_to_dollar_string(savings_categories[i].amount)]
        
        // add each cell value as a new 'td' element
        for (let j = 0; j < values.length; j++)
        {
            let td = document.createElement("td");
            td.className = "ttable-cell";
            // make a paragraph element with a certain text color for the cell
            span = document.createElement("span");
            span.className = "color-text1";
            span.innerHTML = values[j];
            td.appendChild(span);
            // append the entry to the row
            row.appendChild(td);
        }
        // append the row to the table
        table.appendChild(row);
    }
    
    // put the table into the container and return it
    tdiv.appendChild(table);
    return tdiv;
}


// =============================== UI Updates =============================== //
// Used to refresh the summary written at the top of the page.
async function summary_refresh(bclasses, reset_dates)
{
    summary_container.innerHTML = "";
    // we'll compute some statistics
    let total_expense = 0.0;    // total expense costs
    let total_income = 0.0;     // total income gain
    let total = 0.0;            // net gain/loss total
 
    // iterate through every budget class
    for (let i = 0; i < bclasses.length; i++)
    {
        // increment the sums for all categories
        let sum = bclass_sum(bclasses[i]);
        if (bclass_is_expense(bclasses[i]))
        { total_expense += sum; }
        else if (bclass_is_income(bclasses[i]))
        { total_income += sum; }
    }
    total = total_income - total_expense;
    
    let elem = document.createElement("p");
    // create an element for the total expenses
    let total_expense_elem = document.createElement("b");
    total_expense_elem.className = "color-expense1";
    total_expense_elem.innerHTML = "Total expenses: ";
    elem.appendChild(total_expense_elem);
    elem.innerHTML += float_to_dollar_string(total_expense) + "<br>";

    // create an element for the total income
    let total_income_elem = document.createElement("b");
    total_income_elem.className = "color-income1";
    total_income_elem.innerHTML = "Total income: ";
    elem.appendChild(total_income_elem);
    elem.innerHTML += float_to_dollar_string(total_income) + "<br>";

    // create an element for the net value
    let total_elem = document.createElement("b");
    // create a specific message depending on the total net value
    let net_str = "Broken even!";
    if (total < 0.0)
    {
        total_elem.className += "color-acc4";
        net_str = "In-the-hole: ";
    }
    else if (total > 0.0)
    {
        total_elem.className += "color-acc2";
        net_str = "Extra cash: ";
    }
    total_elem.innerHTML = net_str;
    // add to the main element, then add the 'total' value, if necessary
    elem.appendChild(total_elem);
    if (total != 0.0)
    { elem.innerHTML += float_to_dollar_string(total); }
    elem.innerHTML += "<br>";

    // grab the nearest reset date and create an element to display it
    let next_date_elem = document.createElement("b");
    next_date_elem.className = "color-acc1";
    next_date_elem.innerHTML = "Next reset: ";
    elem.appendChild(next_date_elem);
    elem.innerHTML += timestamp_to_date_string(reset_dates[0]);

    // append to the main div to add to the document
    summary_container.appendChild(elem);
}

// Used to refresh the savings menu.
async function savings_refresh(bclasses, savings_categories)
{
    // first, compute the income and expense sums
    let esum = 0.0;
    let isum = 0.0;
    for (let i = 0; i < bclasses.length; i++)
    {
        let sum = bclass_sum(bclasses[i]);
        if (bclass_is_expense(bclasses[i]))
        { esum += sum; }
        else if (bclass_is_income(bclasses[i]))
        { isum += sum; }
    }
    sumdiff = isum - esum;
    
    // compute an array of the savings amounts for each category
    savings_sum = 0.0;
    for (let i = 0; i < savings_categories.length; i++)
    {
        let save_amount = 0.0;
        if (sumdiff > 0.0)
        { save_amount = savings_categories[i].percent * sumdiff; }
        // set the field in each category, and add to our savings sum
        savings_categories[i].amount = save_amount;
        savings_sum += save_amount;

    }
 
    // create the collapsible button and content
    savings_btn = make_collapsible_button("savings_btn", "Savings",
                                          float_to_dollar_string(savings_sum),
                                          "color-acc2 font-main", "color-acc1");
    savings_content = make_collapsible_content("savings_content");

    // add a line of intro information
    let intro = document.createElement("p");
    intro.innerHTML = "Take your savings and split them into these categories.";
    if (sumdiff <= 0.0)
    { intro.innerHTML = "You don't have extra money for savings."; }
    savings_content.appendChild(intro);

    // now, build a table with our savings data
    let table = make_savings_table(savings_categories); 
    savings_content.appendChild(table);

    // add the elements to the page and initialize the collapsible
    savings_container.appendChild(savings_btn);
    savings_container.appendChild(savings_content);
    collapsible_init(savings_btn);

}

// Used to refresh the main menu.
async function menu_refresh(bclasses)
{
    // enable the buttons
    btn_add_transaction.disabled = false;
    btn_add_class.disabled = false;
    btn_get_spreadsheet.disabled = false;

    // add click listeners to the buttons
    btn_add_transaction.addEventListener("click", click_add_transaction);
    btn_add_class.addEventListener("click", click_add_class);
    btn_get_spreadsheet.addEventListener("click", click_get_spreadsheet);
}

// Used to update a single budget class UI element.
async function budget_class_refresh(bclass)
{
    // take the budget class' ID and look for an element within the main div.
    // If one doesn't exist, we'll create it and add it to the correct div
    bclass_div = document.getElementById(bclass.id);
    if (!bclass_div)
    {
        bclass_div = document.createElement("div");
        bclass_div.id = bclass.id;
        // depending on the type, append to the correct child
        if (bclass_is_expense(bclass))
        { bclass_expense_container.appendChild(bclass_div); }
        else if (bclass_is_income(bclass))
        { bclass_income_container.appendChild(bclass_div); }
        else
        { console.log("Found budget class of unknown type: " + bclass.id); }
    }

    // look for the collapsible button corresponding to the bclass. If we can't
    // find it, we'll create one
    btn_id = bclass.id + "_btn";
    bclass_btn = document.getElementById(btn_id);
    if (!bclass_btn)
    {
        // pick out classes based on if it's an expense or income class
        classes = "font-main";
        rclasses = "font-main";
        if (bclass_is_expense(bclass))
        {
            classes += " color-expense1";
            rclasses += " color-expense2";
        }
        else if (bclass_is_income(bclass))
        {
            classes += " color-income1";
            rclasses += " color-income2";
        }

        // create the button and add it to the div (making the right-hand text
        // the total dollar value of the class, factoring in the target, if
        // one exists for this class)
        let bcsum = bclass_sum(bclass);
        let sumstr = float_to_dollar_string(bcsum);
        let tstr = "";
        if (bclass.target)
        {
            tstr += " / " + float_to_dollar_string(btarget_value(bclass.target, budget_total_income));
            tstr = "<span class=\"color-text2\">" + tstr + "</span>";
        }
        bclass_btn = make_collapsible_button(btn_id, bclass.name, sumstr + tstr,
                                             classes, rclasses);
        bclass_div.appendChild(bclass_btn);
    }

    // look for the collapsible content corresponding to the bclass. If we
    // can't find it, we'll create one
    content_id = bclass.id + "_content";
    bclass_content = document.getElementById(content_id);
    if (!bclass_content)
    { 
        bclass_content = make_collapsible_content(content_id);
        bclass_div.appendChild(bclass_content);
        collapsible_init(bclass_btn);
        
        // add a menu to the bclass's content section, then add a listing of
        // the class's transaction history
        bclass_content.appendChild(make_bclass_menu(bclass));
        bclass_content.appendChild(make_bclass_history(bclass));
        bclass_content.appendChild(make_bclass_charts(bclass));
        bclass_content.appendChild(make_bclass_bottom_menu(bclass));
    }
}

// Used to update ALL budget class UI elements.
async function budget_classes_refresh(bclasses)
{
    // iterate through each budget class and refresh it
    for (let i = 0; i < bclasses.length; i++)
    { budget_class_refresh(bclasses[i]); }
}


// ============================= Initialization ============================= //
// Main initializer for the entire page.
async function ui_init()
{
    diagnostics_add_message("Contacting server...");
    let data = await retrieve_data();
    if (!data)
    {
        // show an error message
        diagnostics_clear();
        diagnostics_add_error("Failed to retrieve data from server.");
        return;
    }
    // also, look up the reset dates
    let rdates = await send_request("/get/resets", "GET", null);
    if (!rdates)
    {
        diagnostics_clear();
        diagnostics_add_error("Failed to retrieve reset dates from the server.");
        return;
    }
    budget_rdates = rdates.payload;
    
    // also, look up the savings categories
    let scs = await send_request("/get/savings", "GET", null);
    if (!scs)
    {
        diagnostics_clear();
        diagnostics_add_error("Failed to retrieve savings categories from the server.");
        return;
    }
    diagnostics_clear();

    // extract the payload and sort them (budget classes) by name
    let bclasses = data.payload;
    bclasses.sort(function(c1, c2) { return c1.name.localeCompare(c2.name); });

    // extract the reset dates and sort them by timestamp
    let reset_dates = rdates.payload;
    reset_dates.sort(function(rd1, rd2) { return rd1 - rd2; });
    
    // extract the savings categories and sort by name
    let savings_categories = scs.payload;
    savings_categories.sort(function(sc1, sc2) { return sc1.category.localeCompare(sc2.category); });

    // compute total income
    budget_total_income = 0.0;
    for (let i = 0; i < bclasses.length; i++)
    {
        if (bclass_is_income(bclasses[i]))
        { budget_total_income += bclass_sum(bclasses[i]); }
    }

    // pass the budget classes to refresh functions
    summary_refresh(bclasses, reset_dates);
    menu_refresh(bclasses);
    savings_refresh(bclasses, savings_categories);
    budget_classes_refresh(bclasses);
}

// Function that's invoked upon window-load.
window.onload = function()
{
    ui_init();
}


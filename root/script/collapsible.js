// JS that handles opening/closing collapsible content sections.
// Source: https://www.w3schools.com/howto/howto_js_collapsible.asp
//
//      Connor Shugg

const collapsible_indicator_defaults = ["+", "-"];

// Takes in a reference to an indicator element and returns true if the inner
// HTML holds the default collapsible values.
function collapsible_indicator_is_default(indicator)
{
    // search the default value array - if we find something return true
    return collapsible_indicator_defaults.indexOf(indicator.innerHTML) > -1;
}

// Takes in a collapsible-button object and initializes it.
function collapsible_init(cbutton)
{
    // add a 'click' listener that does the work
    cbutton.addEventListener("click", function()
    {
        this.classList.toggle("active");        // make the button 'active'
        let content = this.nextElementSibling;  // get content div
        let indicator = null;                   // "+"/"-" indicator
        
        // iterate through the child nodes and find the indicator
        for (let j = 0; j < this.childNodes.length; j++)
        {
            if (this.childNodes[j].className === "collapsible-button-indicator")
            {
                indicator = this.childNodes[j];
                break;
            }
        }
        
        // take the collapsible content div and flip its display
        if (content.style.display === "block")
        {
            content.style.display = "none";
            // only change the indicator text if it has a default value in it
            if (indicator != null && collapsible_indicator_is_default(indicator))
            { indicator.innerHTML = "+"; }
        }
        else
        {
            content.style.display = "block";
            // only change the indicator text if it has a default value in it
            if (indicator != null && collapsible_indicator_is_default(indicator))
            { indicator.innerHTML = "-"; }
        }
    });
}


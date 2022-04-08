// JS that handles opening/closing collapsible content sections.
// Source: https://www.w3schools.com/howto/howto_js_collapsible.asp
//
//      Connor Shugg

// grab all buttons with the correct class, then iterate through them
let buttons = document.getElementsByClassName("collapsible-button");
for (let i = 0; i < buttons.length; i++)
{
    // add a 'click' listener that does the work
    buttons[i].addEventListener("click", function()
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
            if (indicator != null)
            { indicator.innerHTML = "+"; }
        }
        else
        {
            content.style.display = "block";
            if (indicator != null)
            { indicator.innerHTML = "-"; }
        }
    });
}
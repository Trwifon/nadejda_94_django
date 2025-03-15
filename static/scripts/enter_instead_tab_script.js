
// JavaScript function to move to the next input field
function handleEnter(event) {
    // Check if Enter key (key code 13) is pressed
    if (event.key === 'Enter') {
        event.preventDefault(); // Prevent form submission
        let form = event.target.form; // Get the form element
        let index = Array.prototype.indexOf.call(form, event.target); // Find the current field index
        let nextField = form.elements[index + 1]; // Move to the next field
        if (nextField) {
            nextField.focus();
            if (nextField.tagName === 'INPUT' || nextField.tagName === 'TEXTAREA') {
                nextField.select(); // Select the text inside the input/textarea
            }
        }
    }
}

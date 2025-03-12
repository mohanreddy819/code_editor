// Initialize CodeMirror
const editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
    lineNumbers: true,
    mode: "python",  // Default mode
    theme: "default",
});

// Function to update mode when language changes
document.getElementById("language-selector").addEventListener("change", function () {
    const selectedLanguage = this.value;
    editor.setOption("mode", selectedLanguage);
});

// Function to run code
function runCode() {
    const code = editor.getValue();
    console.log("code before sending: ", code)
    const language = document.getElementById("language-selector").value;
    const outputDiv = document.getElementById("output");

    outputDiv.innerHTML = "";  // Clear previous output
    outputDiv.style.color = "black"; // Reset color to black

    if (language === "javascript") {
        try {
            // Wrap code in a function for better error handling
            const result = new Function(code)();
            outputDiv.innerHTML = `<pre>${result !== undefined ? result : "Code executed successfully"}</pre>`;
        } catch (error) {
            outputDiv.innerHTML = `<pre>Error: ${error.message}</pre>`;
            outputDiv.style.color = "red"; // Change text to red if error occurs
        }
    } else {
        // Send Python code to backend
        fetch("/runcode", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code })
        })
        .then(response => response.json())
        .then(data => {
            console.log("Received response:", data); 
            if (data.error) {
                outputDiv.innerHTML = `<pre>Error: ${data.error}</pre>`;
            outputDiv.style.color = "red"; 	
            } else {
                outputDiv.innerHTML = `<pre>${data.output}</pre>`;

            }
        })
        .catch(error => {
            console.error(error);
            outputDiv.innerText = "Error occurred while running the code.";
        outputDiv.style.color = "red";
        });
    }
}  
function stopExecution() {
    fetch("/stop_execution", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("output").innerHTML = `<pre>${data.message}</pre>`;
    })
    .catch(error => console.error("Failed to stop execution:", error));
}    


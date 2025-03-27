
const editor = CodeMirror.fromTextArea(document.getElementById("code-editor"), {
    lineNumbers: true,
    mode: "python",  
    theme: "ayu-dark",
});


document.getElementById("language-selector").addEventListener("change", function () {
    const selectedLanguage = this.value;
    editor.setOption("mode", selectedLanguage);
});


function runCode() {
    const code = editor.getValue();
    console.log("code before sending: ", code)
    const language = document.getElementById("language-selector").value;
    const outputDiv = document.getElementById("output");

    outputDiv.innerHTML = "";  
    outputDiv.style.color = "black"; 

    if (language === "javascript") {
        try {
            
            const result = new Function(code)();
            outputDiv.innerHTML = `<pre>${result !== undefined ? result : "Code executed successfully"}</pre>`;
        } catch (error) {
            outputDiv.innerHTML = `<pre>Error: ${error.message}</pre>`;
            outputDiv.style.color = "red"; 
        }
    } else {
        
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


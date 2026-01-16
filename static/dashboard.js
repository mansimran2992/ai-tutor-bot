function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const status = document.getElementById("upload-status");

    if (!fileInput.files.length) {
        status.textContent = "❌ Please select a file first.";
        status.style.color = "red";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    status.textContent = "⏳ Uploading file...";
    status.style.color = "orange";

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        status.textContent = "✅ " + data.status;
        status.style.color = "green";
    })
    .catch(() => {
        status.textContent = "❌ Upload failed.";
        status.style.color = "red";
    });
}

function sendMessage() {
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user");
    input.value = "";

    fetch("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
    })
    .then(res => res.json())
    .then(data => {
        addMessage(data.reply, "bot");
    });
}

function addMessage(text, sender) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = `message ${sender}`;
    div.textContent = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

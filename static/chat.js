var converter = new showdown.Converter();
const chatContainer = document.getElementById("chat-container");
var fileList = []

function scrollToBottom() {
  const chatMessages = chatContainer.querySelectorAll(".message-container");
  const lastMessage = chatMessages[chatMessages.length - 1];
  if (lastMessage) {
    lastMessage.scrollIntoView();
  }
}

function addMessage(message, isSender) {
  if (chatContainer.classList.contains("flex")) {
    chatContainer.classList.remove("flex");
    chatContainer.classList.remove("justify-center");
    chatContainer.classList.remove("items-center");
    chatContainer.innerHTML = "";
  }
  const messageElement = document.createElement("div");
  messageElement.classList.add(
    "message-container",
    isSender ? "sender" : "receiver",
    "flex",
    "items-start",
    "mb-4"
  );

  const avatar = document.createElement("img");
  avatar.src = isSender ? "/static/sender-avatar.png" : "/static/receiver-avatar.png";
  avatar.classList.add(
    "avatar",
    "rounded-full",
    "w-10",
    "h-10",
    "mr-2",
    "border-2",
    "border-black"
  );
  messageElement.appendChild(avatar);

  const messageBubble = document.createElement("div");
  messageBubble.classList.add(
    "message-bubble",
    isSender ? "bg-[#131314]" : "bg-[#29293d]",
    isSender ? "bg-opacity-80" : "bg-opacity-60",
    "rounded-lg",
    "py-3",
    "px-4",
    "w-auto",
    "max-w-[90%]"
  );
  messageBubble.innerHTML = message;
  messageElement.appendChild(messageBubble);

  chatContainer.appendChild(messageElement);

  scrollToBottom();
}

function handleUserInput(event) {
  if (event.key === "Enter") {
    sendMessage();
  }
}

function handleFileUpload() {
  const fileInput = document.getElementById("file-upload");
  const files = fileInput.files;
  console.log(files.length)
  for (let i=0;i<files.length;++i) {
    const file = files[i];
    const formData = new FormData();
    formData.append("document", file);

    fetch("http://127.0.0.1:5000/input_m", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.text())
      .then((result) => {
        console.log("File upload response:", result);
        addMessage(`Uploaded: ${file.name}`, true);
        fileList.push(file.name);
      })
      .catch((error) => console.error("Error:", error));
  }
}

function sendMessage() {
  const userInput = document.getElementById("user-input").value;
  if (userInput.trim() === "") {
  }

  addMessage(userInput, true);

  const messageElement = document.createElement("div");
  messageElement.classList.add(
    "message-container",
    "receiver",
    "flex",
    "items-start",
    "mb-4"
  );

  const avatar = document.createElement("img");
  avatar.src = "/static/receiver-avatar.png";
  avatar.classList.add(
    "avatar",
    "rounded-full",
    "w-10",
    "h-10",
    "mr-2",
    "border-2",
    "border-black"
  );
  messageElement.appendChild(avatar);

  const messageBubble = document.createElement("div");
  messageBubble.classList.add(
    "message-bubble",
    "bg-[#29293d]",
    "bg-opacity-60",
    "rounded-lg",
    "py-3",
    "px-4",
    "w-auto",
    "max-w-[80%]"
  );
  messageBubble.innerHTML = "Loading...";
  messageElement.appendChild(messageBubble);

  chatContainer.appendChild(messageElement);
  scrollToBottom();
  
  fetch("http://127.0.0.1:5000/input_t", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: userInput, fileList: fileList }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok"); // Handling HTTP error statuses
      }
      return response.text(); // Assuming server responds with text
    })
    .then((data) => {
      console.log("Server response:", data);
      chatContainer.removeChild(messageElement);
      addMessage(data, false); // Optionally, display the server's response
    })
    .catch((error) => {
      console.error("Error:", error);
      chatContainer.removeChild(messageElement);
      addMessage(`Error: ${error.message}`, false); // Display error message in the chat interface
    });

  document.getElementById("user-input").value = ""; // Clear input after sending
  fileList = []
}

function fetchString() {
  fetch("http://127.0.0.1:5000/send_string")
    .then((response) => response.text())
    .then((data) => {
      addMessage(data, false); // Displaying the fetched string from send_string endpoint
    })
    .catch((error) => console.error("Error fetching from send_string:", error));
}

// function createTerminalContent() {
//     const terminalDiv = document.getElementById('terminal');

//     // Clear any existing content
//     terminalDiv.innerHTML = '';

//     // Add terminal output
//     const filesRunning = ["npm run start", "Node.js v14.17.0", "Watching for changes..."];
//     filesRunning.forEach(file => {
//         const p = document.createElement('p');
//         p.textContent = file;
//         p.classList.add('p-4', 'font-mono', 'text-white');
//         terminalDiv.appendChild(p);
//     });
// }

document.addEventListener("DOMContentLoaded", function () {
  // createTerminalContent();
  const sendButton = document.getElementById("send-btn");
  const fileUploadInput = document.getElementById("file-upload");
  const userInput = document.getElementById("user-input");

  sendButton.addEventListener("click", sendMessage);
  fileUploadInput.addEventListener("change", handleFileUpload);
  userInput.addEventListener("keypress", handleUserInput);
});

document.getElementById("user-input").addEventListener("focus", function () {
  document.getElementById("container").classList.add("outline-blue");
});

document.getElementById("user-input").addEventListener("blur", function () {
  document.getElementById("container").classList.remove("outline-blue");
});


const fileTree = document.getElementById("fileTree");

function createFileTree(files, parent) {
  parent.innerHTML = "";
  files.forEach((file) => {
    const li = document.createElement("li");
    li.classList.add("pl-4", "py-2", "text-lg");

    const span = document.createElement("span");
    span.classList.add("cursor-pointer", "text-white");
    span.innerHTML = file.children.length
      ? `<i class="fas fa-folder mr-1 text-white"></i>${file.name}`
      : `<i class="fas fa-file mr-1 text-white"></i>${file.name}`;
    span.addEventListener("click", () => {
      if (file.children.length) {
        const icon = span.querySelector("i");
        icon.classList.toggle("fa-folder-open");
        icon.classList.toggle("fa-folder");
        const ul = li.querySelector("ul");
        if (ul) ul.classList.toggle("hidden");
      } else {
        // Send POST request to backend server
        openFile(file.path);
      }
    });

    li.appendChild(span);

    if (file.children) {
      const ul = document.createElement("ul");
      ul.classList.add("hidden");
      createFileTree(file.children, ul);
      li.appendChild(ul);
    }

    parent.appendChild(li);
  });
}

function openFile(filePath) {
  // Example of sending a POST request using fetch API
  fetch("http://127.0.0.1:5000/open-file", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ filePath: filePath }),
  })
    .then((response) => {
      if (response.ok) {
        console.log("File path sent to backend successfully.");
      } else {
        console.error("Failed to send file path to backend.");
      }
    })
    .catch((error) => {
      console.error("Error sending file path to backend:", error);
    });
}

function fetch_tree() {
  fetch("http://127.0.0.1:5000/get-json")
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      createFileTree(data.children, fileTree);
      return data;
    })
    .catch((error) => {
      // Handle errors here
      console.error("There was a problem with the fetch operation:", error);
    });
}

fetch_tree();

setInterval(fetch_tree, 30000);

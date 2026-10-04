const promptInput = document.getElementById("promptInput");
const mediaType = document.getElementById("mediaType");
const generateBtn = document.getElementById("generateBtn");
const statusBox = document.getElementById("status");
const mediaPreview = document.getElementById("mediaPreview");

generateBtn.addEventListener("click", async () => {
  const prompt = promptInput.value.trim();
  if (!prompt) {
    statusBox.textContent = "Please type a prompt first.";
    return;
  }

  statusBox.textContent = "Generating...";
  mediaPreview.classList.add("hidden");
  mediaPreview.innerHTML = "";

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        prompt,
        media_type: mediaType.value || null
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Generation failed");
    }

    const filePath = data.file_path.replace(/\\/g, "/");
    const url = `http://localhost:8000/${filePath}`;

    statusBox.textContent = data.message || "Success!";

    if (data.media_type === "image") {
      mediaPreview.innerHTML = `<img src="${url}" alt="Generated image" />`;
    } else if (data.media_type === "pdf") {
      mediaPreview.innerHTML = `<iframe src="${url}" width="100%" height="600px"></iframe>`;
    } else if (data.media_type === "video") {
      mediaPreview.innerHTML = `<video controls src="${url}" width="100%"></video>`;
    }

    mediaPreview.classList.remove("hidden");
  } catch (error) {
    statusBox.textContent = "Error: " + error.message;
  }
});

# AI Media Chatbot

A free, local-first Python app that creates:
- images
- PDF files
- videos

from a simple text prompt.

No paid API key is required.

## Features

- FastAPI backend
- prompt-to-media routing
- local image generation via open-source diffusion models (optional)
- PDF generation using ReportLab
- video generation using OpenCV and Pillow
- simple browser interface

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the configuration file:
   ```bash
   cp .env.example .env
   ```

4. Run the app:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Open your browser at:
   ```text
   http://localhost:8000
   ```

## Example prompts

- "Create a cinematic poster of a futuristic city at sunset"
- "Generate a PDF report about solar energy benefits"
- "Make a short video of a glowing cyberpunk skyline"

## Free image generation notes

This app is designed to work without paying for an API. It tries to use an open-source local diffusion model via `diffusers` when available.

If the model is not installed or available, the app automatically falls back to a generated placeholder graphic so the app still works.

## Project layout

```text
app/
  config.py
  main.py
  models.py
  services/
    media_generator.py
static/
  index.html
  app.js
requirements.txt
README.md
```

## Important

Image generation with open-source models may require a GPU or a long CPU download time. The fallback mode ensures the app is still usable immediately.

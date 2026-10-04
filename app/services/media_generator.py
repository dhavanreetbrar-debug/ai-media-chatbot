import os
import textwrap
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.config import APP_STORAGE_DIR

try:
    import torch
    from diffusers import AutoPipelineForText2Image
    DIFFUSERS_AVAILABLE = True
except Exception:
    torch = None
    AutoPipelineForText2Image = None
    DIFFUSERS_AVAILABLE = False


def detect_media_type(prompt: str) -> str:
    p = prompt.lower()

    if any(word in p for word in [
        "video", "animation", "movie", "clip", "reel", "motion", "cinematic", "demo", "trailer"
    ]):
        return "video"

    if any(word in p for word in [
        "pdf", "report", "document", "resume", "brochure", "ebook", "article", "whitepaper", "newsletter"
    ]):
        return "pdf"

    return "image"


def _safe_filename(prefix: str) -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    return f"{prefix}_{timestamp}"


def _render_placeholder_image(prompt: str, output_path: str):
    width, height = 1024, 1024
    image = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        for x in range(width):
            r = int(30 + (x / width) * 80)
            g = int(40 + (y / height) * 120)
            b = int(120 + (x / width) * 90)
            image[y, x] = [b, g, r]

    pil_image = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_image)

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 70))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rounded_rectangle((80, 80, width - 80, height - 80), radius=40, fill=(0, 0, 0, 80))
    pil_image = Image.alpha_composite(pil_image.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(pil_image)

    title = "AI Generated Image"
    try:
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
    except Exception:
        title_font = ImageFont.load_default()

    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_w) / 2, 140), title, fill=(255, 255, 255), font=title_font)

    try:
        body_font = ImageFont.truetype("DejaVuSans.ttf", 28)
    except Exception:
        body_font = ImageFont.load_default()

    wrapped = textwrap.wrap(prompt, width=28)
    y_pos = 260
    for line in wrapped[:6]:
        line_bbox = draw.textbbox((0, 0), line, font=body_font)
        line_w = line_bbox[2] - line_bbox[0]
        draw.text(((width - line_w) / 2, y_pos), line, fill=(255, 255, 255), font=body_font)
        y_pos += 42

    pil_image.save(output_path, format="PNG")


def _generate_image_with_diffusers(prompt: str, output_path: str):
    if not DIFFUSERS_AVAILABLE or torch is None or AutoPipelineForText2Image is None:
        return False

    try:
        pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo",
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        pipe = pipe.to("cuda" if torch.cuda.is_available() else "cpu")

        image = pipe(
            prompt=prompt,
            num_inference_steps=4,
            guidance_scale=0.0,
            width=1024,
            height=1024,
        ).images[0]

        image.save(output_path)
        return True
    except Exception:
        return False


def generate_image(prompt: str) -> str:
    filename = _safe_filename("image")
    output_path = APP_STORAGE_DIR / f"{filename}.png"

    if _generate_image_with_diffusers(prompt, str(output_path)):
        return str(output_path)

    _render_placeholder_image(prompt, str(output_path))
    return str(output_path)


def generate_pdf(prompt: str) -> str:
    filename = _safe_filename("document")
    output_path = APP_STORAGE_DIR / f"{filename}.pdf"

    canvas_pdf = canvas.Canvas(str(output_path), pagesize=letter)
    canvas_pdf.setTitle("AI Generated PDF")
    canvas_pdf.setFont("Helvetica-Bold", 22)
    canvas_pdf.drawString(72, 760, "AI Generated PDF")

    canvas_pdf.setFont("Helvetica", 14)
    canvas_pdf.drawString(72, 720, "Prompt:")

    wrapped = textwrap.wrap(prompt, width=80)
    y = 690
    for line in wrapped:
        canvas_pdf.drawString(72, y, line[:90])
        y -= 18
        if y < 60:
            canvas_pdf.showPage()
            y = 760
            canvas_pdf.setFont("Helvetica", 12)

    canvas_pdf.save()
    return str(output_path)


def generate_video(prompt: str) -> str:
    filename = _safe_filename("video")
    output_path = APP_STORAGE_DIR / f"{filename}.mp4"

    width, height = 1280, 720
    fps = 24
    duration_seconds = 5
    total_frames = fps * duration_seconds

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

    if not writer.isOpened():
        raise RuntimeError("OpenCV could not create video output. Please verify ffmpeg support.")

    prompt_lines = textwrap.wrap(prompt, width=28)

    for frame_index in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        t = frame_index / total_frames

        for x in range(width):
            for y in range(height):
                b = int(20 + (x / width) * 90 + 30 * t)
                g = int(25 + (y / height) * 90 + 40 * t)
                r = int(50 + (x / width) * 110)
                frame[y, x] = (b, g, r)

        overlay = np.zeros((height, width, 3), dtype=np.uint8)
        cv2.rectangle(overlay, (100, 100), (width - 100, height - 100), (30, 20, 15), -1)
        frame = cv2.addWeighted(frame, 1.0, overlay, 0.35, 0)

        cv2.putText(frame, "AI Generated Video", (120, 150), cv2.FONT_HERSHEY_COMPLEX, 2.0, (255, 255, 255), 3, cv2.LINE_AA)

        y_coord = 280
        for line in prompt_lines[:6]:
            cv2.putText(frame, line, (120, y_coord), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 2, cv2.LINE_AA)
            y_coord += 60

        x_center = int((width / 2) + (width * 0.2) * np.sin(2 * np.pi * t))
        y_center = int(height / 2)
        cv2.circle(frame, (x_center, y_center), 80, (255, 255, 255), 4)

        writer.write(frame)

    writer.release()
    return str(output_path)


def generate_media(prompt: str, media_type: str | None = None) -> dict:
    resolved_type = (media_type or detect_media_type(prompt)).lower()

    if resolved_type == "image":
        file_path = generate_image(prompt)
    elif resolved_type == "pdf":
        file_path = generate_pdf(prompt)
    elif resolved_type == "video":
        file_path = generate_video(prompt)
    else:
        raise ValueError(f"Unsupported media type: {resolved_type}")

    return {
        "media_type": resolved_type,
        "prompt": prompt,
        "file_path": file_path,
        "message": f"{resolved_type.upper()} generated successfully."
    }

import pdfplumber
import os
import traceback
import io
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def extract_text(file):
    """
    Main entry point for extracting text from a resume file (PDF or Image).
    Now returns structured JSON instead of raw text.
    """
    if file.filename.lower().endswith('.pdf'):
        return _extract_text_from_pdf(file)
    elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return _extract_text_from_image(file)
    return {"pages": []}


# ===============================
# PDF HANDLING
# ===============================
def _extract_text_from_pdf(pdf_file):
    try:
        pages_data = []

        with pdfplumber.open(pdf_file) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    pages_data.append({
                        "page_no": i + 1,
                        "text": page_text.strip()
                    })

        return {"pages": pages_data}

    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return {"pages": []}


# ===============================
# IMAGE OCR (Gemini)
# ===============================
def _extract_text_from_image(image_file):
    try:
        from services.ai_engine import AIEngine
        ai = AIEngine()

        if not ai.gemini_client:
            print("Gemini client not initialized. Check GEMINI_API_KEY.")
            return {"pages": []}

        image_file.seek(0)
        image_bytes = image_file.read()

        if not image_bytes:
            return {"pages": []}

        # Validate image
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
        except Exception as img_err:
            print(f"Invalid image file: {img_err}")
            return {"pages": []}

        print(f"DEBUG: Sending image OCR request to Gemini (flash-latest)")

        response = ai.gemini_client.models.generate_content(
            model='gemini-flash-latest',
            contents=[
                "Extract all text from this resume image accurately. Maintain the structure as much as possible.",
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg" if image_file.filename.lower().endswith(('.jpg', '.jpeg')) else "image/png"
                )
            ]
        )

        if response and response.text:
            return {
                "pages": [
                    {
                        "page_no": 1,
                        "text": response.text.strip()
                    }
                ]
            }

        return {"pages": []}

    except Exception as e:
        err_msg = str(e)
        print(f"Error parsing Image with Gemini: {err_msg}")
        traceback.print_exc()
        return {"pages": []}


# For backward compatibility
def extract_text_from_pdf(pdf_file):
    return extract_text(pdf_file)

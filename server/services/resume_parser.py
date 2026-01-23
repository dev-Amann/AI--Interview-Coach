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
    """
    if file.filename.lower().endswith('.pdf'):
        return _extract_text_from_pdf(file)
    elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        return _extract_text_from_image(file)
    return ""

def _extract_text_from_pdf(pdf_file):
    try:
        text = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""

def _extract_text_from_image(image_file):
    try:
        from services.ai_engine import AIEngine
        ai = AIEngine()
        
        if not ai.gemini_client:
            print("Gemini client not initialized. Check GEMINI_API_KEY.")
            return "Error: Gemini AI service not available."

        # Reset file pointer and read bytes
        image_file.seek(0)
        image_bytes = image_file.read()
        
        # Check if bytes were actually read
        if not image_bytes:
            return "Error: Could not read image file content."

        # Use the PIL Image to verify it's a valid image
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify() # Basic verification
            # After verify, we need to reopen or seek if we wanted to use img, 
            # but we use bytes for Gemini.
        except Exception as img_err:
            print(f"Invalid image file: {img_err}")
            return "Error: The uploaded file is not a valid image."

        if not image_bytes:
            print("ERROR: Empty image bytes")
            return "Error: Could not read image file content."

        print(f"DEBUG: Sending image OCR request to Gemini (flash-latest) for {image_file.filename}")
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
            return response.text.strip()
        return "Error: Gemini returned empty response."
        
    except Exception as e:
        err_msg = str(e)
        print(f"Error parsing Image with Gemini: {err_msg}")
        traceback.print_exc()
        if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
            return "Error: Gemini API Quota exceeded. Please wait a minute and try again."
        return f"Error during OCR: {err_msg}"

# For backward compatibility
def extract_text_from_pdf(pdf_file):
    return extract_text(pdf_file)

def extract_text_from_json(ocr_json):
    return " ".join(page["text"] for page in ocr_json["pages"])

def chunk_text(text, chunk_size=400):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks

# Temporary in-memory store
temp_store = {}

def save_ocr(session_id, ocr_json):
    temp_store[session_id] = ocr_json

def get_ocr(session_id):
    return temp_store.get(session_id)

import pdfplumber
import os

def extract_text_from_pdf_raw(pdf_path: str) -> str | None:
    if not os.path.exists(pdf_path):
        return None
    
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        # print(f"Error extracting raw text from PDF '{pdf_path}': {e}")
        return None

def combine_and_normalize_text(raw_extract_text: str) -> str:
    if not raw_extract_text:
        return ""
        
    lines = raw_extract_text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip() != '']
    combined_text = ' '.join(cleaned_lines).lower()
    return combined_text

def parse_pdf_to_text(pdf_path: str) -> str | None:
    raw_text = extract_text_from_pdf_raw(pdf_path)
    if raw_text is None: # File tidak ditemukan atau ada error saat ekstraksi mentah
        return None
        
    processed_text = combine_and_normalize_text(raw_text)
    return processed_text

# TESTING (dicomment)
# if __name__ == "__main__":
#     # Ganti dengan path PDF yang valid untuk testing
#     pdf_path = "cv1.pdf"
#     text = parse_pdf_to_text(pdf_path)
#     if text:
#         print("Extracted and normalized text:")
#         print(text)
#     else:
#         print("Failed to extract text from the PDF.")
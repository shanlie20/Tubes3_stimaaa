import pdfplumber

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def combine_to_string(raw_extract_text):
    lines = raw_extract_text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip() != '']  # hilangkan baris kosong
    combined_text = ' '.join(cleaned_lines).lower()
    return combined_text


# TESTING
# if __name__ == "__main__":
#     pdf_file = "cv1.pdf"  # Ganti dengan path file PDF kamu
#     hasil_teks = extract_text_from_pdf(pdf_file)
#     hasil_string = combine_to_string(hasil_teks)

#     # Simpan hasil ekstraksi ke file teks
#     with open("parser_regex", "w", encoding="utf-8") as f:
#         f.write(hasil_teks)
#     # Simpan hasil gabungan ke file teks
#     with open("parser_string", "w", encoding="utf-8") as f:
#         f.write(hasil_string)
#     # close
    

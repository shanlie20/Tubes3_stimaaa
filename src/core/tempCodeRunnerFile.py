if __name__ == "__main__":
    pdf_path = "cv1.pdf"
    text = parse_pdf_to_text(pdf_path)
    if text:
        print("Extracted and normalized text:")
        print(text)
    else:
        print("Failed to extract text from PDF.")
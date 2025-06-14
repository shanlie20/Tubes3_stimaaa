import pdfplumber
import os
import re # Import the re module for regular expressions

def extract_text_from_pdf_raw(pdf_path: str) -> str | None:
    """
    Extracts raw text content from a PDF file.
    """
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
    """
    Combines lines, removes extra spaces, and converts text to lowercase.
    """
    if not raw_extract_text:
        return ""

    lines = raw_extract_text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip() != '']
    combined_text = ' '.join(cleaned_lines).lower()
    return combined_text

# --- New functions for Regex extraction ---

def _extract_emails(text: str) -> list[str]:
    """Extracts email addresses from text."""
    # Regex for common email formats
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    # Use re.findall to get all matches, then convert to set to get unique emails
    return list(set(re.findall(email_pattern, text, re.IGNORECASE)))

def _extract_phone_numbers(text: str) -> list[str]:
    """Extracts common phone number formats from text."""
    # Regex for various international/local phone number formats
    # Examples: +62 812 3456 7890, (021) 1234567, 0812-3456-7890, 123-456-7890
    phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}(?:[-.\s]?\d{1,4})?\b'
    found_phones = re.findall(phone_pattern, text)
    # Basic filtering for very short numbers that might be false positives
    return list(set([p for p in found_phones if len(re.sub(r'\D', '', p)) >= 8])) # Min 8 digits after removing non-digits


def _extract_urls(text: str) -> list[str]:
    """Extracts URLs (e.g., LinkedIn, GitHub, personal websites) from text."""
    # Regex for common URL formats
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+' # Basic URL pattern
    return list(set(re.findall(url_pattern, text)))

def _extract_dates(text: str) -> list[str]:
    """Extracts common date formats from text (e.g., MM/DD/YYYY, DD-MM-YYYY, Month YYYY)."""
    # Regex for various date formats: MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD, Month YYYY, MM YYYY
    date_pattern = r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{2,4}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}|\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4})\b'
    return list(set(re.findall(date_pattern, text, re.IGNORECASE)))

def _extract_education(text: str) -> list[dict]:
    """
    Extracts potential education entries. This is complex and often needs
    more advanced NLP, but regex can get basic patterns.
    """
    education_patterns = [
        # Degree and institution, optional year range
        r'(?:B\.?S\.?|M\.?S\.?|Ph\.?D\.?|Bachelor|Master|Doctor) in ([A-Za-z\s.,\-&]+?) from ([A-Za-z\s.,\-&]+?)(?:\s+\(?(\d{4}[-–]\d{4}|\d{4})\)?)?',
        # Institution, Degree, optional year
        r'([A-Za-z\s.,\-&]+?),\s*(?:B\.?S\.?|M\.?S\.?|Ph\.?D\.?|Bachelor|Master|Doctor) in ([A-Za-z\s.,\-&]+?)(?:\s+\(?(\d{4}[-–]\d{4}|\d{4})\)?)?',
        # Diploma/Certificate, field, institution, optional year
        r'(?:Diploma|Certificate) in ([A-Za-z\s.,\-&]+?) from ([A-Za-z\s.,\-&]+?)(?:\s+\(?(\d{4}[-–]\d{4}|\d{4})\)?)?'
    ]
    
    extracted_education = []
    for pattern in education_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Depending on pattern, match group order might change.
            # This is a simplified approach, often needs more specific pattern handling
            # or Named Groups in regex.
            if len(match) == 3:
                degree_or_field = match[0].strip()
                institution = match[1].strip()
                year = match[2].strip() if match[2] else None
                extracted_education.append({
                    "degree_or_field": degree_or_field,
                    "institution": institution,
                    "years": year
                })
            elif len(match) == 2: # For patterns without explicit degree/field first
                 extracted_education.append({
                    "degree_or_field": match[0].strip(),
                    "institution": match[1].strip(),
                    "years": None
                })
    return extracted_education


# --- Main Parsing Function with Extraction ---

def parse_pdf_to_text(pdf_path: str) -> str | None:
    """
    Extracts and normalizes text content from a PDF file.
    This is the original function. For structured info, use parse_pdf_to_text_and_extract_info.
    """
    raw_text = extract_text_from_pdf_raw(pdf_path)
    if raw_text is None:
        return None

    processed_text = combine_and_normalize_text(raw_text)
    return processed_text

def parse_pdf_to_text_and_extract_info(pdf_path: str) -> dict:
    """
    Extracts raw text from PDF, normalizes it, and extracts structured information
    using Regular Expressions.

    Returns:
        dict: A dictionary containing:
            'full_text_raw': The raw extracted text.
            'full_text_normalized': The normalized (lowercase, single-space) text.
            'emails': List of extracted email addresses.
            'phone_numbers': List of extracted phone numbers.
            'urls': List of extracted URLs.
            'dates': List of extracted dates.
            'education': List of dictionaries for education entries.
            # Add more fields as you implement more extraction functions
    """
    raw_text = extract_text_from_pdf_raw(pdf_path)
    
    extracted_data = {
        "full_text_raw": raw_text if raw_text else "",
        "full_text_normalized": combine_and_normalize_text(raw_text) if raw_text else "",
        "emails": [],
        "phone_numbers": [],
        "urls": [],
        "dates": [],
        "education": []
        # Initialize other fields you want to extract
    }

    if raw_text:
        # Perform Regex extractions on the raw text
        extracted_data["emails"] = _extract_emails(raw_text)
        extracted_data["phone_numbers"] = _extract_phone_numbers(raw_text)
        extracted_data["urls"] = _extract_urls(raw_text)
        extracted_data["dates"] = _extract_dates(raw_text)
        extracted_data["education"] = _extract_education(raw_text)
        # Call other extraction functions here
    
    return extracted_data

# # TESTING
# if __name__ == "__main__":
#     # Ganti dengan path PDF yang valid untuk testing
#     # Pastikan Anda memiliki contoh CV yang mengandung informasi ini
#     pdf_test_path = "data/contoh_cv_indonesia.pdf" # Sesuaikan path ini

#     # Pastikan file contoh_cv_indonesia.pdf ada di folder data
#     # Contoh isi (simulasi):
#     # Nama: Budi Santoso
#     # Email: budi.santoso@email.com
#     # Telepon: +62 812 3456 7890
#     # LinkedIn: https://linkedin.com/in/budisantoso
#     # Pendidikan:
#     # Sarjana Teknik Informatika dari Institut Teknologi Bandung (2018-2022)
#     # Master of Science, Computer Science, University of California, Berkeley (2023)
#     # Pengalaman:
#     # Software Engineer di PT. Maju Jaya (Jan 2023 - Sekarang)
#     # ...

#     if os.path.exists(pdf_test_path):
#         print(f"Processing: {pdf_test_path}")
#         extracted_info = parse_pdf_to_text_and_extract_info(pdf_test_path)

#         print("\n--- Extracted Information ---")
#         print(f"Full Text (Normalized, first 500 chars): {extracted_info['full_text_normalized'][:500]}...")
#         print(f"Emails: {extracted_info['emails']}")
#         print(f"Phone Numbers: {extracted_info['phone_numbers']}")
#         print(f"URLs: {extracted_info['urls']}")
#         print(f"Dates: {extracted_info['dates']}")
#         print(f"Education: {extracted_info['education']}")
#         # print(f"Skills: {extracted_info['skills']}") # Jika sudah ditambahkan

#         # Contoh pengujian dengan parse_pdf_to_text (fungsi asli)
#         # text_only = parse_pdf_to_text(pdf_test_path)
#         # print("\n--- Original Text-Only Parsing ---")
#         # print(f"Text only (normalized): {text_only[:500]}...")

#     else:
#         print(f"PDF test file not found at: {pdf_test_path}")
#         print("Please create a dummy PDF or adjust the path for testing.")
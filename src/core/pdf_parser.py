import pdfplumber
import os
import re

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
        return None

def combine_and_normalize_text(raw_extract_text: str) -> str:
    if not raw_extract_text:
        return ""
        
    lines = raw_extract_text.splitlines()
    cleaned_lines = [line.strip() for line in lines if line.strip() != '']
    # Jangan lowercase di sini karena Regex Case Insensitive akan digunakan
    # dan kita mungkin perlu case untuk ekstraksi yang akurat atau tampilan
    combined_text = ' '.join(cleaned_lines) # Hapus .lower()
    return combined_text

# --- Fungsi Ekstraksi Regex yang Disesuaikan ---

def _extract_phone_numbers(text: str) -> list[str]:
    phone_pattern = re.compile(
        r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}(?:[-.\s]?\d{1,4})?\b'
    )
    found_phones = phone_pattern.findall(text)
    return list(set([p for p in found_phones if len(re.sub(r'\D', '', p)) >= 8]))

def _extract_skills(text: str) -> list[str]:
    """
    Mengambil daftar keterampilan dari bagian 'Skills:' hingga bagian selanjutnya.
    Pola ini lebih spesifik untuk format CV di mana skills ada di bagian bawah,
    seringkali dipisahkan oleh koma atau dengan satu spasi (jika dari daftar panjang).
    """
    # Mencari bagian "Skills" dan mengambil semua teks sampai akhir dokumen
    # atau sampai section berikutnya (jika ada lagi setelah Skills)
    skills_section_match = re.search(
        r'(?:skills|skill):?\s*(.*?)(?:\n[A-Z][A-Za-z\s]+:|$)', # Cari "Skills:" dan ambil sampai newline + uppercase header atau akhir
        text, re.IGNORECASE | re.DOTALL
    )
    
    if skills_section_match:
        skills_text = skills_section_match.group(1).strip()
        # Hapus karakter backslash jika ada
        skills_text = re.sub(r'\\', '', skills_text)
        
        # Pecah berdasarkan koma, atau dua spasi atau lebih, atau bullet/dash.
        # Kemudian bersihkan entri kosong.
        raw_skills = re.split(r',\s*|,\s*\n|;\s*|\n\s*•\s*|\n\s*-\s*|\s{2,}', skills_text)
        
        cleaned_skills = []
        for skill in raw_skills:
            s = skill.strip()
            # Hapus angka yang berdiri sendiri, misal "8" pada "8 Magna Cum Lade"
            if re.match(r'^\d+$', s):
                continue
            if s and len(s) > 1: # Pastikan bukan string kosong atau terlalu pendek
                cleaned_skills.append(s)
        
        # Filter kata kunci yang terlalu umum atau tidak relevan jika perlu
        # Contoh:
        # common_junk = ["management", "services", "solutions"]
        # cleaned_skills = [s for s in cleaned_skills if s.lower() not in common_junk]

        return list(set(cleaned_skills)) # Hapus duplikat
    return []


def _extract_job_history(text: str) -> list[dict]:
    """
    Ekstraksi job history yang lebih robust berdasarkan format CV yang diberikan.
    """
    job_history_section_match = re.search(
        r'(?:job history|experience):?\s*(.*?)(?:education:|skills:|accomplishments:|summary:|$)',
        text, re.IGNORECASE | re.DOTALL
    )
    
    extracted_jobs = []
    if job_history_section_match:
        job_text = job_history_section_match.group(1).strip()
        
        # Pola untuk setiap entri pekerjaan:
        # Role/Jabatan (misal: "Sous Chef")
        # Periode (misal: "Jul 2010") -- atau rentang
        # CompanyName, City, State
        # Deskripsi (beberapa baris setelahnya)
        
        job_entry_pattern = re.compile(
            r'([A-Za-z\s.,\-&\/\(\)]+\s*(?:II|III|IV)?)\n'  # Group 1: Role (e.g., "Sous Chef", "Front Desk Agent", "Front Desk Manager")
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}(?:\s*to\s*(?:Current|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*\d{4}))?)\n' # Group 2: Period (e.g., "Jul 2010", "Jan 2013 to Jan 2014")
            r'([A-Za-z\s.,\-&\/\(\)]+?)\n' # Group 3: Company Name (e.g., "CompanyName", "Stratford University")
            r'([\s\S]*?)(?=\n(?:[A-Z][a-z\s.,\-&\/\(\)]+\s*\d{4})|' # Description (Group 4) until next job entry pattern (Role Year)
            r'^(?:Education|Skills|Accomplishments|Summary|Certifications):?|$)', # or until new section header or end of string
            re.MULTILINE | re.IGNORECASE
        )
        
        job_entries = job_entry_pattern.finditer(job_text)
        
        for match in job_entries:
            role = match.group(1).strip()
            period = match.group(2).strip()
            company = match.group(3).strip()
            description_raw = match.group(4).strip()
            
            # Bersihkan deskripsi dari dan bullet points/leading spaces
            description_cleaned = re.sub(r'\|\n\s*\*?\s*', ' ', description_raw).strip()
            
            extracted_jobs.append({
                "role": role,
                "period": period,
                "company": company,
                "description": description_cleaned
            })
    return extracted_jobs


def _extract_education(text: str) -> list[dict]:
    """
    Ekstraksi bagian Education.
    Mencari Jurusan Kuliah, Institusi, dan Periode Waktu.
    """
    education_section_match = re.search(
        r'education:?\s*(.*?)(?:skills:|experience:|job history:|accomplishments:|summary:|$)',
        text, re.IGNORECASE | re.DOTALL
    )
    
    extracted_education = []
    if education_section_match:
        edu_text = education_section_match.group(1).strip()
        
        # Pola berdasarkan contoh PDF:
        # Degree/Major, Institution [City, State] GPA: GPA: 3.8 Magna Cum Lade Business AdministrationGPA: 3.8 Magna Cum Lade
        # Bachelors of Arts , Hospitality Management 2013 Stratford University , City , State, USA
        # Associate of Applied Science, Advanced Culinary Arts 2010 Stratford , City , State, USA
        
        edu_entry_pattern = re.compile(
            r'([A-Za-z\s.,\-&:]+?)\s*(?:\d{4})?\s*' # Group 1: Degree/Major (e.g., Master's , Business Administration)
            r'([A-Za-z\s.,\-&]+?)\s+' # Group 2: Institution (e.g., Stratford University)
            r'(?:[A-Za-z\s,]+(?:GPA:.*?)?)?' # Optional City, State, GPA, other junk
            r'(\d{4}(?:[-–]\d{4})?)?', # Group 3: Optional Year or Year Range (e.g., 2015, 2010-2014)
            re.IGNORECASE | re.MULTILINE
        )
        
        edu_entries = edu_entry_pattern.finditer(edu_text)
        
        for match in edu_entries:
            major_field = match.group(1).strip()
            institution = match.group(2).strip()
            period = match.group(3).strip() if match.group(3) else "" # Period could be empty

            extracted_education.append({
                "major_field": major_field,
                "institution": institution,
                "period": period
            })
    return extracted_education


# --- Main Parsing Function with Extraction ---

def parse_pdf_to_text(pdf_path: str = None, text_content: str = None) -> str | None: # Tambahkan default None
    """
    Extracts and normalizes text content from a PDF file.
    This is the original function. For structured info, use parse_pdf_to_text_and_extract_info.
    """
    raw_text = None
    if pdf_path:
        raw_text = extract_text_from_pdf_raw(pdf_path)
    elif text_content: # Gunakan text_content jika disediakan
        raw_text = text_content
    
    if raw_text is None:
        return None
    processed_text = combine_and_normalize_text(raw_text)
    return processed_text

def parse_pdf_to_text_and_extract_info(pdf_path: str = None, text_content: str = None) -> dict: # Tambahkan default None
    """
    Extracts raw text from PDF (or uses provided text_content), normalizes it,
    and extracts structured information using Regular Expressions.

    Args:
        pdf_path (str, optional): Path to the PDF file.
        text_content (str, optional): Raw text content directly provided.
                                      If pdf_path is None, this will be used.

    Returns:
        dict: A dictionary containing:
            'full_text_raw': The raw extracted text.
            'full_text_normalized': The normalized (lowercase, single-space) text.
            'phone_numbers': List of extracted phone numbers.
            'skills': List of extracted skills (strings).
            'job_history': List of dictionaries for job history entries.
            'education': List of dictionaries for education entries.
    """
    raw_text = None
    if pdf_path:
        raw_text = extract_text_from_pdf_raw(pdf_path)
    elif text_content:
        raw_text = text_content
    
    extracted_data = {
        "full_text_raw": raw_text if raw_text else "",
        "full_text_normalized": combine_and_normalize_text(raw_text) if raw_text else "",
        "phone_numbers": [],
        "skills": [],
        "job_history": [],
        "education": []
    }

    if raw_text:
        extracted_data["phone_numbers"] = _extract_phone_numbers(raw_text)
        extracted_data["skills"] = _extract_skills(raw_text)
        extracted_data["job_history"] = _extract_job_history(raw_text)
        extracted_data["education"] = _extract_education(raw_text)
    
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
import re

def extract_email(text: str) -> str | None:
    match = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b', text)
    return match.group(0) if match else None

def extract_phone(text: str) -> str | None:
    match = re.search(r'\b\d{10,13}\b', text)
    return match.group(0) if match else None

def extract_years(text: str) -> List[str]:
    return re.findall(r'\b(19|20)\d{2}\b', text)
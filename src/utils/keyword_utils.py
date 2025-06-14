import re
import string

def normalize_text(text: str) -> str:
    """
    Menormalisasi teks dengan mengkonversi ke huruf kecil dan menghapus tanda baca.

    Args:
        text (str): Teks input.

    Returns:
        str: Teks yang sudah dinormalisasi.
    """
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text.strip()

def tokenize_text(text: str) -> list[str]:
    """
    Melakukan tokenisasi teks menjadi daftar kata.

    Args:
        text (str): Teks input.

    Returns:
        list[str]: Daftar kata (token).
    """
    return re.findall(r'\b\w+\b', text.lower()) # Menemukan semua kata alpha-numeric

def remove_stopwords(tokens: list[str], stopwords: set[str] = None) -> list[str]:
    """
    Menghapus stop words dari daftar token.

    Args:
        tokens (list[str]): Daftar token.
        stopwords (set[str]): Set berisi stop words yang akan dihapus.
                               Jika None, akan menggunakan stop words default Bahasa Inggris sederhana.

    Returns:
        list[str]: Daftar token tanpa stop words.
    """
    if stopwords is None:
        # Contoh stop words sederhana. Dalam aplikasi nyata, disarankan menggunakan
        # library NLP seperti NLTK atau SpaCy untuk daftar stop words yang lebih komprehensif
        # dan mendukung berbagai bahasa.
        stopwords = {
            "a", "an", "the", "and", "or", "but", "is", "are", "was", "were", "be",
            "has", "have", "had", "do", "does", "did", "not", "no", "yes", "for",
            "with", "on", "at", "by", "to", "from", "in", "out", "of", "and", "or",
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you",
            "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself",
            "she", "her", "hers", "herself", "it", "its", "itself", "they", "them",
            "their", "theirs", "themselves", "what", "which", "who", "whom", "this",
            "that", "these", "those", "am", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "having", "do", "does", "did", "doing",
            "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
            "while", "of", "at", "by", "for", "with", "about", "against", "between",
            "into", "through", "during", "before", "after", "above", "below", "to",
            "from", "up", "down", "in", "out", "on", "off", "over", "under", "again",
            "further", "then", "once", "here", "there", "when", "where", "why", "how",
            "all", "any", "both", "each", "few", "more", "most", "other", "some",
            "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "s", "t", "can", "will", "just", "don", "should", "now"
        }
    return [word for word in tokens if word not in stopwords]

def extract_unique_keywords(text: str, normalize: bool = True, remove_sw: bool = True) -> list[str]:
    """
    Mengekstrak daftar kata kunci unik dari teks, dengan opsi normalisasi dan penghapusan stop words.

    Args:
        text (str): Teks input.
        normalize (bool): Jika True, normalisasi teks dilakukan.
        remove_sw (bool): Jika True, stop words akan dihapus.

    Returns:
        list[str]: Daftar kata kunci unik yang sudah diproses.
    """
    processed_text = text
    if normalize:
        processed_text = normalize_text(text)

    tokens = tokenize_text(processed_text)

    if remove_sw:
        tokens = remove_stopwords(tokens)

    return sorted(list(set(tokens))) # Mengembalikan yang unik dan terurut

# Contoh penggunaan:
# from src.utils.keyword_utils import normalize_text, tokenize_text, remove_stopwords, extract_unique_keywords
#
# # text = "Programmer Python, S.Kom., pengalaman 5 tahun."
# # normalized_text = normalize_text(text)
# # print(f"Normalized: {normalized_text}")
#
# # tokens = tokenize_text(normalized_text)
# # print(f"Tokens: {tokens}")
#
# # filtered_tokens = remove_stopwords(tokens)
# # print(f"Filtered: {filtered_tokens}")
#
# # keywords = extract_unique_keywords(text, normalize=True, remove_sw=True)
# # print(f"Keywords: {keywords}")
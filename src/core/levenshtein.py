def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Menghitung jarak Levenshtein antara dua string s1 dan s2.
    Jarak maksudnya adalah jumlah operasi edit minimum
    (insert, delete, replace) untuk mengubah s1 menjadi s2.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # s1 lebih panjang atau sama panjang dengan s2
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1, start=1):
        current_row = [i]
        for j, c2 in enumerate(s2, start=1):
            insertions = previous_row[j] + 1
            deletions = current_row[j-1] + 1
            substitutions = previous_row[j-1] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def levenshtein_ratio(s1: str, s2: str) -> float:
    """
    Menghitung rasio kemiripan dua string berdasarkan jarak Levenshtein,
    dengan nilai 1.0 berarti identik, dan 0 berarti sangat berbeda.
    """
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0  # kedua string kosong
    return 1.0 - (distance / max_len)

def fuzzy_search(text: str, keyword: str, threshold: float = 0.8) -> bool:
    """
    Mencari apakah terdapat kata dalam 'text' yang mirip dengan 'keyword' 
    berdasarkan threshold kemiripan Levenshtein Ratio.
    Return True jika ada kata mirip, False jika tidak.

    Args:
        text (str): Teks untuk dicari
        keyword (str): Kata kunci yang akan dicari kemiripannya
        threshold (float): nilai ambang batas rasio kemiripan (0.0-1.0)

    Returns:
        bool: True jika ditemukan kemiripan di atas threshold, False jika tidak
    """
    words = text.split()
    for word in words:
        ratio = levenshtein_ratio(word, keyword)
        if ratio >= threshold:
            return True
    return False

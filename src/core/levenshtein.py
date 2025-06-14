from typing import List

def levenshtein_distance(s1: str, s2: str) -> int:
    """Menghitung jarak Levenshtein antara dua string s1 dan s2."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

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
    """Menghitung rasio kemiripan dua string berdasarkan jarak Levenshtein."""
    distance = levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 1.0  # kedua string kosong
    return 1.0 - (distance / max_len)

def fuzzy_search(text: str, keyword: str, threshold: float) -> int:
    """Mencari dan menghitung jumlah kemunculan kata dalam text yang mirip dengan keyword berdasarkan Levenshtein Distance."""
    words = text.split()
    count = 0
    for word in words:
        ratio = levenshtein_ratio(word, keyword)
        if ratio >= threshold:
            count += 1
    return count


# Contoh penggunaan:
if __name__ == "__main__":
    text_example = "hello world, this is a test of the fuzzy matching algorithm"
    keyword_example = "helo"  # Kata yang salah ketik
    threshold = 0.8  # Ambang batas kemiripan
    
    results = fuzzy_search(text_example, keyword_example, threshold)
    
    # Menampilkan hasil pencarian
    print(f"Keyword: {keyword_example}")
    print(f"Fuzzy Matches Count: {results}")

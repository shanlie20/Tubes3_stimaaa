from typing import List

def boyer_moore_search(text: str, pattern: str) -> int:
    """
    Mencari semua kemunculan 'pattern' dalam 'text' menggunakan algoritma Boyer-Moore
    (dengan Bad Character Rule sederhana), dan mengembalikan jumlah total kemunculannya.

    Args:
        text (str): Teks tempat pencarian dilakukan.
        pattern (str): Pola yang dicari.

    Returns:
        int: Jumlah kemunculan pattern dalam text.
    """
    n = len(text)
    m = len(pattern)

    if m == 0:
        return 1 if n >= 0 else 0
    if n == 0 or m > n:
        return 0

    # Buat tabel last occurrence dari tiap karakter
    bad_char = {c: i for i, c in enumerate(pattern)}

    occurrences = []
    s = 0

    while s <= n - m:
        j = m - 1

        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1

        if j < 0:
            occurrences.append(s)
            s += m  # geser penuh untuk skip overlap
        else:
            last = bad_char.get(text[s + j], -1)
            shift = max(1, j - last)
            s += shift

    return len(occurrences)

# Contoh penggunaan:
# if __name__ == "__main__":
#     text_example = "BABABBABBBABABBABBBB"
#     pattern_example = "BABB"
#     count_occurences, is_found = boyer_moore_search(text_example, pattern_example)
#     print(f"Occurences: {count_occurences}")
#     print(f"Found? {is_found}")
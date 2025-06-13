from typing import List

def compute_lps_array(pattern: str) -> int:
    """
    Menghitung Longest Proper Prefix which is also Suffix (LPS) array
    untuk algoritma KMP.

    LPS array menyimpan panjang awalan terpanjang dari pola yang
    juga merupakan akhiran dari pola tersebut hingga indeks tertentu.

    Args:
        pattern (str): Pola yang akan dicari.

    Returns:
        List[int]: Array LPS.
    """
    m = len(pattern)
    lps = [0] * m
    length = 0  # Panjang awalan terpanjang yang juga merupakan akhiran

    i = 1
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

def kmp_search(text: str, pattern: str) -> List[int]:
    """
    Mencari semua kemunculan 'pattern' dalam 'text' menggunakan algoritma KMP.
    Sensitif terhadap kapitalisasi.

    Args:
        text (str): Teks tempat pencarian akan dilakukan.
        pattern (str): Pola yang akan dicari.

    Returns:
        List[int]: Daftar indeks awal dari semua kemunculan pola yang ditemukan.
                   Mengembalikan list kosong jika pola tidak ditemukan atau input tidak valid.
    """
    n = len(text)
    m = len(pattern)

    if m == 0:
        return [0] if n >= 0 else [] # Pola kosong ditemukan di indeks 0 jika teks ada
    if n == 0 or m > n:
        return [] # Teks kosong atau pola lebih panjang dari teks

    lps = compute_lps_array(pattern)
    occurrences = []

    i = 0  # Indeks untuk teks
    j = 0  # Indeks untuk pola

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            occurrences.append(i - j)
            j = lps[j - 1] # Geser pola menggunakan nilai LPS untuk mencari kemunculan berikutnya
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1] # Jangan cocokkan j karakter, cocokkan lps[j-1] karakter
            else:
                i += 1

    occurrences
    count_occurrences = len(occurrences)
    return count_occurrences

# Contoh penggunaan:
# from src.core.kmp import kmp_search
#
# # text_example = "ABABDABACDABABCABAB"
# # pattern_example = "ABABCABAB"
# # results = kmp_search(text_example, pattern_example)
# # print(f"Occurrences at: {results}")
#
# # text_long = "ABCABCABCABCABCABC" * 1000
# # pattern_long = "ABCABC"
# # # start_time = time.perf_counter() # Bisa menggunakan timer.py di sini
# # results_long = kmp_search(text_long, pattern_long)
# # # end_time = time.perf_counter()
# # # print(f"Long search took {(end_time - start_time) * 1000:.4f} ms")
# # # print(f"Found {len(results_long)} times.")
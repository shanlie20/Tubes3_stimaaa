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
    length = 0

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
        return [0] if n >= 0 else []
    if n == 0 or m > n:
        return []

    lps = compute_lps_array(pattern)
    occurrences = []

    i = 0
    j = 0

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            occurrences.append(i - j)
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    occurrences
    count_occurrences = len(occurrences)
    return count_occurrences
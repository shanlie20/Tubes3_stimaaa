from typing import List

def compute_lps_array(pattern: str) -> List[int]:
    """
    Menghitung Longest Proper Prefix yang juga Suffix (LPS) array untuk KMP.
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

def kmp_search(text: str, pattern: str) -> int:
    """
    KMP Search yang mengembalikan jumlah total kemunculan pattern dalam text.

    Args:
        text (str): Teks tempat pencarian.
        pattern (str): Pola yang dicari.

    Returns:
        int: Jumlah kemunculan pola dalam teks.
    """
    n = len(text)
    m = len(pattern)

    if m == 0:
        return 1 if n >= 0 else 0
    if n == 0 or m > n:
        return 0

    lps = compute_lps_array(pattern)
    count = 0
    i = 0
    j = 0

    while i < n:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == m:
            count += 1
            j = lps[j - 1]
        elif i < n and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1

    return count
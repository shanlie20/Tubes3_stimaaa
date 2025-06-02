from typing import List, Tuple

def boyer_moore_search(text: str, pattern: str) -> Tuple[List[int], bool]:
    """
    Mencari semua kemunculan 'pattern' dalam 'text' menggunakan algoritma Boyer-Moore sederhana
    dengan fokus pada Bad Character Rule dan 3 case utama.
    
    Mengembalikan tuple (list_posisi_kemunculan, ditemukan_atau_tidak).

    Args:
        text (str): Teks tempat pencarian akan dilakukan.
        pattern (str): Pola yang akan dicari.

    Returns:
        Tuple[List[int], bool]: (Daftar indeks kemunculan, True jika ditemukan, False jika tidak)
    """
    n = len(text)
    m = len(pattern)

    if m == 0:
        return ([0] if n >= 0 else [], True if n >= 0 else False)
    if n == 0 or m > n:
        return ([], False)

    # Membuat tabel bad character: char -> posisi terakhir kemunculan di pola
    bad_char = {}
    for i, c in enumerate(pattern):
        bad_char[c] = i

    occurrences = []
    s = 0  # posisi pergeseran pola terhadap teks

    while s <= n - m:
        j = m - 1

        # Cocokkan pola dengan teks dari belakang ke depan
        while j >= 0 and pattern[j] == text[s + j]:
            j -= 1

        if j < 0:
            # Pola ditemukan di posisi s
            occurrences.append(s)
            # Geser pola sebanyak panjang pola agar tidak menghitung kemunculan yang overlap
            s += m
        else:
            x = text[s + j]
            last_occurrence = bad_char.get(x, -1)

            if last_occurrence != -1:
                # Case 1 dan Case 2
                shift = j - last_occurrence
                if shift > 0:
                    # Case 1: geser pola agar karakter terakhir x di pola sejajar dengan teks
                    s += shift
                else:
                    # Case 2: geser pola 1 langkah jika shift <= 0
                    s += 1
            else:
                # Case 3: karakter x tidak ada di pola
                s += j + 1  # geser pola melewati karakter mismatch

    count_occurences = len(occurrences)
    found = count_occurences > 0
    return count_occurences, found


# Contoh penggunaan:
if __name__ == "__main__":
    text_example = "BABABBABBBABABBABBBB"
    pattern_example = "BABB"
    count_occurences, is_found = boyer_moore_search(text_example, pattern_example)
    print(f"Occurences: {count_occurences}")
    print(f"Found? {is_found}")

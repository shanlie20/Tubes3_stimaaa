# src/core/aho_corasick.py

import collections

def aho_corasick_search(text: str, keywords: list[str]) -> dict[str, int]:
    """
    Mencari semua kemunculan dari sekumpulan kata kunci dalam sebuah teks
    menggunakan algoritma Aho-Corasick dalam satu fungsi mandiri.

    Args:
        text (str): Teks masukan untuk dicari.
        keywords (list[str]): Daftar pola/kata kunci yang akan dicari.

    Returns:
        dict[str, int]: Dictionary yang memetakan kata kunci yang ditemukan
                        dengan jumlah kemunculannya.
    """
    if not keywords:
        return {}

    # --- Definisi Node Lokal ---
    # Kelas _Node sekarang hanya ada di dalam scope fungsi ini.
    class _Node:
        def __init__(self):
            self.children = collections.defaultdict(_Node)
            self.output = []
            self.failure_link = None
    
    # ===================================================================
    # --- FASE 1: PRA-PEMROSESAN (Membangun Automata) ---
    # ===================================================================
    
    root = _Node()

    # --- Bagian 1A: Membangun Trie (logika dari _build_trie) ---
    for keyword in keywords:
        node = root
        for char in keyword:
            node = node.children[char]
        node.output.append(keyword)

    # --- Bagian 1B: Membangun Failure Links (logika dari _build_failure_links) ---
    queue = collections.deque()
    root.failure_link = root

    for char, child_node in root.children.items():
        child_node.failure_link = root
        queue.append(child_node)

    while queue:
        current_node = queue.popleft()
        for char, next_node in current_node.children.items():
            failure_node = current_node.failure_link
            
            while char not in failure_node.children and failure_node is not root:
                failure_node = failure_node.failure_link
            
            if char in failure_node.children:
                next_node.failure_link = failure_node.children[char]
            else:
                next_node.failure_link = root

            next_node.output.extend(next_node.failure_link.output)
            queue.append(next_node)

    # ===================================================================
    # --- FASE 2: PENCARIAN ---
    # ===================================================================
    results = collections.defaultdict(int)
    current_node = root

    for char in text:
        while char not in current_node.children and current_node is not root:
            current_node = current_node.failure_link
        
        if char in current_node.children:
            current_node = current_node.children[char]

        if current_node.output:
            for keyword in current_node.output:
                results[keyword] += 1
    
    return dict(results)

# ==============================================================================
# CONTOH PENGGUNAAN (tidak berubah dan tetap berfungsi)
# ==============================================================================
if __name__ == "__main__":
    keywords = ["he", "she", "his", "hers"]
    text = "ushers he she his"

    # Panggil fungsi pencarian utama secara langsung
    found = aho_corasick_search(text, keywords)

    print(f"Text: '{text}'")
    print(f"Keywords to find: {keywords}")
    print("-" * 30)
    if found:
        print("Found keywords and their counts:")
        for keyword, count in found.items():
            print(f"- '{keyword}': {count} time(s)")
    else:
        print("No keywords found.")
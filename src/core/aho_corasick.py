from collections import deque

# Fungsi untuk menambahkan pola ke dalam trie
# Mengembalikan jumlah node yang baru
def add_pattern(pattern, trie, fail, output):
    node = 0
    # Menggunakan len(trie) sebagai num_nodes saat ini
    for char in pattern:
        if char not in trie[node]:
            trie[node][char] = len(trie) # Node baru akan menjadi indeks berikutnya di trie
            trie.append({})
            fail.append(-1)
            output.append(set())
        node = trie[node][char]
    output[node].add(pattern)  # Menyimpan pola yang ditemukan pada node terakhir
    # Tidak perlu mengembalikan num_nodes, karena len(trie) yang sudah update bisa digunakan
    # dalam fungsi lain untuk mengetahui total node.

# Fungsi untuk membangun fail function
def build_failure_function(trie, fail, output):
    queue = deque()

    # Inisialisasi: Semua anak langsung dari root (node 0) memiliki fail link ke root (0)
    for char_code in range(256): # Asumsi karakter ASCII
        char = chr(char_code)
        if char in trie[0]:
            next_node = trie[0][char]
            fail[next_node] = 0 # Fail link anak-anak root selalu ke root
            queue.append(next_node)
        # Penting: Jangan modifikasi trie[0][char] = 0 di sini.
        # Transisi default dari root ditangani di get_next_state saat search.

    # Proses BFS untuk node lainnya
    while queue:
        state = queue.popleft() # Ambil node saat ini (u)
        
        for char, next_state in trie[state].items(): # Iterasi melalui anak-anak node u (v)
            # Dapatkan fail link dari parent state (u)
            fail_state = fail[state]
            
            # Ikuti fail link sampai menemukan transisi untuk karakter 'char'
            # atau sampai kembali ke root.
            while fail_state != 0 and char not in trie[fail_state]:
                fail_state = fail[fail_state]
            
            # Jika karakter ditemukan di fail_state, atau fail_state adalah root
            # dan karakter ada di root, maka fail link adalah node tersebut.
            if char in trie[fail_state]:
                fail[next_state] = trie[fail_state][char]
            else:
                fail[next_state] = 0 # Jika tidak ditemukan bahkan di root, fail ke root

            # Gabungkan output dari fail link
            # Output dari next_state harus mencakup output dari fail[next_state]
            output[next_state].update(output[fail[next_state]])
            
            queue.append(next_state)

# Fungsi pembantu untuk mendapatkan state berikutnya
# Ini menggabungkan trie traversal dengan fail function
def get_next_state(current_state, char, trie, fail):
    # Ikuti fail link sampai menemukan transisi untuk 'char' atau kembali ke root
    while current_state != 0 and char not in trie[current_state]:
        current_state = fail[current_state]
    
    # Jika karakter ada di trie[current_state], ikuti transisi.
    # Jika tidak, dan kita di root, tetap di root (current_state = 0)
    if char in trie[current_state]:
        return trie[current_state][char]
    else:
        return 0 # Kembali ke root jika transisi tidak ditemukan

# Fungsi untuk mencari pola dalam teks
def search(text, trie, fail, output):
    node = 0
    result = {}  # Menggunakan dict biasa untuk menyimpan hasil pencocokan
    for char in text:
        node = get_next_state(node, char, trie, fail)
        
        # Jika ada pola yang cocok di node saat ini (termasuk dari fail link)
        if output[node]:
            for pattern in output[node]:
                result[pattern] = result.get(pattern, 0) + 1  # Menambahkan jumlah kemunculan pola
    return result

# Fungsi utama untuk mencocokkan keywords dengan teks
def aho_corasick_search(keywords, normalized_cv_content) -> dict:
    # Inisialisasi struktur data
    trie = [{}]  # Trie untuk menyimpan pola. Node 0 adalah root.
    fail = [0]   # Fungsi fail. fail[0] selalu 0.
    output = [set()] # Fungsi output untuk menyimpan pola yang cocok

    # Menambahkan pola-pola dari keywords ke dalam trie
    for pattern in keywords:
        add_pattern(pattern, trie, fail, output)

    # Membangun fungsi kegagalan
    build_failure_function(trie, fail, output)

    # Mencari pola dalam teks yang sudah dinormalisasi
    result = search(normalized_cv_content, trie, fail, output)
    
    # Mengembalikan hasil pencocokan dalam bentuk dictionary
    return result

# Fungsi untuk menormalisasi teks (menghapus non-alfanumerik dan mengubah menjadi huruf kecil)
def normalize_text(text: str) -> str:
    """Normalizes text by converting to lowercase and replacing non-alphanumeric characters with spaces."""
    # Menghilangkan karakter non-alfanumerik dan spasi berlebih
    normalized = ''.join([char.lower() if char.isalnum() else ' ' for char in text])
    # Mengganti spasi berlebih dengan satu spasi
    return ' '.join(normalized.split())

# # Contoh penggunaan
# if __name__ == "__main__":
#     keywords = ["python", "react", "sql", "developer", "data", "web developer", "java"]
#     cv_content = "I am a Python developer with experience in React and SQL databases. I also work as a web developer using Java."

#     print(f"Original CV Content: {cv_content}")
#     print(f"Keywords: {keywords}")

#     # Menormalisasi teks dan keywords
#     normalized_keywords = [normalize_text(keyword) for keyword in keywords]
#     normalized_cv_content = normalize_text(cv_content)

#     print(f"\nNormalized CV Content: {normalized_cv_content}")
#     print(f"Normalized Keywords: {normalized_keywords}")

#     # Pencocokan pola menggunakan Aho-Corasick
#     result = aho_corasick_search(normalized_keywords, normalized_cv_content)

#     # Menampilkan hasil pencocokan
#     print("\nMatches found:")
#     print(result)

#     # Contoh lain
#     keywords2 = ["cat", "dog", "fish", "data", "database"]
#     cv_content2 = "My pet is a cat. I love my dog. This is data from a database."
#     normalized_keywords2 = [normalize_text(keyword) for keyword in keywords2]
#     normalized_cv_content2 = normalize_text(cv_content2)
#     print(f"\nOriginal CV Content 2: {cv_content2}")
#     print(f"Keywords 2: {keywords2}")
#     result2 = aho_corasick_search(normalized_keywords2, normalized_cv_content2)
#     print("Matches found (Example 2):")
#     print(result2)

#     # Contoh dengan overlapping patterns
#     keywords3 = ["he", "she", "his", "hers"]
#     cv_content3 = "He is happy. She likes his car. His is new."
#     normalized_keywords3 = [normalize_text(keyword) for keyword in keywords3]
#     normalized_cv_content3 = normalize_text(cv_content3)
#     print(f"\nOriginal CV Content 3: {cv_content3}")
#     print(f"Keywords 3: {keywords3}")
#     result3 = aho_corasick_search(normalized_keywords3, normalized_cv_content3)
#     print("Matches found (Example 3):")
#     print(result3)
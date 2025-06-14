from collections import deque

# Fungsi untuk menambahkan pola ke dalam trie
def add_pattern(pattern, trie, fail, output, num_nodes):
    node = 0
    for char in pattern:
        if char not in trie[node]:
            trie[node][char] = num_nodes
            num_nodes += 1
            trie.append({})
            fail.append(-1)
            output.append(set())
        node = trie[node][char]
    output[node].add(pattern)  # Menyimpan pola yang ditemukan pada node terakhir
    return num_nodes

# Fungsi untuk membangun fail function
def build_failure_function(trie, fail, output):
    queue = deque()
    
    # Setup fungsi fail untuk kedalaman 1
    for char in range(256):  # ASCII range
        char = chr(char)
        if char in trie[0]:
            fail[trie[0][char]] = 0
            queue.append(trie[0][char])
        else:
            trie[0][char] = 0

    # Proses fungsi fail untuk node lainnya
    while queue:
        state = queue.popleft()
        for char in trie[state]:
            # Ikuti link kegagalan jika diperlukan
            fail_state = fail[state]
            while char not in trie[fail_state]:
                fail_state = fail[fail_state]
            fail[trie[state][char]] = trie[fail_state][char]
            # Gabungkan output dari node kegagalan
            output[trie[state][char]].update(output[fail[trie[state][char]]])
            queue.append(trie[state][char])

# Fungsi untuk mencari pola dalam teks menggunakan dict biasa
def search(text, trie, fail, output):
    node = 0
    result = {}  # Menggunakan dict biasa untuk menyimpan hasil pencocokan
    for i in range(len(text)):
        char = text[i]
        # Ikuti link kegagalan jika diperlukan
        while char not in trie[node]:
            node = fail[node]
        node = trie[node][char]
        if output[node]:
            for pattern in output[node]:
                result[pattern] = result.get(pattern, 0) + 1  # Menambahkan jumlah kemunculan pola
    return result

# Fungsi utama untuk mencocokkan keywords dengan teks
def aho_corasick_search(keywords, normalized_cv_content) -> dict:
    # Inisialisasi struktur data
    trie = [{}]  # Trie untuk menyimpan pola
    fail = [-1]  # Fungsi fail
    output = [set()]  # Fungsi output untuk menyimpan pola yang cocok
    num_nodes = 1  # Jumlah node, mulai dari 1
    
    # Menambahkan pola-pola dari keywords ke dalam trie
    for pattern in keywords:
        num_nodes = add_pattern(pattern, trie, fail, output, num_nodes)

    # Debugging: Menampilkan struktur trie setelah penambahan pola
    print("Trie:", trie)
    print("Fail:", fail)
    print("Output:", output)
    
    # Membangun fungsi kegagalan
    build_failure_function(trie, fail, output)

    # Debugging: Menampilkan struktur trie setelah fail function dibangun
    print("Trie After Fail Function:", trie)
    print("Fail After Fail Function:", fail)
    print("Output After Fail Function:", output)
    
    # Mencari pola dalam teks yang sudah dinormalisasi
    result = search(normalized_cv_content, trie, fail, output)
    print("Matching Result:", result)  # Debugging output
    
    # Mengembalikan hasil pencocokan dalam bentuk dictionary
    return result

# Fungsi untuk menormalisasi teks (menghapus non-alfanumerik dan mengubah menjadi huruf kecil)
def normalize_text(text: str) -> str:
    """Normalizes text by converting to lowercase and replacing non-alphanumeric characters with spaces."""
    return ''.join([char.lower() if char.isalnum() else ' ' for char in text])

# Contoh penggunaan
# keywords = ["python", "react", "sql", "developer", "data"]
# normalized_cv_content = "I am a Python developer with experience in React and SQL databases."

# # Menormalisasi teks
# normalized_keywords = [normalize_text(keyword) for keyword in keywords]
# normalized_cv_content = normalize_text(normalized_cv_content)

# # Pencocokan pola menggunakan Aho-Corasick
# result = aho_corasick_search(normalized_keywords, normalized_cv_content)

# # Menampilkan hasil pencocokan
# print("Matches found:")
# print(result)

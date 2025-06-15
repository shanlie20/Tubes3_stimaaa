from collections import deque

# Fungsi untuk menambahkan pola ke dalam trie
# Mengembalikan jumlah node yang baru
def add_pattern(pattern, trie, fail, output):
    node = 0
    for char in pattern:
        if char not in trie[node]:
            trie[node][char] = len(trie)
            trie.append({})
            fail.append(-1)
            output.append(set())
        node = trie[node][char]
    output[node].add(pattern)

# Fungsi untuk membangun fail function
def build_failure_function(trie, fail, output):
    queue = deque()

    for char_code in range(256):
        char = chr(char_code)
        if char in trie[0]:
            next_node = trie[0][char]
            fail[next_node] = 0
            queue.append(next_node)

    while queue:
        state = queue.popleft()
        for char, next_state in trie[state].items():
            fail_state = fail[state]            
            while fail_state != 0 and char not in trie[fail_state]:
                fail_state = fail[fail_state]
            
            if char in trie[fail_state]:
                fail[next_state] = trie[fail_state][char]
            else:
                fail[next_state] = 0

            output[next_state].update(output[fail[next_state]])
            
            queue.append(next_state)

# Fungsi pembantu untuk mendapatkan state berikutnya
# Ini menggabungkan trie traversal dengan fail function
def get_next_state(current_state, char, trie, fail):
    while current_state != 0 and char not in trie[current_state]:
        current_state = fail[current_state]
    if char in trie[current_state]:
        return trie[current_state][char]
    else:
        return 0

# Fungsi untuk mencari pola dalam teks
def search(text, trie, fail, output):
    node = 0
    result = {}
    for char in text:
        node = get_next_state(node, char, trie, fail)
        
        if output[node]:
            for pattern in output[node]:
                result[pattern] = result.get(pattern, 0) + 1
    return result

# Fungsi utama untuk mencocokkan keywords dengan teks
def aho_corasick_search(keywords, normalized_cv_content) -> dict:
    trie = [{}]
    fail = [0] 
    output = [set()]

    for pattern in keywords:
        add_pattern(pattern, trie, fail, output)
    build_failure_function(trie, fail, output)
    result = search(normalized_cv_content, trie, fail, output)    
    return result

# Fungsi untuk menormalisasi teks (menghapus non-alfanumerik dan mengubah menjadi huruf kecil)
def normalize_text(text: str) -> str:
    """Normalizes text by converting to lowercase and replacing non-alphanumeric characters with spaces."""
    normalized = ''.join([char.lower() if char.isalnum() else ' ' for char in text])
    return ' '.join(normalized.split())
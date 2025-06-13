# Rijndael S-box
Sbox = [
    [99,124,119,123,242,107,111,197,48,1,103,43,254,215,171,118],
    [202,130,201,125,250,89,71,240,173,212,162,175,156,164,114,192],
    [183,253,147,38,54,63,247,204,52,165,229,241,113,216,49,21],
    [4,199,35,195,24,150,5,154,7,18,128,226,235,39,178,117],
    [9,131,44,26,27,110,90,160,82,59,214,179,41,227,47,132],
    [83,209,0,237,32,252,177,91,106,203,190,57,74,76,88,207],
    [208,239,170,251,67,77,51,133,69,249,2,127,80,60,159,168],
    [81,163,64,143,146,157,56,245,188,182,218,33,16,255,243,210],
    [205,12,19,236,95,151,68,23,196,167,126,61,100,93,25,115],
    [96,129,79,220,34,42,144,136,70,238,184,20,222,94,11,219],
    [224,50,58,10,73,6,36,92,194,211,172,98,145,149,228,121],
    [231,200,55,109,141,213,78,169,108,86,244,234,101,122,174,8],
    [186,120,37,46,28,166,180,198,232,221,116,31,75,189,139,138],
    [112,62,181,102,72,3,246,14,97,53,87,185,134,193,29,158],
    [225,248,152,17,105,217,142,148,155,30,135,233,206,85,40,223],
    [140,161,137,13,191,230,66,104,65,153,45,15,176,84,187,22],
]

# Inversi S-box untuk dekripsi
InverseSbox = [
    [82,9,106,27,106,44,45,33,88,107,103,43,13,89,7,111],
    [129,21,44,60,47,32,26,55,93,70,52,88,77,66,108,41],
    [67,92,16,113,47,35,74,69,71,48,60,73,53,19,22,82],
    [118,2,12,45,30,56,25,23,100,42,5,21,61,39,10,49],
    [28,105,91,97,113,16,20,83,78,19,31,33,37,90,59,15],
    [18,116,112,39,48,62,49,117,9,115,8,64,25,13,14,70],
    [73,34,61,24,68,67,10,87,81,50,65,31,64,90,63,26],
    [73,71,50,41,40,103,35,19,43,17,45,107,5,58,56,50],
    [21,102,56,54,63,64,115,85,93,119,103,94,50,87,74,113],
    [108,110,103,79,89,32,25,31,62,110,94,97,29,55,48,56],
    [35,51,51,11,20,81,103,42,78,105,13,66,22,77,68,43],
    [25,28,45,12,11,34,52,56,49,78,27,37,13,107,71,88]
]

# Rcon untuk ekspansi kunci
Rcon = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

# AES Functions

# SubBytes: Substitusi dengan S-box
def sub_bytes(state):
    for i in range(4):
        for j in range(4):
            byte = state[i][j]
            state[i][j] = Sbox[byte >> 4][byte & 0x0F]
    return state

# ShiftRows: Pergeseran baris data
def shift_rows(state):
    for i in range(1, 4):
        state[i] = state[i][i:] + state[i][:i]
    return state

# xtime: Operasi untuk MixColumns
def xtime(a):
    return (((a << 1) ^ 0x1b) & 0xff) if (a & 0x80) else (a << 1)

# MixColumns
def mix_single_column(a):
    t = a[0] ^ a[1] ^ a[2] ^ a[3]
    u = a[0]
    a[0] ^= t ^ xtime(a[0] ^ a[1])
    a[1] ^= t ^ xtime(a[1] ^ a[2])
    a[2] ^= t ^ xtime(a[2] ^ a[3])
    a[3] ^= t ^ xtime(a[3] ^ u)
    return a

def mix_columns(state):
    for i in range(4):
        col = [state[j][i] for j in range(4)]
        mixed = mix_single_column(col)
        for j in range(4):
            state[j][i] = mixed[j]
    return state

# AddRoundKey: XOR state dengan kunci
def add_round_key(state, key):
    for i in range(4):
        for j in range(4):
            state[i][j] ^= key[i][j]
    return state

# Key Expansion: Ekspansi kunci AES
def key_expansion(key):
    Nk = 4
    Nb = 4
    Nr = 10
    w = [ [0]*4 for _ in range(Nb*(Nr+1)) ]
    for i in range(Nk):
        for j in range(4):
            w[i][j] = key[j][i]
    for i in range(Nk, Nb*(Nr+1)):
        temp = w[i-1][:]  # Salin kolom terakhir
        if i % Nk == 0:
            temp = temp[1:] + temp[:1]
            for j in range(4):
                temp[j] = Sbox[temp[j] >> 4][temp[j] & 0x0F]  # Substitusi byte
            temp[0] ^= Rcon[i//Nk]  # XOR dengan Rcon
        for j in range(4):
            w[i][j] = w[i-Nk][j] ^ temp[j]
    round_keys = []
    for i in range(0, len(w), 4):
        round_keys.append([w[i], w[i+1], w[i+2], w[i+3]])
    round_keys = [ [ [rk[row][col] for row in range(4)] for col in range(4) ] for rk in round_keys ]
    return round_keys

# Konversi bytes ke matriks 4x4
def bytes2matrix(text):
    return [ list(text[i:i+4]) for i in range(0, len(text), 4)]

# Konversi matriks 4x4 ke bytes
def matrix2bytes(matrix):
    return bytes(sum(matrix, []))

# Fungsi untuk padding PKCS7
def pad(data):
    pad_length = 16 - len(data) % 16
    return data + bytes([pad_length] * pad_length)

# Fungsi untuk menghapus padding PKCS7
def unpad(data):
    pad_length = data[-1]
    return data[:-pad_length]

# AES Enkripsi dengan padding
def aes_encrypt(plaintext, key):
    assert len(key) == 16  # Pastikan kunci berukuran 16 byte
    plaintext = pad(plaintext)  # Padding plaintext agar panjangnya 16 byte
    state = bytes2matrix(plaintext)
    round_keys = key_expansion(bytes2matrix(key))
    state = add_round_key(state, round_keys[0])
    for rnd in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, round_keys[rnd])
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, round_keys[10])
    return matrix2bytes(state)

# AES Dekripsi dengan padding
def aes_decrypt(ciphertext, key):
    assert len(key) == 16  # Pastikan kunci berukuran 16 byte
    state = bytes2matrix(ciphertext)
    round_keys = key_expansion(bytes2matrix(key))
    state = add_round_key(state, round_keys[10])  # Round 10, key
    for rnd in range(9, 0, -1):
        state = inverse_shift_rows(state)
        state = inverse_sub_bytes(state)
        state = add_round_key(state, round_keys[rnd])
        state = inverse_mix_columns(state)
    state = inverse_shift_rows(state)
    state = inverse_sub_bytes(state)
    state = add_round_key(state, round_keys[0])  # Round 0, key
    decrypted_data = matrix2bytes(state)
    return unpad(decrypted_data)  # Hapus padding setelah dekripsi

# Fungsi inverse_shift_rows (membalikkan pergeseran baris untuk dekripsi)
def inverse_shift_rows(state):
    for i in range(1, 4):
        state[i] = state[i][-i:] + state[i][:-i]  # Geser ke kiri untuk dekripsi
    return state

# Fungsi inverse_sub_bytes untuk dekripsi (menggunakan inverse S-box)
# Inversi SubBytes untuk dekripsi
def inverse_sub_bytes(state):
    for i in range(4):
        for j in range(4):
            byte = state[i][j]
            row = byte >> 4
            col = byte & 0x0F
            # Pastikan row dan col berada dalam rentang 0-15
            if row < 0 or row > 15 or col < 0 or col > 15:
                raise ValueError(f"Invalid byte value: {byte}. Byte should be in the range 0-255.")
            state[i][j] = InverseSbox[row][col]
    return state


# Inversi MixColumns
def inverse_mix_single_column(a):
    # Matriks Inverse MixColumns dalam GF(2^8)
    m = [
        [14, 11, 13, 9],
        [9, 14, 11, 13],
        [13, 9, 14, 11],
        [11, 13, 9, 14]
    ]
    
    # Perkalian matriks dalam GF(2^8)
    result = [0] * 4
    for i in range(4):
        result[i] = 0
        for j in range(4):
            result[i] ^= gf_mult(m[i][j], a[j])  # Lakukan perkalian dalam GF(2^8)
    return result

# Fungsi perkalian dalam GF(2^8)
def gf_mult(a, b):
    p = 0
    hi_bit_set = 0x80
    mask = 0xFF
    for i in range(8):
        if (b & 1) != 0:
            p ^= a
        hi_bit_set = a & hi_bit_set
        a <<= 1
        if hi_bit_set != 0:
            a ^= 0x11b  # Irreducible polynomial for GF(2^8)
        b >>= 1
    return p & mask

def inverse_mix_columns(state):
    for i in range(4):
        col = [state[j][i] for j in range(4)]
        mixed = inverse_mix_single_column(col)
        for j in range(4):
            state[j][i] = mixed[j]
    return state


# Contoh penggunaan:
plaintext = b"Semoga besok basdat, jarkom, sosif Am4nn..!!"  # Pastikan panjang plaintext 16 byte
key = b"RAHASIA_16_BYTE!"  # Kunci AES 128-bit
ciphertext = aes_encrypt(plaintext, key)
decrypted_data = aes_decrypt(ciphertext, key)

print("Ciphertext (hex):", ciphertext.hex())
print("Decrypted data:", decrypted_data.decode('utf-8'))

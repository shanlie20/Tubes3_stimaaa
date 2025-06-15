import sympy

# Fungsi untuk mencari d menggunakan sympy.mod_inverse()
def mod_inverse(e, phi_n):
    return sympy.mod_inverse(e, phi_n)

# Fungsi untuk mengubah string menjadi angka (menggunakan kode ASCII)
def string_to_int(message):
    return [ord(char) for char in message]

# Fungsi untuk mengubah angka kembali menjadi string
def int_to_string(int_list):
    return ''.join([chr(num) for num in int_list])

# Fungsi untuk mengubah angka menjadi string dalam bentuk heksadesimal
def int_to_hex(int_list):
    return ''.join([hex(num)[2:].zfill(4) for num in int_list])  # Menggunakan format hex

# Fungsi untuk mengubah string heksadesimal menjadi angka
def hex_to_int(hex_string):
    return [int(hex_string[i:i+4], 16) for i in range(0, len(hex_string), 4)]

# Fungsi enkripsi
def encrypt(message) -> str:
    p = 61
    q = 53
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = 17
    d = mod_inverse(e, phi_n)

    # Kunci publik dan privat
    public_key = (e, n)

    # Mengubah pesan menjadi angka dan mengenkripsi setiap angka
    message_int = string_to_int(message)
    ciphertext_int = [pow(num, e, n) for num in message_int]
    
    # Mengonversi ciphertext menjadi string heksadesimal
    ciphertext_hex = int_to_hex(ciphertext_int)
    ciphertext_hex = str(ciphertext_hex)  # Pastikan ciphertext_hex adalah string
    return ciphertext_hex

# Fungsi dekripsi
def decrypt(ciphertext_hex) -> str:
    p = 61
    q = 53
    n = p * q
    phi_n = (p - 1) * (q - 1)
    e = 17
    d = mod_inverse(e, phi_n)

    # Kunci publik dan privat
    private_key = (d, n)

    # Mengubah ciphertext heksadesimal menjadi angka
    ciphertext_int = hex_to_int(ciphertext_hex)

    # Mendekripsi setiap angka
    decrypted_int = [pow(num, d, n) for num in ciphertext_int]
    
    # Mengubah hasil dekripsi kembali menjadi string
    decrypted_message = int_to_string(decrypted_int)
    return decrypted_message

# # Contoh penggunaan
# message = "andrew ganteng 123+_+(&)"  # pesan dalam bentuk string
# ciphertext_hex = encrypt(message)
# decrypted_message = decrypt(ciphertext_hex)

# print("Pesan asli:", message)
# print("Ciphertext (heksadesimal):", ciphertext_hex)
# print("Pesan terdekripsi:", decrypted_message)
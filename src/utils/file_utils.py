import os

def read_file_content(file_path: str, encoding: str = 'utf-8') -> str | None:
    """
    Membaca seluruh konten dari sebuah file teks.

    Args:
        file_path (str): Path lengkap ke file.
        encoding (str): Encoding file. Defaultnya 'utf-8'.

    Returns:
        str | None: Konten file sebagai string, atau None jika terjadi error.
    """
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except FileNotFoundError:
        # print(f"Error: File not found at '{file_path}'") # Bisa di-log di aplikasi GUI
        return None
    except Exception as e:
        # print(f"Error reading file '{file_path}': {e}") # Bisa di-log di aplikasi GUI
        return None

def write_to_file(file_path: str, content: str, encoding: str = 'utf-8', mode: str = 'w') -> bool:
    """
    Menulis konten ke sebuah file. Direktori akan dibuat jika belum ada.

    Args:
        file_path (str): Path lengkap ke file.
        content (str): Konten yang akan ditulis.
        encoding (str): Encoding file. Defaultnya 'utf-8'.
        mode (str): Mode penulisan ('w' untuk overwrite, 'a' untuk append). Defaultnya 'w'.

    Returns:
        bool: True jika berhasil, False jika gagal.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True) # Pastikan direktori ada
        with open(file_path, mode, encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        # print(f"Error writing to file '{file_path}': {e}") # Bisa di-log di aplikasi GUI
        return False

def check_path_exists(path: str) -> bool:
    """
    Memeriksa apakah sebuah path (file atau folder) ada.

    Args:
        path (str): Path yang akan diperiksa.

    Returns:
        bool: True jika path ada, False jika tidak.
    """
    return os.path.exists(path)

def get_file_extension(file_path: str) -> str:
    """
    Mendapatkan ekstensi file dari sebuah path.

    Args:
        file_path (str): Path lengkap ke file.

    Returns:
        str: Ekstensi file (misal: '.pdf', '.txt'), atau string kosong jika tidak ada ekstensi.
    """
    return os.path.splitext(file_path)[1]

# Contoh penggunaan:
# from src.utils.file_utils import read_file_content, write_to_file, check_path_exists, get_file_extension
#
# # read_content = read_file_content("non_existent.txt")
# # if read_content is None:
# #     print("Failed to read non_existent.txt")
#
# # write_success = write_to_file("output/my_doc.txt", "Ini adalah contoh konten.")
# # if write_success:
# #     print("File written successfully.")
#
# # exists = check_path_exists("output/my_doc.txt")
# # print(f"File exists: {exists}")
#
# # ext = get_file_extension("document.pdf")
# # print(f"Extension: {ext}")
import time

def start_timer() -> float:
    """
    Memulai timer dan mengembalikan waktu awal (dalam detik).
    """
    return time.perf_counter()

def stop_timer(start_time: float, operation_name: str = "Operation") -> float:
    """
    Menghentikan timer, menghitung durasi, dan mencetak hasilnya.

    Args:
        start_time (float): Waktu awal yang dikembalikan oleh start_timer().
        operation_name (str): Nama operasi yang diukur waktunya.

    Returns:
        float: Waktu eksekusi dalam milidetik.
    """
    end_time = time.perf_counter()
    execution_time = (end_time - start_time) * 1000 # dalam milidetik
    print(f"'{operation_name}' completed in {execution_time:.4f} ms")
    return execution_time

# Contoh penggunaan:
# from src.utils.timer import start_timer, stop_timer
# import time
#
# start = start_timer()
# time.sleep(0.123)
# stop_timer(start, "Simulasi Proses")
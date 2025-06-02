import time
from typing import List, Tuple, Dict

from core import kmp_search, fuzzy_search, boyer_moore_search, parse_pdf_to_text
from utils.keyword_utils import normalize_text

# ALURNYA MASIH BELUM DISESUAIKAN DENGAN KONDISI ASLI

def perform_search(keywords: List[str], algorithm: str, top_n: int,
                   cv_paths: List[str]) -> Tuple[List[Dict], Dict[str, float]]:
    """
    Melakukan pencarian kata kunci di dokumen CV digital.

    Args:
        keywords (List[str]): Daftar kata kunci pencarian.
        algorithm (str): Algoritma pencarian exact match ("KMP" atau "Boyer-Moore").
        top_n (int): Jumlah hasil teratas yang ingin ditampilkan.
        cv_paths (List[str]): List path file PDF CV yang akan diproses.

    Returns:
        Tuple:
            - List[Dict]: Daftar hasil pencarian, tiap dict berisi:
                {"candidate_id", "name", "match_count", "matched_keywords"}.
            - Dict[str, float]: Waktu eksekusi pencarian {"exact_ms", "fuzzy_ms"}.
    """

    # Normalisasi semua keyword
    normalized_keywords = [normalize_text(kw) for kw in keywords]

    # Ekstrak dan normalisasi teks dari setiap CV
    all_cv_contents = []
    for idx, cv_path in enumerate(cv_paths, start=1):
        raw_text = parse_pdf_to_text(cv_path)
        if raw_text is None:
            # Jika gagal ekstraksi, bisa skip atau isi dengan string kosong
            raw_text = ""
        normalized_text = normalize_text(raw_text)
        all_cv_contents.append({
            "candidate_id": idx,
            "name": f"Candidate {idx}",
            "cv_path": cv_path,
            "content": normalized_text,
        })

    # Exact match search
    exact_start = time.perf_counter()

    candidate_matches = []
    keywords_found_global = set()

    for candidate in all_cv_contents:
        matched_keywords = []
        total_matches = 0

        text = candidate["content"]

        for kw in normalized_keywords:
            if algorithm.upper() == "KMP":
                occurrences = kmp_search(text, kw)
                count = len(occurrences)
            elif algorithm.upper() == "BOYER-MOORE":
                positions, found = boyer_moore_search(text, kw)
                count = len(positions) if found else 0
            else:
                # fallback naive search
                count = text.count(kw)

            if count > 0:
                matched_keywords.append(kw)
                total_matches += count
                keywords_found_global.add(kw)

        if total_matches > 0:
            candidate_matches.append({
                "candidate_id": candidate["candidate_id"],
                "name": candidate["name"],
                "match_count": total_matches,
                "matched_keywords": matched_keywords,
                "cv_path": candidate["cv_path"],
            })

    exact_elapsed = (time.perf_counter() - exact_start) * 1000

    # Fuzzy match search for keywords NOT found
    fuzzy_start = time.perf_counter()
    keywords_not_found = [kw for kw in normalized_keywords if kw not in keywords_found_global]

    for candidate in all_cv_contents:
        text = candidate["content"]
        for kw in keywords_not_found:
            if fuzzy_search(text, kw, threshold=0.8):
                # Cek apakah kandidat sudah ada di list
                existing = next((c for c in candidate_matches if c["candidate_id"] == candidate["candidate_id"]), None)
                if existing:
                    if kw not in existing["matched_keywords"]:
                        existing["matched_keywords"].append(kw)
                        existing["match_count"] += 1
                else:
                    candidate_matches.append({
                        "candidate_id": candidate["candidate_id"],
                        "name": candidate["name"],
                        "match_count": 1,
                        "matched_keywords": [kw],
                        "cv_path": candidate["cv_path"],
                    })

    fuzzy_elapsed = (time.perf_counter() - fuzzy_start) * 1000

    # Sort hasil berdasarkan match_count, descending
    candidate_matches.sort(key=lambda x: x["match_count"], reverse=True)
    top_results = candidate_matches[:top_n]

    timings = {"exact_ms": exact_elapsed, "fuzzy_ms": fuzzy_elapsed}
    return top_results, timings
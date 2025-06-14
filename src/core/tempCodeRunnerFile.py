if __name__ == "__main__":
    text_example = "hello world, this is a test of the fuzzy matching algorithm"
    keyword_example = "helo"  # Kata yang salah ketik
    threshold = 0.8  # Ambang batas kemiripan
    
    results = search_with_fuzzy_matching(text_example, keyword_example, threshold)
    
    # Menampilkan hasil pencarian
    print(f"Keyword: {keyword_example}")
    print(f"Fuzzy Matches Count: {results}")

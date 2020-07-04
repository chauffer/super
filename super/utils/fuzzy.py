from fuzzywuzzy import process

def fuz(word, words, default=None, threshold=60):
    result = process.extract(word, words, limit=1)
    print('fuz', word, result, words)
    return result[0][0] if result[0][1] > threshold else default

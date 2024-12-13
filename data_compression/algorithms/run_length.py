import re

def run_length_encoding(sequence):
    compressed = ''
    count = 1
    for i in range(1, len(sequence)):
        if sequence[i] == sequence[i-1]:
            count += 1
        else:
            compressed += sequence[i-1]
            if count >= 2:
                compressed += str(count)
            count = 1
    compressed += sequence[-1]
    compressed += str(count)
    return compressed


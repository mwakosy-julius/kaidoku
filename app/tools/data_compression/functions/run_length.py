def run_length_encoding(sequence):
    compressed = ""
    count = 1

    if not sequence:
        return ""

    for i in range(1, len(sequence)):
        if sequence[i] == sequence[i - 1]:
            count += 1
        else:
            compressed += sequence[i - 1]
            if count >= 2:
                compressed += str(count)
            count = 1

    # Add the last character
    compressed += sequence[-1]
    if count >= 2:
        compressed += str(count)

    return compressed


def run_length_decoding(compressed):
    if not compressed:
        return ""

    result = ""
    i = 0

    while i < len(compressed):
        char = compressed[i]
        i += 1

        # Check if the next characters form a number
        count_str = ""
        while i < len(compressed) and compressed[i].isdigit():
            count_str += compressed[i]
            i += 1

        count = int(count_str) if count_str else 1
        result += char * count

    return result

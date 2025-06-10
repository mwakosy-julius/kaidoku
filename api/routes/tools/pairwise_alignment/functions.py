import pandas as pd
import altair as alt


def format_sequence(sequence):
    sequence = sequence.upper()
    if sequence[0] == ">":
        sequence = sequence.splitlines()[1:]
        sequence = "".join(sequence).strip()
    else:
        sequence = "".join(sequence.splitlines()).strip()
    return sequence

def is_dna(seq):
    return set(seq).issubset({"A", "C", "G", "T"})


def matrix_subs():
    return {
        "col": ["A", "C", "G", "T"],
        "A": [4, -2, -1, -2],
        "C": [-2, 4, -2, -1],
        "G": [-1, -2, 4, -2],
        "T": [-2, -1, -2, 4],
    }


def calculate_score(base1, base2, matrix):
    j = matrix["col"].index(base1)
    return matrix[base2][j]


def maximum_score(base1, base2, side, top, diagonal):
    if (base1 == base2) and (diagonal >= side) and (diagonal >= top):
        return diagonal
    elif (base1 != base2) and (diagonal >= side) and (diagonal >= top):
        return diagonal
    elif (side >= top) and (side >= diagonal):
        return side
    return top


def create_path(base1, base2, side, top, diagonal):
    if (base1 == base2) and (diagonal >= side) and (diagonal >= top):
        return "\\"
    elif (base1 != base2) and (diagonal >= side) and (diagonal >= top):
        return "\\"
    elif (side >= top) and (side >= diagonal):
        return "-"
    return "|"


def lcs_global(seq1, seq2, matrix_subs):
    score = []
    path = []
    g = -3

    for i in range(0, len(seq1)):
        score.append([0] * len(seq2))
        path.append([""] * len(seq2))

    for i in range(0, len(seq1)):
        score[i][0] = g * i
        path[i][0] = "|"
    for j in range(0, len(seq2)):
        score[0][j] = g * j
        path[0][j] = "-"

    for i in range(1, len(seq1)):
        for j in range(1, len(seq2)):
            base1 = seq1[i]
            base2 = seq2[j]
            s = calculate_score(base1, base2, matrix_subs)

            side = score[i][j - 1]
            top = score[i - 1][j]
            diagonal = score[i - 1][j - 1]

            score[i][j] = maximum_score(base1, base2, side + g, top + g, diagonal + s)
            path[i][j] = create_path(base1, base2, side + g, top + g, diagonal + s)

    return path


def lcs_local(seq1, seq2, matrix_subs):
    score = []
    path = []
    g = -3

    for i in range(0, len(seq1)):
        score.append([0] * len(seq2))
        path.append([""] * len(seq2))

    for i in range(0, len(seq1)):
        path[i][0] = "|"
    for j in range(0, len(seq2)):
        path[0][j] = "-"

    for i in range(1, len(seq1)):
        for j in range(1, len(seq2)):
            base1 = seq1[i]
            base2 = seq2[j]
            s = calculate_score(base1, base2, matrix_subs)

            side = score[i][j - 1]
            top = score[i - 1][j]
            diagonal = score[i - 1][j - 1]

            score[i][j] = max(
                0, maximum_score(base1, base2, side + g, top + g, diagonal + s)
            )
            path[i][j] = create_path(base1, base2, side + g, top + g, diagonal + s)

    return score, path


def global_alignment(seq1, seq2, matrix_path, matrix_subs):
    ali_seq1 = ""
    ali_seq2 = ""
    g = -3
    match = 0
    mismatch = 0
    gap = 0
    score_final = 0

    i = len(seq1) - 1
    j = len(seq2) - 1

    while (i != 0) or (j != 0):
        s = calculate_score(seq1[i], seq2[j], matrix_subs)

        if matrix_path[i][j] == "\\" and seq1[i] == seq2[j]:
            ali_seq1 = seq1[i] + ali_seq1
            ali_seq2 = seq2[j] + ali_seq2
            match += 1
            score_final += s
            i -= 1
            j -= 1

        elif matrix_path[i][j] == "\\" and seq1[i] != seq2[j]:
            ali_seq1 = seq1[i] + ali_seq1
            ali_seq2 = seq2[j] + ali_seq2
            mismatch += 1
            score_final += s
            i -= 1
            j -= 1

        elif matrix_path[i][j] == "-":
            ali_seq1 = " - " + ali_seq1
            ali_seq2 = seq2[j] + ali_seq2
            gap += 1
            score_final += g
            j -= 1

        elif matrix_path[i][j] == "|":
            ali_seq1 = seq1[i] + ali_seq1
            ali_seq2 = " - " + ali_seq2
            gap += 1
            score_final += g
            i -= 1

    return match, mismatch, gap, score_final, ali_seq1, ali_seq2


def find_highest_value(seq1, matrix):
    highest_value_matrix = 0

    for i in range(len(seq1)):
        highest_value_in_line = max(matrix[i])
        if highest_value_in_line > highest_value_matrix:
            highest_value_matrix = highest_value_in_line
            line = i

    column = matrix[line].index(highest_value_matrix)
    return line, column


def local_alignment(seq1, seq2, score_matrix, matrix_path, matrix_subs):
    ali_seq1 = ""
    ali_seq2 = ""
    g = -3
    match = 0
    mismatch = 0
    gap = 0
    score_final = 0

    i, j = find_highest_value(seq1, score_matrix)
    value = score_matrix[i][j]

    while value > 0:
        s = calculate_score(seq1[i], seq2[j], matrix_subs)

        if matrix_path[i][j] == "\\" and seq1[i] == seq2[j]:
            ali_seq1 = seq1[i] + ali_seq1
            ali_seq2 = seq2[j] + ali_seq2
            match += 1
            score_final += s
            i -= 1
            j -= 1
            value = score_matrix[i][j]

        elif matrix_path[i][j] == "\\" and seq1[i] != seq2[j]:
            ali_seq1 = seq1[i] + ali_seq1
            ali_seq2 = seq2[j] + ali_seq2
            mismatch += 1
            score_final += s
            i -= 1
            j -= 1
            value = score_matrix[i][j]

        elif matrix_path[i][j] == "-":
            ali_seq1 = " - " + ali_seq1
            ali_seq2 = seq2[j] + ali_seq2
            gap += 1
            score_final += g
            j -= 1
            value = score_matrix[i][j]

        elif matrix_path[i][j] == "|":
            ali_seq1 = seq1[i] + ali_seq1
            ali_seq2 = " - " + ali_seq2
            gap += 1
            score_final += g
            i -= 1
            value = score_matrix[i][j]

    return match, mismatch, gap, score_final, ali_seq1, ali_seq2


def dataframe(sequence1, sequence2):
    try:
        return dict(
            [
                ("A ", [sequence1.upper().count("A"), sequence2.upper().count("A")]),
                ("G ", [sequence1.upper().count("G"), sequence2.upper().count("G")]),
                ("C ", [sequence1.upper().count("C"), sequence2.upper().count("C")]),
                ("T ", [sequence1.upper().count("T"), sequence2.upper().count("T")]),
                (
                    "Total",
                    [
                        (
                            sequence1.upper().count("A")
                            + sequence1.upper().count("G")
                            + sequence1.upper().count("C")
                            + sequence1.upper().count("T")
                        ),
                        (
                            sequence2.upper().count("A")
                            + sequence2.upper().count("G")
                            + sequence2.upper().count("C")
                            + sequence2.upper().count("T")
                        ),
                    ],
                ),
            ]
        )
    except ZeroDivisionError:
        return {}


def table(sequence1, sequence2):
    df_dict = dataframe(sequence1, sequence2)
    df = pd.DataFrame.from_dict(df_dict, orient="index")
    df = df.rename({0: "sequence1", 1: "sequence2"}, axis="columns")
    df.reset_index(inplace=True)
    df.rename(columns={"index": "nucleotide"}, inplace=True)
    return df


def bar_chart(sequence1, sequence2):
    ds = pd.DataFrame(
        [
            ["A", sequence1.upper().count("A"), "seq1"],
            ["C", sequence1.upper().count("C"), "seq1"],
            ["G", sequence1.upper().count("G"), "seq1"],
            ["T", sequence1.upper().count("T"), "seq1"],
            ["A", sequence2.upper().count("A"), "seq2"],
            ["C", sequence2.upper().count("C"), "seq2"],
            ["G", sequence2.upper().count("G"), "seq2"],
            ["T", sequence2.upper().count("T"), "seq2"],
        ],
        columns=["Nucleotide", "Percentage_Count", "Sequences"],
    )

    bar_chart = (
        alt.Chart(ds)
        .mark_bar()
        .encode(
            column=alt.Column("Nucleotide"),
            x=alt.X("Sequences"),
            y=alt.Y("Percentage_Count"),
            color=alt.Color("Sequences", scale=alt.Scale(range=["#EA98D2", "#659CCA"])),
        )
        .configure_view(
            strokeWidth=1.0,
        )
        .properties(height=200, width=80)
    )
    return bar_chart

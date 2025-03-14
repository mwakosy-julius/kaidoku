from django.shortcuts import render
from . import functions

def pairwise_alignment(request):
    if request.method == "POST":
        sequence1 = request.POST.get("sequence1", "")
        sequence2 = request.POST.get("sequence2", "")
        alignment_type = request.POST.get("alignment_type", "Global_Alignment")

        if sequence1 and sequence2:
            seq1 = functions.format_sequence(sequence1)
            seq2 = functions.format_sequence(sequence2)

            if functions.is_dna(seq1) and functions.is_dna(seq2):
                matrix = functions.matrix_subs()
                if alignment_type == "Global_Alignment":
                    path_matrix = functions.lcs_global(seq1, seq2, matrix)
                    results = functions.global_alignment(seq1, seq2, path_matrix, matrix)
                elif alignment_type == "Local_Alignment":
                    score_matrix, path_matrix = functions.lcs_local(seq1, seq2, matrix)
                    results = functions.local_alignment(seq1, seq2, score_matrix, path_matrix, matrix)
                df = functions.table(sequence1, sequence2)
                bar_chart = functions.bar_chart(sequence1, sequence2)
                return render(request, 'pairwise_alignment.html', {
                    'results': results,
                    'df': df.to_html(),
                    'bar_chart': bar_chart.to_html(),
                    'alignment_type': alignment_type,
                })
            else:
                error = "One or both sequences contain invalid DNA characters."
                return render(request, 'pairwise_alignment.html', {'error': error})
    return render(request, "pairwise_alignment.html")

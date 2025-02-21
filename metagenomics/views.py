from django.shortcuts import render
from . import functions

def metagenomics(request):
    results = None

    if request.method == "POST":
        sequence = request.POST.get("sequence", "").strip()  
        sequences = functions.format_sequence(sequence)
        gc_content = functions.calculate_gc_content(sequences)
        kmer_counts, kmer_percentages = functions.count_kmers(sequences)
        
        kmer_info = []
        for kmer in kmer_counts:
            kmer_info.append({
                "kmer": kmer,
                "count": kmer_counts[kmer],
                "percentage": kmer_percentages.get(kmer, 0)
            })
        
        chart = functions.generate_kmer_bar_chart(kmer_counts)
        
        results = {
            "gc_content": gc_content,
            "kmer_info": kmer_info,
            "chart": chart,
            "sequences": sequences,
        }
    
    return render(request, "metagenomics.html", {'results': results})

    
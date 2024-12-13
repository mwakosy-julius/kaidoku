from django.shortcuts import render
from .forms import CompressionForm
from .algorithms import run_length, consensus, delta_compression

def data_compression(request):
    if request.method == "POST":
        form = CompressionForm(request.POST, request.FILES)
        if form.is_valid():
            method = form.cleaned_data['compression_method']
            sequence_file = request.FILES['file'].read().decode('utf-8')
            reference_file = form.cleaned_data.get('reference_file')

            if method == 'run_length':
                compressed = run_length.run_length_encoding(sequence_file)
            elif method == 'consensus':
                sequences = consensus.read_fasta(sequence_file)
                compressed = consensus.generate_consensus(sequences)
            elif method == 'delta' and reference_file:
                reference = reference_file.read().decode('utf-8')
                compressed = delta_compression.delta_compress(sequence_file, reference)
            else:
                compressed = "Invalid input or missing reference file."

            return render(request, 'result.html', {
                'compressed_data': compressed
            })
    else:
        form = CompressionForm()

    return render(request, 'home.html', {'form': form})

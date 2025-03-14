from plotly.graph_objects import Scatter, Figure

def calculate_gc_content(sequence, window_size=100):
    gc_content = []
    positions = []
    for i in range(0, len(sequence) - window_size + 1, window_size):
        window = sequence[i:i + window_size]
        gc_count = window.count('G') + window.count('C')
        gc_content.append((gc_count / window_size) * 100)
        positions.append(i)
    return positions, gc_content

def plot_gc_content(positions, gc_content, window_size):
    fig = Figure()
    fig.add_trace(Scatter(
        x=positions, y=gc_content,
        mode='lines+markers',
        name='GC Content',
        marker=dict(color='blue', size=6),
        line=dict(color='blue', width=2)
    ))
    fig.update_layout(
        title=f'GC Content Across Gene (Window size: {window_size} bp)',
        xaxis_title='Position in Gene',
        yaxis_title='GC Content (%)',
        template='plotly_white'
    )
    return fig.to_html(full_html=False)

def calculate_nucleotide_counts(sequence):
    total_length = len(sequence)
    counts = {
        'A': sequence.count('A'),
        'T': sequence.count('T'),
        'G': sequence.count('G'),
        'C': sequence.count('C')
    }
    percentages = {nuc: (count / total_length) * 100 for nuc, count in counts.items()}
    return total_length, counts, percentages
import numpy as np

def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)
    return wave

def combine_waves(waves):
    return np.concatenate(waves)

def sequence_validator(sequence):
    sequence = sequence.upper()
    if sequence[0] == ">":
        sequence = sequence.splitlines()
        sequence = sequence[1:]
        sequence = "".join(sequence).strip()
    else:
        sequence = sequence.splitlines()
        sequence = "".join(sequence).strip()
    return sequence

def is_dna(sequence):
    return set(sequence).issubset({"A", "C", "G", "T"})

def get_next_index(current_index, step, scale_length):
    new_index = current_index + step
    if new_index < 0:
        new_index = -new_index  # Reflect at lower bound
    elif new_index >= scale_length:
        new_index = 2 * (scale_length - 1) - new_index  # Reflect at upper bound
    return new_index

def melody_maker(sequence):
    melody_scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C4 to C5
    step_mapping = {'A': 1, 'T': -1, 'C': 2, 'G': -2}
    current_index = 0
    scale_length = len(melody_scale)
    melody_freq = []

    for nucleotide in sequence:
        if nucleotide in step_mapping:
            step = step_mapping[nucleotide]
            current_index = get_next_index(current_index, step, scale_length)
            melody_freq.append(melody_scale[current_index])

    return melody_freq

def get_chord_freqs(melody_freq, melody_scale, chord_scale):
    try:
        index = melody_scale.index(melody_freq)
    except ValueError:
        index = min(range(len(melody_scale)), key=lambda i: abs(melody_scale[i] - melody_freq))
    # Simplified chord: root, third, fifth
    chord_indices = [index % 7, (index + 2) % 7, (index + 4) % 7]
    chord_freqs = [chord_scale[i] for i in chord_indices]
    return chord_freqs

def generate_chord_wave(chord_freqs, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    chord_wave = sum(np.sin(2 * np.pi * freq * t) for freq in chord_freqs)
    return chord_wave / len(chord_freqs)  # Normalize

def generate_combined_wave(melody_freq, chunk_size=4, duration_per_note=0.25, sample_rate=44100):
    melody_scale = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C4 to C5
    chord_scale = [130.81, 146.83, 164.81, 174.61, 196.00, 220.00, 246.94, 261.63]  # C3 to C4
    combined_waves = []

    for i in range(0, len(melody_freq), chunk_size):
        chunk = melody_freq[i:i + chunk_size]
        if not chunk:
            break

        # Generate melody wave for chunk
        melody_wave_chunk = np.concatenate([generate_sine_wave(freq, duration_per_note, sample_rate) for freq in chunk])

        # Generate chord wave based on first note
        chord_freqs = get_chord_freqs(chunk[0], melody_scale, chord_scale)
        chunk_duration = len(chunk) * duration_per_note
        chord_wave = generate_chord_wave(chord_freqs, chunk_duration, sample_rate)

        # Mix and normalize
        combined_wave = (melody_wave_chunk + chord_wave) / 2
        combined_waves.append(combined_wave)

    return np.concatenate(combined_waves)
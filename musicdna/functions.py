import numpy as np
import sounddevice as sd

def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)  # Generate equally spaced points in time
    wave = np.sin(2 * np.pi * frequency * t)  # Generate the sine wave
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
    if set(sequence).issubset({"A", "C", "G", "T"}):
        return True
    else:
        return False

notes = {
    'C': 261.63,  
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88,
    'Eb': 311.13,
    'Ab': 415.30,
    'Bb': 466.16
}

scales = {
    'major': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
    'minor': ['C', 'D', 'Eb', 'F', 'G', 'Ab', 'Bb'],
    'pentatonic': ['C', 'D', 'E', 'G', 'A']
}

def get_scale_notes(scale_name):
    return scales.get(scale_name, scales['major'])

def melody_maker(sequence, scale='major'):
    scale_notes = get_scale_notes(scale)
    melody = []
    for nucleotide in sequence:
        if nucleotide == 'A':
            melody.extend(scale_notes[0:3])  # Chord from scale
        elif nucleotide == 'C':
            melody.extend(scale_notes[2:5])
        elif nucleotide == 'G':
            melody.extend(scale_notes[3:6])
        elif nucleotide == 'T':
            melody.extend(scale_notes[1:4])
    return melody

def play_melody(melody, rhythm_pattern=None):
    if rhythm_pattern is None:
        rhythm_pattern = [0.5] * len(melody)  # Default to uniform rhythm
    
    melody_wave = []
    for note, duration in zip(melody, rhythm_pattern):
        frequency = notes.get(note, 261.63)  # Default to C if note not found
        note_wave = generate_sine_wave(frequency, duration)
        melody_wave.append(note_wave)

    melody_wave_combined = combine_waves(melody_wave)
    melody_wave_scaled = np.int16(melody_wave_combined * 32767)
    sd.play(melody_wave_scaled, samplerate=44100)
    sd.wait()

def generate_rhythm(sequence):
    return [0.25 if nucleotide in 'AT' else 0.5 for nucleotide in sequence]

def harmony_maker(sequence, scale='major'):
    scale_notes = get_scale_notes(scale)
    harmony = []
    for i in range(0, len(sequence) - 2, 3):  # Process codons
        codon = sequence[i:i+3]
        if set(codon) == {'A', 'T'}:
            harmony.append(scale_notes[0])  # Root
        elif set(codon) == {'C', 'G'}:
            harmony.append(scale_notes[4])  # Fifth
        else:
            harmony.append(scale_notes[2])  # Third
    return harmony

def play_melody_with_harmony(melody, harmony):
    melody_wave = [generate_sine_wave(notes[note], 0.5) for note in melody]
    harmony_wave = [generate_sine_wave(notes[note], 0.5) for note in harmony]
    
    combined_wave = [
        m + h if len(h) == len(m) else m 
        for m, h in zip(melody_wave, harmony_wave)
    ]
    
    combined_wave = combine_waves(combined_wave)
    combined_wave_scaled = np.int16(combined_wave * 32767)
    sd.play(combined_wave_scaled, samplerate=44100)
    sd.wait()
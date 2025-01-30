import numpy as np
import sounddevice as sd

def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)  
    wave = np.sin(2 * np.pi * frequency * t)  
    return wave

def combine_waves(waves):
    return np.concatenate(waves)

notes = {
    'C': 261.63,
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88
}

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

def melody_maker(sequence):
    #sequence = sequence.upper()
    melody = []
    for nucleotide in sequence:
        if nucleotide == 'A':
            melody.extend(['C','E','G'])
        elif nucleotide == 'C':
            melody.extend(['E','G','B'])
        elif nucleotide == 'G':
            melody.extend(['F','A','C'])
        elif nucleotide == 'T':
            melody.extend(['D','F','A'])
    return melody

def play_melody(melody):
    melody_duration = 0.5  
    melody_wave = []
    for note in melody:
        frequency = notes[note]  
        note_wave = generate_sine_wave(frequency, melody_duration)  
        melody_wave.append(note_wave)  

    melody_wave_combined = combine_waves(melody_wave)

    melody_wave_scaled = np.int16(melody_wave_combined * 32767)

    sd.play(melody_wave_scaled, samplerate=44100)
    sd.wait()
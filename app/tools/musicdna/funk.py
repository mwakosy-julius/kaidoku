import numpy as np
import sounddevice as sd
import sys
import subprocess
import math
import random

# devices = sd.query_devices()
# print(devices)

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

#########################################
# Note definitions for the C major scale
#########################################
notes_freq = {
    'C': 261.63,
    'D': 293.66,
    'E': 329.63,
    'F': 349.23,
    'G': 392.00,
    'A': 440.00,
    'B': 493.88
}

#########################################
# Sine wave generator for a given note
#########################################
def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)
    return wave

def combine_waves(waves):
    return np.concatenate(waves)

#####################################################
# Uniform system volume getter (OS-specific branch)
#####################################################
def get_system_volume():
    """Return a normalized linear volume factor (0.0 to 1.0) based on the OS master volume."""
    if sys.platform.startswith("win"):
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            currentVolumeDb = volume_interface.GetMasterVolumeLevel()
            # Convert dB to a linear factor (assuming 0 dB means full volume)
            return math.pow(10, currentVolumeDb / 20.0)
        except Exception:
            return 1.0
    elif sys.platform.startswith("darwin"):
        try:
            # Use osascript to query output volume (returns 0-100)
            result = subprocess.run(
                ['osascript', '-e', 'output volume of (get volume settings)'],
                capture_output=True, text=True
            )
            vol = float(result.stdout.strip())
            return vol / 100.0
        except Exception:
            return 1.0
    elif sys.platform.startswith("linux"):
        try:
            # Use 'amixer' to get Master volume; parsing depends on your configuration
            result = subprocess.run(
                ['amixer', 'get', 'Master'],
                capture_output=True, text=True
            )
            import re
            m = re.search(r'\[(\d+)%\]', result.stdout)
            if m:
                vol = float(m.group(1))
                return vol / 100.0
            else:
                return 1.0
        except Exception:
            return 1.0
    else:
        return 1.0

#####################################################
# Markov chain transition probabilities over notes
#####################################################
transition_prob = {
    'C': {'C':0.1, 'D':0.2, 'E':0.3, 'F':0.1, 'G':0.2, 'A':0.05, 'B':0.05},
    'D': {'C':0.15, 'D':0.1, 'E':0.25, 'F':0.15, 'G':0.2, 'A':0.1, 'B':0.05},
    'E': {'C':0.1, 'D':0.2, 'E':0.1, 'F':0.2, 'G':0.2, 'A':0.1, 'B':0.1},
    'F': {'C':0.1, 'D':0.2, 'E':0.2, 'F':0.1, 'G':0.2, 'A':0.1, 'B':0.1},
    'G': {'C':0.2, 'D':0.15, 'E':0.15, 'F':0.15, 'G':0.1, 'A':0.15, 'B':0.1},
    'A': {'C':0.1, 'D':0.15, 'E':0.2, 'F':0.1, 'G':0.2, 'A':0.1, 'B':0.15},
    'B': {'C':0.15, 'D':0.1, 'E':0.15, 'F':0.15, 'G':0.1, 'A':0.2, 'B':0.15},
}

def choose_next_note(current_note):
    """Select the next note based on weighted probabilities."""
    probs = transition_prob.get(current_note, {})
    notes = list(probs.keys())
    weights = list(probs.values())
    return random.choices(notes, weights=weights, k=1)[0]

#####################################################
# Generate a motif from a DNA sequence as a seed.
#####################################################
def generate_motif_from_dna(sequence, desired_length=None):
    """
    Use the DNA sequence (only A, C, G, T) to seed a motif.
    The first nucleotide determines the starting note.
    """
    # Define a simple mapping from nucleotides to starting indices in the scale:
    mapping = {"A": 0, "C": 1, "G": 2, "T": 3}
    scale = list(notes_freq.keys())
    starting_index = mapping.get(sequence[0], 0)
    starting_note = scale[starting_index % len(scale)]

    if desired_length is None:
        desired_length = len(sequence)

    motif = []
    for i in range(desired_length):
        # Use the nucleotide at position i mod len(sequence)
        nucleotide = sequence[i % len(sequence)]
        # Incorporate the position (i) so that different positions generate different offsets.
        index = (mapping[nucleotide] + i) % len(scale)
        motif.append(scale[index])
    return motif

#####################################################
# Generate a rhythmic pattern (variable durations)
#####################################################
def generate_rhythmic_pattern(length):
    """Return a list of durations (in seconds) for each note."""
    durations = [0.25, 0.5, 0.75, 1.0]  # Example durations
    weights = [0.3, 0.4, 0.2, 0.1]       # Favoring 0.5 sec
    pattern = random.choices(durations, weights=weights, k=length)
    return pattern

#####################################################
# Transformation: Invert the motif
#####################################################
def invert_motif(motif):
    """Invert the motif around the midpoint of the scale."""
    scale = list(notes_freq.keys())
    indices = [scale.index(note) for note in motif]
    midpoint = len(scale) // 2
    inverted_indices = [midpoint - (i - midpoint) for i in indices]
    # Clamp indices to valid range
    inverted_indices = [max(0, min(len(scale) - 1, i)) for i in inverted_indices]
    inverted_motif = [scale[i] for i in inverted_indices]
    return inverted_motif

#####################################################
# Main function: Generate and play a melody from a DNA sequence
#####################################################
def play_musicdna(sequence, use_inversion=False, desired_length=None, volume_factor=None):
    """
    Generate a melody from a DNA sequence:
      - The DNA seed selects an initial motif using a Markov chain.
      - A rhythmic pattern is generated for note durations.
      - Optionally, the motif is inverted.
      - The overall amplitude is scaled using the system volume.
    """
    motif = generate_motif_from_dna(sequence, desired_length=desired_length)
    
    if use_inversion:
        motif = invert_motif(motif)
    
    rhythm = generate_rhythmic_pattern(len(motif))
    
    waves = []
    # Generate each note's wave using its corresponding duration.
    for note, duration in zip(motif, rhythm):
        freq = notes_freq[note]
        wave = generate_sine_wave(freq, duration)
        waves.append(wave)
    
    combined_wave = combine_waves(waves)
    
    # Determine volume scaling factor:
    if volume_factor is None:
        volume_factor = get_system_volume()
    
    # Scale the waveform (assuming combined_wave values are in -1 to 1)
    scaled_wave = np.int16(combined_wave * volume_factor * 32767)
    
    # Play the resulting melody.
    sd.play(scaled_wave, samplerate=44100)
    sd.wait()
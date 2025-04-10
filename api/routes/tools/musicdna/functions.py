import sys
import subprocess
import math
import numpy as np
import sounddevice as sd

devices = sd.query_devices()

# for i, dev in enumerate(devices):
#     if 'bluetooth' in dev['name'].lower():
#         bluetooth_device = i
#         break

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


def get_system_volume():
    if sys.platform.startswith("win"):
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
            currentVolumeDb = volume_interface.GetMasterVolumeLevel()
            return math.pow(10, currentVolumeDb / 20.0)
        except Exception:
            return 1.0

    elif sys.platform.startswith("darwin"):
        try:
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

def play_melody(melody):
    melody_duration = 0.5  
    melody_wave = []
    for note in melody:
        frequency = notes[note]  
        note_wave = generate_sine_wave(frequency, melody_duration)  
        melody_wave.append(note_wave)  

    melody_wave_combined = combine_waves(melody_wave)

    volume_factor = get_system_volume()

    melody_wave_scaled = np.int16(melody_wave_combined * volume_factor * 32767)
    sd.play(melody_wave_scaled, samplerate=44100)
    sd.wait()

    # if bluetooth_device is not None:
    #     sd.default.device = (None, bluetooth_device) 
    #     # sd.play(melody_wave_scaled, samplerate=44100)
    #     # sd.wait()
    # else:
    #     # sd.play(melody_wave_scaled, samplerate=44100)
    #     # sd.wait()
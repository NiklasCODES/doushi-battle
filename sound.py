"""
8-Bit Chiptune Sound & Music Engine for Doushi Battle.
Features:
- Pure Python synthesis of authentic GameBoy sound effects
- Full 8-bit battle soundtrack with driving bassline, retro lead melody, and 8-bit drum beats
- Seamless background music loop management (macOS afplay / Linux / Windows)
"""

import os
import sys
import math
import struct
import wave
import subprocess
import threading
import time
from pathlib import Path

SOUNDS_DIR = Path(__file__).parent / "assets" / "sounds"
SOUNDS_DIR.mkdir(parents=True, exist_ok=True)

SOUND_ENABLED = True

# Global music process controller
_music_process = None
_music_thread = None
_music_running = False


def generate_wave(filename: str, samples: list, sample_rate: int = 22050):
    """Saves raw 16-bit mono audio samples to a WAV file."""
    filepath = SOUNDS_DIR / filename
    if filepath.exists():
        return
    with wave.open(str(filepath), "w") as wav_file:
        wav_file.setnchannels(1)        # Mono
        wav_file.setsampwidth(2)        # 16-bit
        wav_file.setframerate(sample_rate)
        packed_data = bytearray()
        for sample in samples:
            clamped = max(-32767, min(32767, int(sample * 32767)))
            packed_data.extend(struct.pack("<h", clamped))
        wav_file.writeframes(packed_data)


def square_wave(freq: float, t: float, duty: float = 0.5) -> float:
    """Generates an authentic 8-bit square/pulse wave."""
    if freq <= 0:
        return 0.0
    phase = (freq * t) % 1.0
    return 1.0 if phase < duty else -1.0


def note_to_freq(note: str) -> float:
    """Converts note names to Hz frequency."""
    note_map = {
        "C2": 65.41, "D2": 73.42, "E2": 82.41, "F2": 87.31, "G2": 98.00, "G#2": 103.83, "A2": 110.00, "B2": 123.47,
        "C3": 130.81, "D3": 146.83, "E3": 164.81, "F3": 174.61, "G3": 196.00, "G#3": 207.65, "A3": 220.00, "B3": 246.94,
        "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.00, "G#4": 415.30, "A4": 440.00, "B4": 493.88,
        "C5": 523.25, "D5": 587.33, "E5": 659.25, "F5": 698.46, "G5": 783.99, "G#5": 830.61, "A5": 880.00, "B5": 987.77,
        "C6": 1046.50, "D6": 1174.66, "REST": 0.0
    }
    return note_map.get(note, 0.0)


def synthesize_battle_beat():
    """
    Synthesizes a driving 140 BPM 8-bit Pokémon battle soundtrack:
    - Track 1: Rapid 16th-note square bassline (A minor / D minor progression)
    - Track 2: High-energy melodic lead pulse wave
    - Track 3: 8-Bit noise snare & kick drum percussion
    """
    sample_rate = 22050
    bpm = 140.0
    beat_dur = 60.0 / bpm            # ~0.428 sec per beat
    sixteenth_dur = beat_dur / 4.0   # ~0.107 sec

    # 4 bars of 4/4 = 16 beats total
    total_beats = 16
    total_duration = total_beats * beat_dur
    total_samples = int(sample_rate * total_duration)

    # 1. Bassline (16th notes pattern)
    bass_notes_bar1 = ["A2", "A2", "C3", "E3", "A2", "A2", "C3", "E3", "A2", "A2", "C3", "E3", "A2", "C3", "D3", "E3"]
    bass_notes_bar2 = ["F2", "F2", "A2", "C3", "F2", "F2", "A2", "C3", "F2", "F2", "A2", "C3", "F2", "A2", "B2", "C3"]
    bass_notes_bar3 = ["D2", "D2", "F2", "A2", "D2", "D2", "F2", "A2", "D2", "D2", "F2", "A2", "D2", "F2", "G2", "A2"]
    bass_notes_bar4 = ["E2", "E2", "G#2", "B2", "E2", "E2", "G#2", "B2", "E2", "E2", "G#2", "B2", "E2", "G#2", "B2", "D3"]
    all_bass = bass_notes_bar1 + bass_notes_bar2 + bass_notes_bar3 + bass_notes_bar4

    # 2. Lead Melody (Note, duration_in_sixteenths)
    melody = [
        # Bar 1 (A minor)
        ("A4", 4), ("C5", 2), ("D5", 2), ("E5", 6), ("D5", 2),
        # Bar 2 (F major)
        ("C5", 4), ("D5", 2), ("C5", 2), ("A4", 6), ("C5", 2),
        # Bar 3 (D minor)
        ("D5", 4), ("E5", 2), ("F5", 2), ("A5", 6), ("G5", 2),
        # Bar 4 (E dominant)
        ("E5", 4), ("B4", 4), ("G#4", 6), ("REST", 2)
    ]

    samples = [0.0] * total_samples

    # Render Bassline
    for step, note_name in enumerate(all_bass):
        freq = note_to_freq(note_name)
        start_idx = int(step * sixteenth_dur * sample_rate)
        end_idx = min(total_samples, int((step + 1) * sixteenth_dur * sample_rate))
        step_len = end_idx - start_idx
        for i in range(step_len):
            idx = start_idx + i
            t = i / sample_rate
            env = max(0.0, 1.0 - (i / step_len) * 0.4)
            samples[idx] += square_wave(freq, t, 0.5) * 0.22 * env

    # Render Melody
    cur_step = 0
    for note_name, num_steps in melody:
        freq = note_to_freq(note_name)
        start_idx = int(cur_step * sixteenth_dur * sample_rate)
        end_idx = min(total_samples, int((cur_step + num_steps) * sixteenth_dur * sample_rate))
        note_len = end_idx - start_idx
        for i in range(note_len):
            idx = start_idx + i
            t = i / sample_rate
            env = max(0.0, 1.0 - (i / note_len) * 0.2)
            samples[idx] += square_wave(freq, t, 0.25) * 0.26 * env
        cur_step += num_steps

    # Render Percussion (Drums: Kick on 1&3, Snare on 2&4, Hi-hat on 8ths)
    for beat in range(total_beats):
        beat_start = int(beat * beat_dur * sample_rate)
        
        # Kick drum on 0, 2 (beats 1, 3)
        if beat % 2 == 0:
            k_len = int(sample_rate * 0.08)
            for i in range(k_len):
                if beat_start + i < total_samples:
                    t = i / sample_rate
                    k_freq = max(40, 180 - (t * 1800))
                    k_env = max(0.0, 1.0 - (i / k_len))
                    samples[beat_start + i] += square_wave(k_freq, t, 0.5) * 0.35 * k_env

        # Snare drum on 1, 3 (beats 2, 4)
        else:
            s_len = int(sample_rate * 0.10)
            for i in range(s_len):
                if beat_start + i < total_samples:
                    noise = (hash(beat_start + i) % 100 - 50) / 50.0
                    s_env = max(0.0, 1.0 - (i / s_len)) ** 1.8
                    samples[beat_start + i] += noise * 0.28 * s_env

    generate_wave("battle_beat.wav", samples, sample_rate)


def init_8bit_sound_library():
    """Synthesizes all retro sound effects and the background battle track."""
    sample_rate = 22050

    # 1. Menu / Dialogue Blip
    duration = 0.04
    blip_samples = []
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        freq = 880 if t < 0.02 else 1174
        val = 0.25 if (math.sin(2 * math.pi * freq * t) > 0) else -0.25
        decay = 1.0 - (t / duration)
        blip_samples.append(val * decay)
    generate_wave("blip.wav", blip_samples, sample_rate)

    # 2. Hit Impact
    duration = 0.12
    hit_samples = []
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        freq = max(80, 450 - (t * 3000))
        val = 0.4 if (math.sin(2 * math.pi * freq * t) > 0) else -0.4
        noise = (hash(i) % 100 - 50) / 150.0
        decay = (1.0 - (t / duration)) ** 1.5
        hit_samples.append((val * 0.7 + noise * 0.3) * decay)
    generate_wave("hit.wav", hit_samples, sample_rate)

    # 3. Critical Hit
    duration = 0.22
    crit_samples = []
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        freq = 750 if t < 0.08 else max(100, 900 - (t * 3500))
        val = 0.5 if (math.sin(2 * math.pi * freq * t) > 0) else -0.5
        noise = (hash(i) % 100 - 50) / 100.0
        decay = (1.0 - (t / duration))
        crit_samples.append((val * 0.6 + noise * 0.4) * decay)
    generate_wave("crit.wav", crit_samples, sample_rate)

    # 4. Doushi ML Scan Chirp
    duration = 0.20
    scan_samples = []
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        freq = 500 + (t * 2400)
        val = 0.35 if (math.sin(2 * math.pi * freq * t) > 0) else -0.35
        decay = 1.0 - (t / duration) * 0.5
        scan_samples.append(val * decay)
    generate_wave("scan.wav", scan_samples, sample_rate)

    # 5. Victory Fanfare
    victory_samples = []
    notes = [(523.25, 0.10), (659.25, 0.10), (783.99, 0.10), (1046.50, 0.35)]
    for freq, dur in notes:
        for i in range(int(sample_rate * dur)):
            t = i / sample_rate
            val = 0.35 if (math.sin(2 * math.pi * freq * t) > 0) else -0.35
            decay = 1.0 - (t / dur) * 0.3
            victory_samples.append(val * decay)
    generate_wave("victory.wav", victory_samples, sample_rate)

    # 6. Faint / Defeat Sound
    faint_samples = []
    f_notes = [(440.0, 0.12), (370.0, 0.12), (311.1, 0.12), (220.0, 0.30)]
    for freq, dur in f_notes:
        for i in range(int(sample_rate * dur)):
            t = i / sample_rate
            val = 0.35 if (math.sin(2 * math.pi * freq * t) > 0) else -0.35
            decay = 1.0 - (t / dur) * 0.4
            faint_samples.append(val * decay)
    generate_wave("faint.wav", faint_samples, sample_rate)

    # 7. Synthesize Background Battle Beat Track
    synthesize_battle_beat()


# Initialize on import
init_8bit_sound_library()


def play_sound(sound_name: str):
    """Plays an instantaneous sound effect."""
    if not SOUND_ENABLED:
        return

    wav_path = SOUNDS_DIR / f"{sound_name}.wav"
    if not wav_path.exists():
        return

    def _play_worker():
        try:
            if sys.platform == "darwin":
                subprocess.run(["afplay", str(wav_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif sys.platform.startswith("linux"):
                subprocess.run(["aplay", "-q", str(wav_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    threading.Thread(target=_play_worker, daemon=True).start()


def start_battle_music():
    """Starts the 8-bit background battle theme looping seamlessly in the background."""
    global _music_running, _music_thread
    if not SOUND_ENABLED or _music_running:
        return

    _music_running = True
    wav_path = SOUNDS_DIR / "battle_beat.wav"
    if not wav_path.exists():
        return

    def _loop_music():
        global _music_process, _music_running
        while _music_running:
            try:
                if sys.platform == "darwin":
                    _music_process = subprocess.Popen(["afplay", str(wav_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    _music_process.wait()
                elif sys.platform.startswith("linux"):
                    _music_process = subprocess.Popen(["aplay", "-q", str(wav_path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    _music_process.wait()
                else:
                    time.sleep(1.0)
            except Exception:
                break

    _music_thread = threading.Thread(target=_loop_music, daemon=True)
    _music_thread.start()


def stop_battle_music():
    """Stops the background battle music immediately."""
    global _music_running, _music_process
    _music_running = False
    if _music_process is not None:
        try:
            _music_process.terminate()
            _music_process = None
        except Exception:
            pass

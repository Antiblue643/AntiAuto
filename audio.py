#There are 4 wave channels with 5-bit volume (L, C1, C2, R), and a 1-bit beeper.
#The beeper can't play waves, instead it only plays 1-bit square
#Each wave channel can play noise (index -1) or a wave of up to 64 samples (0-31 values)
#Technically, I guess, with the right kind of programming, you could play 5-bit PCM audio on the wave channels.

from external import *
import os
import json

WAVE_FILE = 'resources/waves.json'
CHANNELS = 4
CHANNEL_MAP = {
    "L": 0,
    "C1": 1,
    "C2": 2,
    "R": 3
}
INV_CHANNEL_MAP = {v: k for k, v in CHANNEL_MAP.items()}
PAN_MAP = {
    "L": (1.0, 0.0),
    "C1": (0.707, 0.707),
    "C2": (0.707, 0.707),
    "R": (0.0, 1.0)
}
def apply_pan(arr, pan):
    """Apply stereo panning to a mono or stereo numpy array, with right channel inverted."""
    left, right = pan
    if arr.ndim == 1:
        # Mono to stereo, invert right channel
        stereo = np.zeros((arr.shape[0], 2), dtype=arr.dtype)
        stereo[:, 0] = arr * left
        stereo[:, 1] = arr * right * -1
        return stereo
    elif arr.ndim == 2 and arr.shape[1] == 2:
        # Stereo: scale and invert right
        stereo = np.zeros_like(arr)
        stereo[:, 0] = arr[:, 0] * left
        stereo[:, 1] = arr[:, 1] * right * -1
        return stereo
    return arr

class Audio:
    def __init__(self):
        pg.mixer.init(frequency=44100, size=-16, channels=2)
        self.channels = [pg.mixer.Channel(i) for i in range(CHANNELS)]
        self.beeper_channel = pg.mixer.Channel(CHANNELS)  # 5th channel for beeper
        self.waves = {}

    def load_waves(self):
        with open(WAVE_FILE, 'r') as f:
            self.waves = json.load(f)
        
    def note_to_freq(self, note):
        """Convert a musical note to its frequency in Hz."""
        if isinstance(note, str):
            notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            # Support for sharps and flats
            if note[1] in ['#', 'b']:
                base = note[:2]
                octave = int(note[2])
            else:
                base = note[0]
                octave = int(note[1])
            note_index = notes.index(base)
            frequency = 440.0 * (2 ** ((note_index - 9) / 12 + (octave - 4)))
            return frequency
        else:
            return note

    def beep(self, freq, duration):
        """
        Play a beep sound.
        Args:
            freq (str, float): The frequency of the beep sound.
            duration (float): The duration of the beep sound in seconds.
        """
        freq = self.note_to_freq(freq)
        # Generate 1-bit square wave for beeper (mono)
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = 0.5 * (1 + np.sign(np.sin(2 * np.pi * freq * t)))
        wave = (wave * 32767).astype(np.int16)
        sound = pg.mixer.Sound(buffer=wave.tobytes())
        self.beeper_channel.play(sound)

    def play_wave(self, channel, wave, note, volume=31, duration=0.5):
        '''
        Play a waveform on a specified channel with given volume.
        Args:
            channel (str, int): The channel to play the wave on ('L', 'C1', 'C2', 'R') or 0-3.
            wave (str, int, list): The waveform to play (wave name, index, or raw values (0-31, must be maximum 64 samples)).
            volume (int): The volume level (0-31).
        '''
        pass

    def instrument(self, channel, instruments, arpeggio, volumes, tick_duration=0.5):
        """
        Play a sequence of offset notes (arpeggio), instruments, and volumes on a specified channel.
        Args:
            channel (str, int): The channel to play the sequence on ('L', 'C1', 'C2', 'R') or 0-3.
            instruments (list): List of waveforms (wave name, index, or raw values (0-31, must be maximum 64 samples)).
            arpeggio (list): List of note off (int).
            volumes (list): List of volume levels (0-31).
            tick_duration (float): Duration of each tick (how long the pointer takes to go to the next index in the lists) in seconds.
        """
        pass

    def panic(self):
        """
        Stop all audio playback.
        """
        for channel in self.channels:
            channel.stop()
        self.beeper_channel.stop()

    def rest(self, seconds):
        """
        Acts as a rest (pause) in the music. Needs a rework.
        """
        ms = int(seconds * 1000)
        pg.time.delay(ms) #Still appears to pause rendering... idk
#file length for each sample is approximately 100 ntsc frames,
#release point is 48 ntsc frames

#original export has 150 bpm (60hz)
#pattern length is 32, release point is at row 16, stop effect is at row 32.
#each sample (00-28.wav) in resources/samples/ is playing at C-4, 16-bit integer at 44100 hz

#There are 4 channels (L, C1, C2, R), and a beeper.
#The beeper can't play samples, instead it only plays 1-bit square
#it has 5-bit volume

from external import *
import os
import pygame.sndarray

SAMPLES_PATH = os.path.join("resources", "samples")
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
def play_sample_with_release(arr, release_frame, frame_rate, duration_sec):
    """
    Play arr[0:release_frame] (sustain), jump to arr[release_frame:] (release) at duration_sec.
    If duration_sec is longer than the release point, just play the sample out.
    """
    release_sample = int(release_frame * frame_rate / 60)
    total_len = arr.shape[0]
    needed = int(duration_sec * frame_rate)

    # If duration is longer than or equal to the release point, play the sample as-is
    if needed >= release_sample:
        return arr

    # Otherwise, play sustain up to duration, then jump to release section
    if arr.ndim == 2:
        sustain = arr[:needed, :]
        release = arr[release_sample:, :]
    else:
        sustain = arr[:needed]
        release = arr[release_sample:]
    out = np.concatenate([sustain, release], axis=0)
    # Truncate to original sample length if needed
    if out.shape[0] > total_len:
        out = out[:total_len]
    return out

def pitch_shift(sound, semitones):
    """Return a new pygame Sound object, pitch-shifted by the given number of semitones."""
    arr = pygame.sndarray.array(sound)
    rate = 2 ** (semitones / 12)
    # Handle mono and stereo
    if arr.ndim == 1:
        indices = np.round(np.arange(0, len(arr), rate)).astype(int)
        indices = indices[indices < len(arr)]
        arr_shifted = arr[indices]
    else:
        indices = np.round(np.arange(0, arr.shape[0], rate)).astype(int)
        indices = indices[indices < arr.shape[0]]
        arr_shifted = arr[indices, :]
    return pg.mixer.Sound(buffer=arr_shifted.astype(np.int16).tobytes())

class Audio:
    def __init__(self):
        pg.mixer.init(frequency=44100, size=-16, channels=2)
        self.channels = [pg.mixer.Channel(i) for i in range(CHANNELS)]
        self.samples = self.load_samples()
        self.beeper_channel = pg.mixer.Channel(CHANNELS)  # 5th channel for beeper

    def load_samples(self):
        samples = []
        for i in range(29):  # 00-28.wav
            filename = os.path.join(SAMPLES_PATH, f"{i:02}.wav")
            if os.path.exists(filename):
                samples.append(pg.mixer.Sound(filename))
            else:
                samples.append(None)
        return samples

    def note_to_freq(self, note):
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
        freq = self.note_to_freq(freq)
        # Generate 1-bit square wave for beeper (mono)
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = 0.5 * (1 + np.sign(np.sin(2 * np.pi * freq * t)))
        wave = (wave * 32767).astype(np.int16)
        sound = pg.mixer.Sound(buffer=wave.tobytes())
        self.beeper_channel.play(sound)

    def set_channel(self, channel, sample, note):
        if isinstance(channel, int):
            channel = INV_CHANNEL_MAP.get(channel, "C1")
        pan = PAN_MAP.get(channel, (0.5, 0.5))
        channel_idx = CHANNEL_MAP.get(channel, 0)
        if 0 <= channel_idx < CHANNELS and 0 <= sample < len(self.samples):
            snd = self.samples[sample]
            if snd:
                base_note = "C4"
                base_freq = self.note_to_freq(base_note)
                target_freq = self.note_to_freq(note)
                semitones = 12 * np.log2(target_freq / base_freq)
                arr = pygame.sndarray.array(snd)
                arr = pitch_shift(snd, semitones)
                arr = pygame.sndarray.array(arr)
                arr = apply_pan(arr, pan)
                snd_shifted = pg.mixer.Sound(buffer=arr.tobytes())
                self.channels[channel_idx].play(snd_shifted)
            else:
                print(f"Sample {sample} not found.")

    def play_note(self, channel, sample, note, volume, duration):
        if isinstance(channel, int):
            channel = INV_CHANNEL_MAP.get(channel, "C1")
        pan = PAN_MAP.get(channel, (0.5, 0.5))
        channel_idx = CHANNEL_MAP.get(channel, 0)
        if 0 <= channel_idx < CHANNELS and 0 <= sample < len(self.samples):
            snd = self.samples[sample]
            if snd:
                base_note = "C4"
                base_freq = self.note_to_freq(base_note)
                target_freq = self.note_to_freq(note)
                semitones = 12 * np.log2(target_freq / base_freq)
                arr = pygame.sndarray.array(snd)
                arr = pitch_shift(snd, semitones)
                arr = pygame.sndarray.array(arr)
                arr = apply_pan(arr, pan)
                arr = play_sample_with_release(
                    arr,
                    release_frame=48,        # 48 NTSC frames
                    frame_rate=44100,
                    duration_sec=duration
                )
                snd_shifted = pg.mixer.Sound(buffer=arr.astype(np.int16).tobytes())
                vol = max(0, min(volume, 31)) / 31.0
                snd_shifted.set_volume(vol)
                self.channels[channel_idx].play(snd_shifted)
            else:
                print(f"Sample {sample} not found.")

    def panic(self):
        for channel in self.channels:
            channel.stop()
        self.beeper_channel.stop()

    def rest(self, seconds):
        ms = int(seconds * 1000)
        pg.time.delay(ms) #Still appears to pause rendering... idk
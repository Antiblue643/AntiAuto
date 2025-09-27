#The AntiAuto's "Afterbuner" audio hardware has 4 wave channels with 5-bit volume (L, C1, C2, R), and a 1-bit beeper.
#The beeper can't play waves, instead it only plays 1-bit squares.
#Each wave channel can play noise (index -1) or a wave of up to 64 values. (0-31)
#Technically, I guess, with the right kind of programming, you could play 5-bit PCM audio on the wave channels.

from external import * #numpy, pygame, json
import time, re

if __name__ == "__main__":
    print("\nwrong file opened brochacho, it's main.py\n")

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
        self.load_waves()
        self.tuning = 440.0
        self.sequences = [None] * CHANNELS
        self.sequence_idxs = [0] * CHANNELS
        self.sequence_loops = [False] * CHANNELS
        self.sequence_next_time = [0] * CHANNELS
        self.sequence_active = [False] * CHANNELS

    def load_waves(self):
        with open(WAVE_FILE, 'r') as f:
            self.waves = json.load(f)
        
    def note_to_freq(self, note: str):
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
            frequency = self.tuning * (2 ** ((note_index - 9) / 12 + (octave - 4)))
            return frequency
        else:
            return note

    def beep(self, freq: str | float, duration: float):
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

    def _generate_wave_audio(self, wave_data, freq, volume, duration):
        """Generate audio from wave data at specified frequency and volume."""
        sample_rate = 44100
        total_samples = int(sample_rate * duration)

        # If wave_data is a special marker for noise, generate white noise for the whole duration
        if wave_data == "__NOISE__":
            period = max(1, int(sample_rate / (freq * 12))) # freq * 10 since C4 is kinda low for this
            noise = np.empty(total_samples)
            current = np.random.uniform(-1, 1)
            for i in range(total_samples):
                if i % period == 0:  # every 'period' samples, pick a new value
                    current = np.random.uniform(-1, 1)
                noise[i] = current

            audio_data = (noise * (volume / 31.0) * 32767).astype(np.int16)
            return audio_data

        samples_per_cycle = len(wave_data)
        cycles_per_second = freq
        samples_per_wave_cycle = sample_rate / cycles_per_second
        
        # Calculate how many times to repeat the wave pattern
        total_samples = int(sample_rate * duration)
        wave_cycles_needed = total_samples / samples_per_wave_cycle
        
        # Create the full wave by repeating
        audio_data = []
        for i in range(total_samples):
            # Calculate position in wave cycle
            cycle_pos = (i / samples_per_wave_cycle) % 1
            sample_pos = cycle_pos * samples_per_cycle
            
            # Linear interpolation between wave samples
            idx = int(sample_pos)
            # No interpolation: just use the nearest sample
            audio_val = int((wave_data[idx % samples_per_cycle] / 31.0) * volume / 31.0 * 32767)
            audio_data.append(audio_val)
        
        return np.array(audio_data, dtype=np.int16)

    def _get_wave_data(self, wave):
        """Get wave data from various input formats."""
        if isinstance(wave, str):
            # Wave name from JSON
            if wave in self.waves:
                return self.waves[wave]
            else:
                raise ValueError(f"Wave '{wave}' not found in wave file")
        elif isinstance(wave, int):
            if wave == -1:
                # Special marker for noise
                return "__NOISE__"
            elif 0 <= wave < len(list(self.waves.keys())):
                # Wave index
                wave_name = list(self.waves.keys())[wave]
                return self.waves[wave_name]
            else:
                raise ValueError(f"Wave index {wave} out of range")
        elif isinstance(wave, list):
            # Raw wave data
            if len(wave) > 64:
                raise ValueError("Wave data cannot exceed 64 samples")
            if not all(0 <= val <= 31 for val in wave):
                raise ValueError("Wave values must be between 0-31")
            return wave
        else:
            raise ValueError("Wave must be a string (name), int (index), or list (raw data)")

    def play_wave(self, channel: str | int, wave: str | int | list, note: str | float, volume: int = 31, duration: float = 0.5):
        '''
        Play a waveform on a specified channel with given volume.
        Args:
            channel (str, int): The channel to play the wave on ('L', 'C1', 'C2', 'R') or 0-3.
            wave (str, int, list): The waveform to play (wave name, index, or raw values (0-31, must be maximum 64 samples)).
            note (str, float): The note or frequency to play.
            volume (int): The volume level (0-31).
            duration (float): The length that the wave plays for.
        '''
        # Convert channel to index
        if isinstance(channel, str):
            if channel not in CHANNEL_MAP:
                raise ValueError(f"Invalid channel name: {channel}")
            ch_idx = CHANNEL_MAP[channel]
        else:
            if not 0 <= channel < CHANNELS:
                raise ValueError(f"Channel index {channel} out of range (0-{CHANNELS-1})")
            ch_idx = channel
        
        # Clamp volume to 5-bit range
        volume = max(0, min(31, volume))
        
        # Get frequency
        freq = self.note_to_freq(note)
        
        # Get wave data
        wave_data = self._get_wave_data(wave)
        
        # Generate audio
        audio = self._generate_wave_audio(wave_data, freq, volume, duration)
        
        # Apply channel panning
        ch_name = INV_CHANNEL_MAP[ch_idx]
        pan = PAN_MAP[ch_name]
        stereo_audio = apply_pan(audio, pan)
        
        # Convert to bytes and play
        sound = pg.mixer.Sound(buffer=stereo_audio.tobytes())
        self.channels[ch_idx].play(sound)

    def sequence(self, channel: str | int, data: dict, tempo_data: tuple, loop: bool = False):
        """
        Initiate a non blocking sequence of notes, volumes, and waves, aka background music!
        Args:
            channel (str, int): What channel to play on.
            data (dict): The music data (notes, wave, volume, note length)
                For example: 
                {
                    "notes": ["C4", "E4", "A4"], #can be names or raw frequencies.
                    "waves": [0, 0, 0], #still can be names, indices, or raw values.
                    "volumes": [31, 31, 31],
                    "notels": [0.25, 0.25, 0.25] # 1 = full note, 0.25 = quarter note, etc..
                }
                The keys must be those exact names.
            tempo_data (tuple): Base tempo, groove/speed (list), and divider (use 1 for no division). For example:
                (150, [6], 2) #75 bpm, no groove.
            loop (bool): To loop or not.
        """
        # Convert channel to index
        if isinstance(channel, str):
            if channel not in CHANNEL_MAP:
                raise ValueError(f"Invalid channel name: {channel}")
            ch_idx = CHANNEL_MAP[channel]
        else:
            if not 0 <= channel < CHANNELS:
                raise ValueError(f"Channel index {channel} out of range (0-{CHANNELS-1})")
            ch_idx = channel
        
        # Validate data format
        required_keys = ["notes", "waves", "volumes", "notels"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        
        # Check that all arrays have the same length
        lengths = [len(data[key]) for key in required_keys]
        if not all(length == lengths[0] for length in lengths):
            raise ValueError("All sequence arrays must have the same length")
        
        # Store sequence data
        self.sequences[ch_idx] = {
            'data': data,
            'tempo_data': tempo_data,
            'base_tempo': tempo_data[0],
            'groove': tempo_data[1] if len(tempo_data) > 1 else [1],
            'divider': tempo_data[2] if len(tempo_data) > 2 else 1
        }
        self.sequence_idxs[ch_idx] = 0
        self.sequence_loops[ch_idx] = loop
        self.sequence_next_time[ch_idx] = time.time()
        self.sequence_active[ch_idx] = True

    def sequence_update(self, channels: list):
        """
        Used to advance sequences. Call this regularly from your main loop!
        Args:
            channels (list): What channel(s) to update.    
        """
        current_time = time.time()
        
        for ch in channels:
            if isinstance(ch, str):
                if ch not in CHANNEL_MAP:
                    continue
                ch_idx = CHANNEL_MAP[ch]
            else:
                if not 0 <= ch < CHANNELS:
                    continue
                ch_idx = ch
            
            # Skip if no active sequence
            if not self.sequence_active[ch_idx] or self.sequences[ch_idx] is None:
                continue
            
            # Check if it's time to play the next note
            if current_time >= self.sequence_next_time[ch_idx]:
                seq = self.sequences[ch_idx]
                data = seq['data']
                idx = self.sequence_idxs[ch_idx]
                
                # Check if sequence is complete
                if idx >= len(data['notes']):
                    if self.sequence_loops[ch_idx]:
                        self.sequence_idxs[ch_idx] = 0
                        idx = 0
                    else:
                        self.sequence_active[ch_idx] = False
                        self.sequences[ch_idx] = None
                        continue
                
                # Get current note data
                note = data['notes'][idx]
                wave = data['waves'][idx]
                volume = data['volumes'][idx]
                note_length = data['notels'][idx]
                
                # Calculate timing
                base_tempo = seq['base_tempo']
                groove = seq['groove']
                divider = seq['divider']
                
                # Apply groove (cycle through groove pattern)
                groove_idx = idx % len(groove)
                groove_multiplier = groove[groove_idx] / 6.0  # Normalize groove values
                
                # Calculate actual tempo
                actual_tempo = (base_tempo / divider) * groove_multiplier
                
                # Calculate duration (60 seconds per minute, 4 quarter notes per whole note)
                duration = (60.0 / actual_tempo) * note_length * 4
                
                # Play the note
                try:
                    self.play_wave(ch_idx, wave, note, volume, duration)
                except Exception as e:
                    print(f"Error playing sequence note: {e}")
                    self.sequence_active[ch_idx] = False
                    self.sequences[ch_idx] = None
                    continue
                
                # Schedule next note
                self.sequence_idxs[ch_idx] += 1
                self.sequence_next_time[ch_idx] = current_time + duration * 0.9

    def stop_sequence(self, channel: str | int):
        """Stop a sequence on a specific channel."""
        if isinstance(channel, str):
            if channel not in CHANNEL_MAP:
                return
            ch_idx = CHANNEL_MAP[channel]
        else:
            if not 0 <= channel < CHANNELS:
                return
            ch_idx = channel
        
        self.sequence_active[ch_idx] = False
        self.sequences[ch_idx] = None
        self.sequence_idxs[ch_idx] = 0
        self.channels[ch_idx].stop()

    def stop_all_sequences(self):
        """Stop all active sequences."""
        for i in range(CHANNELS):
            self.stop_sequence(i)

    def play_aam(self, path: str):
        """
        Play an AAM music file containing sequences for all channels.
        """
        with open(path, 'r') as f:
            raw = f.read().strip()
        # Split header and JSON
        header, json_data = raw.split('\n', 1)
        match = re.match(r'^aam_(\d+)_(\d+)$', header)
        if not match:
            raise ValueError("Invalid AAM header format")
        channels = int(match.group(1))
        base_tempo = int(match.group(2))
        music = json.loads(json_data)

        if 'channels' not in music or len(music['channels']) != channels:
            raise ValueError("Channel count mismatch")

        for i, chdata in enumerate(music['channels']):
            groove = chdata.get('groove', [6])
            divider = chdata.get('divider', 1)
            loop = chdata.get('loop', False)
            tempo_data = (base_tempo, groove, divider)
            self.sequence(i, chdata, tempo_data, loop)

    def stop_aam(self):
        """Stop all sequences and clear scheduled beeper events."""
        self.stop_all_sequences()

    def update_all_sequences(self):
        """Call from main loop: update wave sequences and dispatch scheduled beeps."""
        self.sequence_update([0, 1, 2, 3])

# uses t for the wave variable.

# code from programs can use variables (a-z, except t) to dynamically change the expression.

import pygame as pg
import array
import numpy as np
import threading

np.seterr(divide='ignore', invalid='ignore')

class Bytebeat:
    def __init__(self, sample_rate=8000):
        self.sample_rate = sample_rate
        self._bytebeat_thread = None
        self._stop_event = threading.Event()
        self._current_sound = None
        self._bytebeat_expression = None
        self._lock = threading.Lock()
        pg.mixer.init(frequency=sample_rate)
    
    def set_sample_rate(self, sample_rate):
        if pg.mixer.get_init() and pg.mixer.get_init()[0] != sample_rate:
            pg.mixer.quit()
            pg.mixer.init(frequency=sample_rate)
        self.sample_rate = sample_rate

    
    def _play_bytebeat(self, sample_rate):
        chunk_duration = 1  # seconds
        chunk_samples = int(sample_rate * chunk_duration)
        t_offset = 0
        while not self._stop_event.is_set():
            with self._lock:
                expr = self._bytebeat_expression.replace("/", "//")
            t = np.arange(t_offset, t_offset + chunk_samples, dtype=np.int32)
            wave = eval(expr, {"t": t, "np": np}).astype(np.int32)
            wave = wave & 255
            wave = wave.astype(np.uint8)
            wave = (wave.astype(np.int16) - 128) * 256
            wave = np.column_stack((wave, wave))
            sound = pg.sndarray.make_sound(wave)
            self._current_sound = sound
            sound.play()
            pg.time.delay(int(chunk_duration * 1000))
            sound.stop()
            t_offset += chunk_samples

    def start_bytebeat(self, expression, sample_rate=None):
        if sample_rate is None:
            sample_rate = self.sample_rate
        else:
            self.set_sample_rate(sample_rate)
        self.stop_bytebeat()
        with self._lock:
            self._bytebeat_expression = expression
        self._stop_event.clear()
        self._bytebeat_thread = threading.Thread(target=self._play_bytebeat, args=(sample_rate,), daemon=True)
        self._bytebeat_thread.start()

    def update_bytebeat(self, expression):
        with self._lock:
            self._bytebeat_expression = expression

    def stop_bytebeat(self):
        self._stop_event.set()
        if self._current_sound:
            self._current_sound.stop()
        if self._bytebeat_thread:
            self._bytebeat_thread.join(timeout=0.1)
        self._bytebeat_thread = None
        self._current_sound = None
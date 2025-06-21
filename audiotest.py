from audio import Audio as a
import time

audio = a()


notes = ["E2", "A2", "E3", "C4", "A3", "E2", "A2", "E3", "C4", "A3", "E2", "A2", "E3", "C4", "A3", "E3"]

test = int(input("Choose a test [1: Samples, 2: Beeper, 3: Polyphony]: "))

if test not in [1, 2, 3]:
    test = 1

if test == 1:
    channel = str(input("Choose channel (L, C1, C2, R): ")).upper()

    if channel not in ["L", "C1", "C2", "R"]:
        print("Bad channel, defaulting to C1")
        channel = "C1"

    print(f"Playing samples in {channel}.")

    for sample in range(29):
        if sample not in range(0x11, 0x17):
            print(f"Sample {sample:02d}")
            for note in notes:
                audio.play_note(channel, sample, note, 31, 0.1)
                time.sleep(0.25)
            time.sleep(1)
        else:
            print(f"Skipped percussion (sample {sample}).")
elif test == 2:
    for note in notes:
        audio.beep(note, 0.1)
        time.sleep(0.25)
elif test == 3:
    chan1 = ["E2", 0, "E3", 0, "A3", 0, "A2", 0, "C4", 0, "E2", 0, "E3", 0, "A3"]
    chan2 = [0, "A2", 0, "C4", 0, "E2", 0, "E3", 0, "A3", 0, "A2", 0, "C4", 0, "E3"]

    for n1, n2 in zip(chan1, chan2):
        if n1:
            audio.play_note("L", 0x18, n1, 31, 0.25)
        if n2:
            audio.play_note("R", 0x18, n2, 31, 0.25)
        time.sleep(0.25)
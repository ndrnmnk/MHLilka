import machine

# Standard note-to-frequency mapping (in Hz).
NOTE_FREQUENCIES = {
    'F5': 2988, 'F4': 1766, 'G#3': 1269, 'D3': 1056, 'G#4': 1997,
    'D5': 2599, 'D4': 1570, 'G3': 1231, 'A3': 1315, 'G#5': 3450,
    'B5': 4000, 'A#5': 3807, 'G4': 1917, 'A#3': 1360, 'A#4': 2176,
    'D#3': 1087, 'B4': 2270, 'B3': 1406, 'G5': 3285, 'E3': 1119,
    'D#4': 1633, 'D#5': 2722, 'E4': 1696, 'C#4': 1514, 'E5': 2851,
    'C4': 1458, 'C5': 2375, 'C#5': 2484, 'C#3': 1028, 'F3': 1154,
    'F#3': 1192, 'F#4': 1836, 'C3': 1000, 'F#5': 3131, 'A5': 3625,
    'A4': 2085
}

def note_to_frequency(note):
    """
    Convert a note (string) to its frequency (in Hz).
    Returns 0 if the note is not found.
    """
    return NOTE_FREQUENCIES.get(note.upper(), 0)

def process_notes(notes):
    """
    Given a beeper-style notes argument, which can be a tuple of note strings or nested tuples
    (for chords), convert it into a list of frequencies.
    
    For chords (tuples of multiple notes), the function computes the average frequency.
    """
    frequencies = []
    
    # Ensure notes is iterable.
    if not isinstance(notes, (list, tuple)):
        notes = [notes]
    
    for item in notes:
        if isinstance(item, (list, tuple)):
            # Process chord: compute the average mapped frequency.
            chord_freqs = [note_to_frequency(n) for n in item if isinstance(n, str)]
            if chord_freqs:
                avg_freq = sum(chord_freqs) // len(chord_freqs)
                frequencies.append(avg_freq)
            else:
                frequencies.append(0)
        elif isinstance(item, str):
            frequencies.append(note_to_frequency(item))
        else:
            frequencies.append(0)
    return frequencies


class Beeper:
    """A class for playing simple UI beeps via a PWM buzzer on a fixed pin using a Timer."""

    def __init__(self):
        self.timer = None
        self.freq_list = []  # List of note frequencies to play
        self.note_index = 0  # Index for the current note

    def _timer_callback(self, t):
        # This callback runs every self.note_time_ms milliseconds
        if self.note_index < len(self.freq_list):
            freq = self.freq_list[self.note_index]
            self.buzzer.freq(freq)
            self.note_index += 1
        else:
            # All notes played: stop the timer and deinitialize the buzzer.
            self.buzzer.deinit()
            t.deinit()  # Stop the timer
            

    def play(self, notes, time_ms=120, volume=5):
        """
        Play the given note(s) using the PWM buzzer without blocking.
        
        'notes' can be a single note, a list/tuple of note strings, or nested lists/tuples (for chords).
        'time_ms' is the duration for each note/chord.
        'volume' is an integer (0-10) where 10 is the loudest.
        """
        # Process the notes into a list of frequencies.
        self.freq_list = process_notes(notes)
        self.note_time_ms = time_ms
        self.note_index = 0

        # Set the duty cycle based on volume (duty_u16 takes values from 0 to 65535).
        # Here, a volume of 10 corresponds to ~10% duty cycle.
        self.buzzer = machine.PWM(machine.Pin(11))
        self.buzzer.duty_u16(6553 * volume)
        self.buzzer.freq(self.freq_list[0])

        # Create and start a timer that fires every time_ms milliseconds.
        # Using id=-1 creates a virtual timer if supported.
        self.timer = machine.Timer(-1)
        self.timer.init(period=time_ms, mode=machine.Timer.PERIODIC, callback=self._timer_callback)


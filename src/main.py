#!/usr/bin/env python
"""
Seanstrument: random music generation

This main.py script either randomly rempas MIDI notes in real time, or randomly generates MIDI messages, depending on the mode.

Call the code in the following way (ex. for music generation mode):

    ./main.py --midi-input False --input-port None --max-duration 3.2 --max-notes 11 --time-step 0.1

Inputs:
    --midi-input: Indicates if MIDI input is to be used
    --input-port: Port to be used for MIDI input
    --max-duration: Maximum duration of a note, in seconds
    --max-notes: Maximum number of notes that can be played simultaneously
    --time-step: Time step, in seconds

Outputs:
    Virtual MIDI output, exposed for use in Garageband, Logic, etc.


Author: Sean Reid
"""

from __future__ import print_function

import logging
import sys
import time
import random
import argparse

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
from rtmidi.midiutil import open_midiinput, open_midioutput

# Set up logging levels
log = logging.getLogger("seanstrument")
logging.basicConfig(level=logging.DEBUG)


# Assign arguments and flags
parser = argparse.ArgumentParser(
                    prog = "Seanstrument",
                    description = "Generate random midi output")

parser.add_argument("-i", "--midi-input", action="store_true", help="Indicates if MIDI input is to be used")
parser.add_argument("-p", "--input-port", default=None, type=int, help="Port to be used for MIDI input")
parser.add_argument("-d", "--max-duration", default=2, type=float, help="Maximum duration of a note, in seconds")
parser.add_argument("-n", "--max-notes", default=3, type=int, help="Maximum number of notes that can be played simultaneously")
parser.add_argument("-s", "--time-step", default=0.05, type=float, help="Time step, in seconds")
parser.add_argument("-r", "--note-range", default=[21, 108], nargs=2, type=int, help="Range of MIDI note values [provide an upper and lower bound, separated by spaces]")


# Class Seanstrument implements a virtual MIDI instrument, that can either remap the keys of an actual MIDI instrument randomly, or generate random music.
class Seanstrument(object):

    # Initialize midi parameters and midi input/outputs
    def __init__(self, args):
        self.midi_input = args.midi_input
        self.max_duration = args.max_duration
        self.max_notes = args.max_notes
        self.time_step = args.time_step
        self.note_range = args.note_range
        self.clock = time.time()
        self.notes = {}
        try:
            self.midi_out, _ = open_midioutput(use_virtual=True)
            # only create midi input object if midi in flag is set
            if args.midi_input:
                self.midi_in, _ = open_midiinput(args.input_port)
                self.midi_in.set_callback(self.input_callback)
        except (EOFError, KeyboardInterrupt):
            sys.exit()

    # Context manager
    def __enter__(self):
        return self

    # Wrap up midi objects when context is closed
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Turn off all midi notes
        for note in self.notes:
            msg = [NOTE_OFF, note, 0]
            self.midi_out.send_message(msg)
        # Wrap up MIDI objects
        self.midi_out.close_port()
        del self.midi_out
        if self.midi_input:
            self.midi_in.close_port()
            del self.midi_in

    # Main loop that remaps or generates music
    def run(self):
        try:
            if self.midi_input:
                while True:
                    time.sleep(1) # everything handled via callback
            else:
                for msg in self.rand_message():
                    self.midi_out.send_message(msg)
                    logging.info(f"[{self.now}] {msg}")
        # Only stop if CTRL-C is pressed
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt, halting.")

    # Generate random MIDI message, including NOTE_ON / NOTE_OFF events
    def rand_message(self):
        while True:
            self.now = time.time()
            note_offs = self.get_note_offs()
            for note in note_offs:
                msg = [NOTE_OFF, note, 0]
                yield msg
            note = self.generate_note()
            if note is None: # maximum notes are played, so pass this time
                continue
            time.sleep(self.time_step)
            self.notes[note] = {}
            self.notes[note]["velocity"] = random.randint(0, 127)
            self.notes[note]["duration"] = random.random() * self.max_duration
            self.notes[note]["start"] = self.now
            self.notes[note]["end"] = self.notes[note]["start"] + self.notes[note]["duration"]
            msg = [NOTE_ON, note, self.notes[note]["velocity"]]
            yield msg

    # Calculate NOTE_OFF events from durations
    def get_note_offs(self):
        note_offs = []
        for note in self.notes:
            if self.now >= self.notes[note]["end"]:
                note_offs.append(note)
        for note in note_offs:
            self.notes.pop(note)
        return note_offs

    # Recursively find a note that is not being held down. Since this is random, it may take a while
    def generate_note(self):
        if len(self.notes) >= self.max_notes:
            return None
        note = random.randint(*self.note_range)
        if note in self.notes:
            note = self.generate_note()
        return note

    # Remap notes in real time (for MIDI input mode)
    def input_callback(self, event, data=None):
        self.now = time.time()
        msg, deltatime = event
        status, note, velocity = msg
        if velocity > 0:
            self.notes[note] = random.randint(*self.note_range)
            msg = [status, self.notes[note], velocity]
        else:
            status, note, velocity = msg
            if note in self.notes:
                msg = [status, self.notes[note], velocity]
                self.notes.pop(note)
        logging.info(f"[{self.now}] {msg}")
        self.midi_out.send_message(msg)

# Main function
def main():
    args = parser.parse_args()
    with Seanstrument(args) as s:
        s.run()

# Called when code is run
if __name__ == "__main__":
    main()

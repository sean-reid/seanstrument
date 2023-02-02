#!/usr/bin/env python

from __future__ import print_function

import logging
import sys
import time
import random

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
from rtmidi.midiutil import open_midiinput, open_midioutput

MAX_DURATION_SECONDS = 2
MAX_NOTES = 3
TIME_STEP_SECONDS = 0.05

log = logging.getLogger('seanstrument')
logging.basicConfig(level=logging.DEBUG)

class Seanstrument:
    def __init__(self):
        self.clock = time.time()
        self.notes = {}
        try:
            self.midi_out, _ = open_midioutput(use_virtual=True)
        except (EOFError, KeyboardInterrupt):
            sys.exit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.midi_out.close_port()
        del self.midi_out

    def __call__(self):
        try:
            for msg in self.message():
                self.midi_out.send_message(msg)
                logging.info(f"[{self.now}] {msg}")
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt, halting.")

    def message(self):
        while True:
            self.now = time.time()
            note_offs = self.get_note_offs()
            for note in note_offs:
                msg = [NOTE_OFF, note, 0]
                yield msg
            note = self.generate_note()
            if note is None:
                continue
            time.sleep(TIME_STEP_SECONDS)
            self.notes[note] = {}
            self.notes[note]["velocity"] = random.randint(0, 127)
            self.notes[note]["duration"] = random.random() * MAX_DURATION_SECONDS
            self.notes[note]["start"] = self.now
            self.notes[note]["end"] = self.notes[note]["start"] + self.notes[note]["duration"]
            msg = [NOTE_ON, note, self.notes[note]["velocity"]]
            yield msg

    def get_note_offs(self):
        note_offs = []
        for note in self.notes:
            if self.now >= self.notes[note]["end"]:
                note_offs.append(note)
        for note in note_offs:
            self.notes.pop(note)
        return note_offs

    def generate_note(self):
        if len(self.notes) >= MAX_NOTES:
            return None
        note = random.randint(21, 108)
        if note in self.notes:
            note = self.generate_note()
        return note

def main():
    with Seanstrument() as s:
        s()

if __name__ == "__main__":
    main()

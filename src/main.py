#!/usr/bin/env python

from __future__ import print_function

import logging
import sys
import time
import random

from rtmidi.midiconstants import NOTE_ON, NOTE_OFF
from rtmidi.midiutil import open_midiinput, open_midioutput

log = logging.getLogger('seanstrument')
logging.basicConfig(level=logging.DEBUG)


class MidiInputHandler(object):
    def __init__(self, port, midiout):
        self.port = port
        self.midiout = midiout
        self._wallclock = time.time()
        self.notes = {}

    def __call__(self, event, data=None):
        message, deltatime = event
        status, note, velocity = message
        if velocity > 0:
            self.notes[note] = random.randint(21, 108)
            message = [status, self.notes[note], velocity]
        else:
            status, note, velocity = message
            if note in self.notes:
                message = [status, self.notes[note], velocity]
                self.notes.pop(note)
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        self.midiout.send_message(message)
        print(self.notes)


# Prompts user for MIDI input port, unless a valid port number or name
# is given as the first argument on the command line.
# API backend defaults to ALSA on Linux.
inport = sys.argv[1] if len(sys.argv) > 1 else None

try:
    midiin, inport_name = open_midiinput(inport)
    midiout, outport_name = open_midioutput(use_virtual=True)
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler.")
midiin.set_callback(MidiInputHandler(inport_name, midiout))

print("Entering main loop. Press Control-C to exit.")
try:
    # Just wait for keyboard interrupt,
    # everything else is handled via the input callback.
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    midiout.close_port()
    del midiin

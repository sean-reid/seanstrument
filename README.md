# Seanstrument
Remapping midi notes randomly, and in real time

## Setup Environment
Run this to activate your virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
```

Then install the dependancies:
```
pip install -r requirements.txt
```

## Setup MIDI
Plug in your MIDI instrument. The code will ask you to choose from a list of the instruments that it finds, unless you give it a MIDI port as an argument.

## Run code
Run the code with:
```
python src/main.py <portnum>
```

The port num is optional. If omitted, you get to choose the port. A virtual MIDI output is exposed that you can use in a DAW like Logic, Garageband, etc. The messages sent to this virtual output have the same velocity and timing as the inputs, but the note values are randomly remapped.

## No-input mode
If you want to generate random MIDI without any real-time control, run the following script:
```
python src/seanstrument.py
```

This script will create a virtual MIDI output and write random notes to it.

## Author
* Sean Reid

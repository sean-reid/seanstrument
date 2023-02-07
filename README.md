# Seanstrument
Remapping midi notes randomly, and in real time

<a href="https://www.buymeacoffee.com/seanreid" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>

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

## Run code (input mode)
Run the code with:
```
./src/main.py -i
```

The port num is optional. If omitted, you get to choose the port. A virtual MIDI output is exposed that you can use in a DAW like Logic, Garageband, etc. The messages sent to this virtual output have the same velocity and timing as the inputs, but the note values are randomly remapped.

## Run code (no-input mode)
If you want to generate random MIDI without any real-time control, run the following script:
```
./src/main.py
```

This script will create a virtual MIDI output and write random notes to it.

For details on the input args, run:
```
./src/main.py --help
```

## Author
* Sean Reid

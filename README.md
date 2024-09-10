
# Py Guitar Synthesizer

**py_guitar_synth** is a Python package for generating realistic guitar music from tab sheets by modeling the physical and musical characteristics of guitar strings and performance techniques. The project allows users to convert guitar tabs into audio, simulating strokes, note durations, transitions, and string properties.

## Features

- Convert guitar tab sheets into realistic audio signals.
- Model various string characteristics such as inharmonicity, decay rates, and vibrato.
- Apply impulse response convolution to simulate room acoustics.
- Add custom echo effects to audio output.
- Support for multiple instruments (guitar, violin, piano).
- Built-in JSON-based configuration for instruments.
- Easily extendable for new instruments and custom sounds.

[Check out the documentation here](/docs/index.rst)

## Installation

You can clone this repository and install the package locally:

```bash
git clone https://github.com/your-repo-url/py_guitar_synth.git
cd py_guitar_synth
pip install .
```

## Dependencies

- Python 3.6+
- `numpy`
- `soundfile`

Ensure all dependencies are installed by running:

```bash
pip install -r requirements.txt
```

## Usage

### Example 1: Generating a Guitar Signal

You can use the following example to generate a guitar signal from a predefined sheet and instrument:

```python
from py_guitar_synth import default_classical_guitar, law_bass_f_aini, generate_guitar_signal_from_sheet

# Generate the signal
signal = generate_guitar_signal_from_sheet(
    instrument=default_classical_guitar,
    sheet=law_bass_f_aini,
    pluck_position=0.7,
    sr=44100
)

# Play or save the signal using your favorite audio library
import sounddevice as sd
sd.play(signal, 44100)
sd.wait()
```

### Example 2: Custom Instrument and Echo

```python
from py_guitar_synth import default_violine, agua_marina, generate_guitar_signal_from_sheet

# Generate signal with echo and impulse response
signal = generate_guitar_signal_from_sheet(
    instrument=default_violine,
    sheet=agua_marina,
    apply_convolution=True,
    apply_echo=True,
    echo_delay=0.25,
    echo_decay=0.3
)

# Save the signal to a WAV file
import soundfile as sf
sf.write('output.wav', signal, 44100)
```

### Loading Custom Instruments and Tabs

```python
from py_guitar_synth.instrument_parser import load_instrument_from_json
from py_guitar_synth.tab_parser import parse_guitar_tab_from_file
from py_guitar_synth import generate_guitar_signal_from_sheet

# Load custom instrument from a JSON file
my_instrument = load_instrument_from_json("path/to/my_instrument.json")

# Parse a guitar tab from a file
my_sheet = parse_guitar_tab_from_file("path/to/my_tab.txt")

# Generate the signal
signal = generate_guitar_signal_from_sheet(
    instrument=my_instrument,
    sheet=my_sheet
)
```

## Command-Line Interface (CLI)

You can use the package from the command line with the guitar_synth command to generate a guitar signal.

```shell
guitar_synth --instrument path/to/instrument.json --sheet path/to/tab.txt --output output.wav
```

#### CLI Options:

- `--instrument` : Path to the JSON file defining the instrument's properties (e.g., guitar, violin).
- `--sheet` : Path to the guitar tab file or the name of a predefined sheet.
- `--output` : Path where the generated WAV file will be saved.
- `--convolve` : Whether to apply an impulse response (room simulation). Default is `True`.
- `--impulse-response` : Path to a custom impulse response WAV file for convolution.
- `--echo` : Whether to add an echo effect. Default is `True`.
- `--echo-delay` : Set the delay time for the echo (default: 0.2 seconds).
- `--echo-decay` : Set the decay factor for the echo (default: 0.2).
- `--pluck-position` : Set the pluck position on the string (default: 0.7).

Example usage:

```shell
guitar_synth --instrument py_guitar_synth/assets/classical_guitar.json --sheet py_guitar_synth/assets/law_bass.txt --output law_bass_output.wav
```


## Project Structure

```
py_guitar_synth/
├── assets/
│   ├── classical_guitar.json
│   ├── violine.json
│   ├── piano.json
│   ├── ir.wav
│   ├── agua_marina.txt
│   └── law_bass.txt
├── py_guitar_synth/
│   ├── instruments.py
│   ├── sheets.py
│   ├── signal_processing.py
│   └── types.py
└── tests/
```

## Development

To contribute to the project, clone the repository and install the dependencies for development:

```bash
git clone https://github.com/MustafaAlotbah/PyGuitarSynthesis.git
cd py_guitar_synth
pip install -r requirements.txt
```

Feel free to submit issues or pull requests to help improve the package!

## Author

- **Mustafa Alotbah**
  - Email: mustafa.alotbah@gmail.com

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
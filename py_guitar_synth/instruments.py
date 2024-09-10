"""
py_guitar_synth.instruments
===========================

Project Overview
----------------
    The `py_guitar_synth` project simulates realistic guitar performances by synthesizing audio from guitar tabs
    based on instrument characteristics, such as string properties, vibrato, and decay rates. This is achieved
    through defining instruments and applying acoustic models like impulse responses.

Script Purpose
--------------
    This script loads various instruments' physical and acoustic properties from JSON files, which are then used
    in the guitar synthesis process. It also loads an impulse response WAV file for convolution to emulate real
    room acoustics. Pre-defined instruments like `default_classical_guitar`, `default_violine`, and `default_piano`
    are available for use in music generation.

Author
------
    Mustafa Alotbah
    Email: mustafa.alotbah@gmail.com
"""
import importlib.resources as pkg_resources
from py_guitar_synth.instrument_parser import load_instrument_from_json, load_impulse_response

# Load the JSON file with the guitar's physical properties
with pkg_resources.path('py_guitar_synth.assets', 'classical_guitar.json') as f:
    default_classical_guitar = load_instrument_from_json(str(f))

# Load the JSON file with the violine's physical properties
with pkg_resources.path('py_guitar_synth.assets', 'violine.json') as f:
    default_violine = load_instrument_from_json(str(f))

# Load the JSON file with the piano's physical properties
with pkg_resources.path('py_guitar_synth.assets', 'piano.json') as f:
    default_piano = load_instrument_from_json(str(f))

# Load a WAV file (impulse response)
with pkg_resources.path('py_guitar_synth.assets', 'ir.wav') as wav_path:
    # Use the path in your audio processing code
    default_impulse_response = load_impulse_response(str(wav_path))

"""
py_guitar_synth
===============

Project Overview
----------------
    The `py_guitar_synth` project is designed to synthesize realistic guitar sounds by modeling the physical
    characteristics of guitar strings and musical performance techniques. It converts guitar tab sheets into
    audio by simulating note strokes, durations, transitions, and acoustic properties.

Script Purpose
--------------
    This `__init__.py` file serves as the main entry point for the `py_guitar_synth` package. It imports essential
    components including default instruments, pre-configured guitar sheets, core types, and signal processing
    functions, making them available at the package level for easy access.

Author
------
    Mustafa Alotbah
    Email: mustafa.alotbah@gmail.com
"""

from .instruments import default_classical_guitar, default_impulse_response, default_piano, default_violine
from .sheets import law_bass_f_aini, agua_marina
from .types import *
from .instrument_parser import load_impulse_response, load_instrument_from_json
from .signal_processing import generate_guitar_signal_from_sheet, to_guitar_sequence, convolve_with_impulse_response, \
    add_echo, normalize_audio
from .tab_parser import parse_guitar_tab_from_file
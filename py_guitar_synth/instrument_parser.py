"""
py_guitar_synth.instrument_parser
=================================

Project Overview
----------------
    The `py_guitar_synth` project focuses on creating realistic guitar synthesis by modeling the physical and
    acoustic properties of instruments, including their string characteristics and response to vibrato, transitions,
    and room acoustics.

Script Purpose
--------------
    This script provides utility functions for loading instrument data and impulse responses. The `load_instrument_from_json`
    function parses JSON files defining the physical properties of instruments, while `load_impulse_response` loads
    impulse response files for simulating the acoustic characteristics of different environments.

Author
------
    Mustafa Alotbah
    Email: mustafa.alotbah@gmail.com
"""
import re
import json
import numpy as np
import soundfile as sf
from py_guitar_synth.types import Instrument, String


def remove_json_comments(json_content: str) -> str:
    """
    Remove line comments (//) from a JSON content string to clean it for parsing.

    Parameters
    ----------
    json_content : str
        The raw JSON content as a string, potentially containing comments.

    Returns
    -------
    str
        The cleaned JSON content, with all comments removed.
    """
    # Use a regular expression to remove all instances of // comments
    pattern = r'//.*?$'
    return re.sub(pattern, '', json_content, flags=re.MULTILINE)


def load_instrument_from_json(file_path: str) -> Instrument:
    """
    Load and parse an instrument's physical properties from a JSON file, constructing an Instrument object.

    Parameters
    ----------
    file_path : str
        The path to the JSON file that contains the instrument's definition.

    Returns
    -------
    Instrument
        An `Instrument` object representing the physical characteristics and capabilities of the instrument,
        including string properties, support for transitions, and vibrato.

    Raises
    ------
    json.JSONDecodeError
        If the JSON file contains invalid syntax (e.g., malformed structure after comment removal).
    """
    with open(file_path, 'r') as file:
        raw_content = file.read()
        cleaned_content = remove_json_comments(raw_content)  # Remove comments
        data = json.loads(cleaned_content)  # Load JSON after removing comments

    strings = []
    for string_data in data["strings"]:
        string = String(
            base_frequency=string_data.get("base_frequency"),
            inharmonicity_coefficient=string_data.get("inharmonicity_coefficient"),
            vibrato_frequency=string_data.get("vibrato_frequency"),
            vibrato_amplitude=string_data.get("vibrato_amplitude"),
            attack_duration=string_data.get("attack_duration"),
            max_duration=string_data.get("max_duration"),
            dynamic_range_factor=string_data.get("dynamic_range_factor"),
            fast_decay_rate=string_data.get("fast_decay_rate"),
            fast_decay_weight=string_data.get("fast_decay_weight"),
            mid_decay_rate=string_data.get("mid_decay_rate"),
            mid_decay_weight=string_data.get("mid_decay_weight"),
            very_slow_decay_rate=string_data.get("very_slow_decay_rate"),
            very_slow_decay_weight=string_data.get("very_slow_decay_weight"),
            harmonics_weights=string_data.get("harmonics_weights", []),
        )
        strings.append(string)

    return Instrument(
        supports_transitions=data["supports_transitions"],
        supports_vibrato=data["supports_vibrato"],
        strings=strings
    )


def load_impulse_response(ir_file: str) -> np.ndarray:
    """
    Load an impulse response from a WAV file, representing the acoustic signature of a room or space,
    which will be used to impart spatial characteristics to the synthesized guitar tone.

    Parameters
    ----------
    ir_file : str
        The path to the impulse response WAV file, often recorded in various acoustically treated environments.

    Returns
    -------
    np.ndarray
        The impulse response array, a 1D or 2D NumPy array representing the room's acoustic fingerprint.
    """
    ir, _ = sf.read(ir_file)
    return ir

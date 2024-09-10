"""
py_guitar_synth.sheets
======================

Project Overview
----------------
    The `py_guitar_synth` project aims to generate realistic guitar music from tab sheets by modeling guitar string
    properties and performance techniques. The project translates written guitar tabs into audio through synthesis
    of strokes, note values, and effects.

Script Purpose
--------------
    This script is responsible for loading pre-defined guitar sheets (tabs) from text files stored in the assets
    directory. The guitar sheets are parsed into `GuitarSheet` objects using the `parse_guitar_tab_from_file` function,
    which will later be used to synthesize guitar music. It ensures that the sheets, such as 'law_bass' and 'agua_marina',
    are ready for further processing and playback.

Author
------
    Mustafa Alotbah
    Email: mustafa.alotbah@gmail.com
"""
import importlib.resources as resources
from py_guitar_synth.tab_parser import parse_guitar_tab_from_file

# Load the 'law_bass.txt' tab file
with resources.as_file(resources.files('py_guitar_synth.assets').joinpath('law_bass.txt')) as f:
    law_bass_f_aini = parse_guitar_tab_from_file(str(f))

# Load the 'agua_marina.txt' tab file
with resources.as_file(resources.files('py_guitar_synth.assets').joinpath('agua_marina.txt')) as f:
    agua_marina = parse_guitar_tab_from_file(str(f))

py_guitar_synth
===============

Welcome to the `py_guitar_synth` project documentation! This project focuses on synthesizing realistic guitar sounds based on guitar tab sheets, simulating the physical and musical characteristics of strings and performance techniques.

.. contents:: Table of Contents
   :depth: 3
   :local:

Project Overview
----------------

`py_guitar_synth` translates guitar tab notation into audio, allowing users to generate guitar sounds by defining the instrument's physical characteristics, plucking techniques, and processing effects like convolution and echo. The generated sound is synthesized by modeling string vibrations, transitions, and harmonic properties.

Installation
------------

To install the project, clone the repository and install the required dependencies:

.. code-block:: bash

   git clone https://github.com/yourusername/py_guitar_synth.git
   cd py_guitar_synth
   pip install -r requirements.txt

You can also install it as a package by running:

.. code-block:: bash

   pip install .

Tab Syntax
----------

The guitar tab sheets used in this project follow a specific syntax to define frets, notes, and other musical elements. Here’s a breakdown of the syntax:

Strings
-------

Each string is represented by a line with the corresponding string name:
- `e`: High E string
- `B`: B string
- `G`: G string
- `D`: D string
- `A`: A string
- `E`: Low E string

Example:

.. code-block:: bash

    e|-3---|
    B|-----|
    G|-----|
    D|-----|
    A|-----|
    E|-----|

This example shows that the third fret on the high `e` string is played.

Frets
-----

Numbers represent the frets, while letters `a` to `f` are used for frets 10-15:

.. code-block:: bash

    e|--a---3--|  # Fret 10 on high E, fret 3 next

Note Values
-----------

Symbols are used to represent note durations:
- `!`: Eighth note (`NoteValue.eighthNote`)
- `!!`: Sixteenth note (`NoteValue.sixteenthNote`)
- `+`: Half note (`NoteValue.halfNote`)
- `++`: Whole note (`NoteValue.wholeNote`)
- No symbol: Defaults to a quarter note (`NoteValue.quarterNote`)

Example:

.. code-block:: bash

    e|-3+---3!!--|  # Half note followed by a sixteenth note

Let Ring
--------

To indicate that a note should sustain beyond its nominal duration, the letter `r` is used:

.. code-block:: bash

    e|-3r--|

Chords and Simultaneous Notes
-----------------------------

Notes played simultaneously across different strings can be written in a vertical column:

.. code-block:: bash

    e|-3--|
    B|-0--|
    G|-0--|

This represents an E minor chord.

Example:

.. code-block:: bash

    e|-3!-3r--|   # Eighth note followed by let ring

Custom Instrument Creation
---------------------------

For advanced users seeking to define their own instruments, a custom JSON structure can be created, which captures the nuanced characteristics of the instrument’s
strings, vibrato, harmonic richness, and decay profiles.

The key parameters include:

- **`supports_transitions`**: Whether the instrument supports glissando and legato transitions, crucial for smooth melodic contouring.
- **`supports_vibrato`**: Defines the presence of vibrato, an essential feature for enhancing tonal expressivity through periodic modulation.

Strings
-------

Each string has the following parameters, enabling the user to model complex acoustic phenomena:

- **`base_frequency`**: The fundamental pitch (Hz) of the string. This directly affects the modal frequencies of the vibrating string.
- **`inharmonicity_coefficient`**: A value controlling the degree of inharmonicity—deviation from pure harmonic frequencies due to stiffness or non-linearity.
- **`vibrato_frequency`**: Frequency of the vibrato modulation, enhancing the periodic tonal fluctuation.
- **`vibrato_amplitude`**: The depth of the vibrato, determining the extent of pitch variation.
- **`attack_duration`**: How quickly the sound reaches its maximum amplitude, defined in milliseconds (ms). Shorter durations are characteristic of sharp attacks.
- **`max_duration`**: The maximum sustain of the note before decay, critical for long tones.
- **`dynamic_range_factor`**: Modulates the intensity of sound based on the plucking force, simulating the physical interaction of the player.
- **`decay_rates`**: Defines the multi-phase decay envelope of the note. Fast, mid, and slow decay rates determine the sound's evolution over time.
- **`harmonics_weights`**: Controls the amplitude of harmonics in the frequency spectrum, contributing to the timbral identity of the instrument.

Creating a custom instrument allows for the synthesis of any stringed instrument, modeled using these principles of acoustics and digital sound synthesis.


Modules
-------

Below are the key modules that make up the `py_guitar_synth` project.

.. toctree::
   :maxdepth: 2

   py_guitar_synth/instruments
   py_guitar_synth/sheets
   py_guitar_synth/tab_parser
   py_guitar_synth/signal_processing
   py_guitar_synth/types
   py_guitar_synth/instrument_parser

Usage
-----

Here is a simple usage example demonstrating how to synthesize a guitar sequence:

.. code-block:: python

   from py_guitar_synth import default_classical_guitar, law_bass_f_aini, generate_guitar_signal_from_sheet
   import sounddevice as sd

   # Generate the guitar signal from a sheet
   signal = generate_guitar_signal_from_sheet(
       instrument=default_classical_guitar,
       sheet=law_bass_f_aini
   )

   # Play the generated sound
   sd.play(signal, 44100)
   sd.wait()

You can customize the instrument, apply effects such as convolution with impulse responses, and even add echo to simulate room acoustics.

Contributing
------------

We welcome contributions! Feel free to submit pull requests, report issues, or suggest improvements. Please make sure to follow the contribution guidelines provided in the repository.

License
-------

This project is licensed under the MIT License.

Author
------

Mustafa Alotbah
Email: mustafa.alotbah@gmail.com
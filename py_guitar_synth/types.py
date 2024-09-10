"""
py_guitar_synth.types
=====================

Project Overview
----------------
    The `py_guitar_synth` project aims to generate realistic guitar music from tab sheets by modeling the physical and
    musical characteristics of guitar strings and performance techniques. The project translates written guitar tabs
    into audio by simulating strokes, note durations, transitions, and string properties.

Script Purpose
--------------
    This module defines the core types used across the project, such as note values, transitions, and guitar strokes.
    It provides data structures like `GuitarSheet`, `SequenceElement`, and `Instrument`, which form the foundation for
    parsing and synthesizing guitar performances.

Author
------
    Mustafa Alotbah
    Email: mustafa.alotbah@gmail.com
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class NoteValue(Enum):
    """
    Enumeration of rhythmic note values, quantifying the temporal length of musical notes in relative proportions.

    Attributes
    ----------
    DoubleNote : float
        Denotes a breve or double whole note (2.0000 beats).
    wholeNote : float
        Denotes a semibreve or whole note (1.0000 beats).
    halfNote : float
        Denotes a minim or half note (0.5000 beats).
    quarterNote : float
        Denotes a crotchet or quarter note (0.2500 beats).
    eighthNote : float
        Denotes a quaver or eighth note (0.1250 beats).
    sixteenthNote : float
        Denotes a semiquaver or sixteenth note (0.0625 beats).
    """
    DoubleNote = 2.0000
    wholeNote = 1.0000
    halfNote = 0.5000
    quarterNote = 0.2500
    eighthNote = 0.1250
    sixteenthNote = 0.0625


class TransitionType(Enum):
    """
    Enumeration of articulatory transitions between musical notes on the guitar, defining distinct legato and staccato techniques.

    Attributes
    ----------
    strike : int
        Represents an attack using direct striking or plucking of the string (0).
    hammerOrPull : int
        Denotes legato techniques, including hammer-ons or pull-offs (1).
    slide : int
        Represents continuous sliding between pitches (2).
    """
    strike = 0
    hammerOrPull = 1
    slide = 2


class PluckStyle(Enum):
    """
    Enumeration of tonal variations in plucking dynamics, influencing timbral intensity and articulation.
    TODO unused

    Attributes
    ----------
    hard : int
        Represents a fortissimo or hard plucking style (0).
    soft : int
        Represents a pianissimo or soft plucking style (1).
    """
    hard = 0
    soft = 1


class PlayStyle(Enum):
    """
    Enumeration of advanced playing techniques, modulating pitch, tone, and articulation through expressive means.
    TODO unused

    Attributes
    ----------
    steady_finger : int
        Represents a legato or continuous steady fingerpicking technique (0).
    vibrato : int
        Represents modulated pitch oscillation through vibrato technique (1).
    tremelo : int
        Represents rapid reiteration of a single pitch in tremolo style (2).
    """
    steady_finger = 0
    vibrato = 1
    tremelo = 2


@dataclass
class Stroke:
    """
    Data structure representing a guitar stroke, encompassing multiple notes
    with distinct rhythmic and articulatory characteristics.

    Attributes
    ----------
    string_number : int
        The index of the guitar string being struck, where 1 represents the lowest string (1 to 6).
    frets : List[int]
        A sequence of frets engaged during the stroke, defining the pitch of each note.
    values : List[NoteValue]
        Rhythmic durations corresponding to each note in the stroke.
    transition_types : Optional[List[TransitionType]], optional
        Articulatory transitions for each note, defaulting to None if no transition applies.
    letRing : bool
        Boolean flag indicating whether the notes should sustain (let ring) beyond their nominal value.
    """
    string_number: int  # 1..6
    frets: List[int]  # 0..16
    values: List[NoteValue]
    transition_types: Optional[List[TransitionType]] = None
    letRing: bool = False


@dataclass
class SequenceElement:
    """
    Represents a single sequence element in a guitar performance, aggregating strokes into a coherent musical phrase.

    Attributes
    ----------
    strokes : List[Stroke]
        A list of `Stroke` objects that form part of the sequence.
    """
    strokes: List[Stroke]


@dataclass
class GuitarSheet:
    """
    Data model representing a complete guitar tab sheet, including metadata and performance instructions.

    Attributes
    ----------
    title : str
        The title of the musical piece.
    author : str
        The composer or arranger of the sheet.
    sequence : List[SequenceElement]
        A chronological sequence of musical elements, represented as strokes.
    bpm : int
        The tempo of the performance in beats per minute (default 60 BPM).
    capo_fret : int
        The fret number where a capo is placed (default is 0, no capo).
    """
    title: str
    author: str
    sequence: List[SequenceElement]
    bpm: int = 60
    capo_fret: int = 0


@dataclass
class String:
    """
    Representation of a guitar string's physical and acoustic properties, encapsulating vibrato and
    decay characteristics essential to timbre production.

    Attributes
    ----------
    base_frequency : float
        The fundamental frequency of the string when played open.
    inharmonicity_coefficient : float
        Coefficient affecting the tuning deviation due to string stiffness and mass.
    vibrato_frequency : float
        The frequency at which the pitch modulation (vibrato) oscillates.
    vibrato_amplitude : float
        Amplitude of the vibrato effect, controlling the intensity of pitch variation.
    attack_duration : float
        The time for the sound to reach peak amplitude post-attack.
    max_duration : float
        The maximum sustain duration before the sound decays to silence.
    dynamic_range_factor : float
        A factor influencing the range between the softest and loudest sounds the string can produce.
    fast_decay_rate : float
        Rate at which the sound decays during the initial fast-decay phase.
    fast_decay_weight : float
        Contribution of the fast decay to the overall sound.
    mid_decay_rate : float
        Decay rate during the middle stage of the note.
    mid_decay_weight : float
        Contribution of the mid-decay phase to the overall timbre.
    very_slow_decay_rate : float
        The final decay rate during the very slow phase.
    very_slow_decay_weight : float
        Contribution of the very slow decay to the overall sustain.
    harmonics_weights : List[float]
        List of weights for harmonic partials, shaping the timbre of the string.
    """
    base_frequency: float
    inharmonicity_coefficient: float
    vibrato_frequency: float
    vibrato_amplitude: float
    attack_duration: float
    max_duration: float
    dynamic_range_factor: float
    fast_decay_rate: float
    fast_decay_weight: float
    mid_decay_rate: float
    mid_decay_weight: float
    very_slow_decay_rate: float
    very_slow_decay_weight: float
    harmonics_weights: list


@dataclass
class Instrument:
    """
    Class encapsulating the musical characteristics of an instrument, emphasizing vibrato and transition capabilities,
    designed for detailed performance modeling.

    Attributes
    ----------
    supports_transitions : bool
        Boolean indicating whether the instrument can execute techniques such as slides, hammer-ons, or pull-offs.
    supports_vibrato : bool
        Boolean indicating whether the instrument supports vibrato techniques for enhanced expressiveness.
    strings : List[String]
        List of `String` objects representing the strings of the instrument, each with detailed acoustic properties.
    """
    supports_transitions: bool
    supports_vibrato: bool
    strings: List[String]


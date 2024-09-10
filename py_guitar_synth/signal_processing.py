"""
py_guitar_synth.signal_processing
=================================

Project Overview
----------------
    The `py_guitar_synth` project focuses on synthesizing realistic guitar sounds from written tab sheets by modeling
    the physical and musical properties of guitar strings and various performance techniques. The project processes
    guitar strokes, note durations, transitions, and harmonic content, translating these into realistic audio signals.

Script Purpose
--------------
    This module handles the core signal processing operations, including the generation of guitar tones,
    convolution with impulse responses, adding effects like echo, and normalizing the final audio signal.
    The module integrates features like string harmonics, vibrato, pluck position, and customizable effects
    to create detailed and realistic guitar sounds from `GuitarSheet` objects.

Author
------
    Mustafa Alotbah
    Email: mustafa.alotbah@gmail.com
"""
import numpy as np
from typing import List, Optional
from py_guitar_synth.types import Stroke, SequenceElement, Instrument, String, GuitarSheet
from py_guitar_synth.instrument_parser import load_impulse_response
from py_guitar_synth.instruments import default_impulse_response


def add_echo(signal: np.ndarray, delay: float, decay: float, sr: int = 44100) -> np.ndarray:
    """
    Add an echo effect to the audio signal, mimicking the reflective delay of sound waves off surfaces in a room.
    This can simulate the natural acoustic reverberation or echo of larger spaces.

    Parameters
    ----------
    signal : np.ndarray
        The original audio signal, which can be either mono (1D) or stereo (2D).
    delay : float
        The delay time of the echo in seconds, representing the time interval before the reflected sound is heard.
    decay : float
        The decay factor, controlling how much quieter the echo is relative to the original sound.
    sr : int, optional
        The sample rate of the signal, default is 44100 Hz.

    Returns
    -------
    np.ndarray
        The audio signal with the echo effect applied, either in mono or stereo depending on the input.
    """
    delay_samples = int(delay * sr)  # Convert delay in seconds to samples

    if len(signal.shape) == 2:
        # Stereo signal: Apply echo separately to each channel
        left_channel = np.zeros(len(signal) + delay_samples)
        right_channel = np.zeros(len(signal) + delay_samples)

        # Add the original signal
        left_channel[:len(signal)] = signal[:, 0]
        right_channel[:len(signal)] = signal[:, 1]

        # Add the delayed and decayed echo
        left_channel[delay_samples:] += signal[:, 0] * decay
        right_channel[delay_samples:] += signal[:, 1] * decay

        return np.vstack((left_channel, right_channel)).T  # Combine left and right channels

    else:
        # Mono signal: Apply echo directly
        echo_signal = np.zeros(len(signal) + delay_samples)
        echo_signal[:len(signal)] = signal

        # Add the delayed and decayed echo
        echo_signal[delay_samples:] += signal * decay

        return echo_signal[:len(signal)]


def fftconvolve(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Perform frequency-domain convolution utilizing the Fast Fourier Transform (FFT) algorithm,
    optimal for large-scale convolutions in musical signal processing.

    Parameters
    ----------
    x : np.ndarray
        Input array representing the first signal or waveform in the time domain.
    y : np.ndarray
        Input array representing the second signal or impulse response to be convolved.

    Returns
    -------
    np.ndarray
        The resultant convolved signal, computed via the convolution theorem, using the product of Fourier transforms.
    """

    # Compute the size of the output
    n = len(x) + len(y) - 1

    # Perform the FFT on both signals with padding
    X = np.fft.fft(x, n=n)
    Y = np.fft.fft(y, n=n)

    # Convolution theorem: multiplication in the frequency domain corresponds to convolution.
    result_freq = X * Y

    # Inverse FFT returns the result to the time domain.
    result = np.fft.ifft(result_freq)

    # Convolution produces a real-valued result.
    return np.real(result)


def convolve_with_impulse_response(signal: np.ndarray, ir: np.ndarray) -> np.ndarray:
    """
    Convolve the synthesized guitar tone with an impulse response, effectively simulating how the tone
    would sound in a real acoustic environment. This process emulates the effect of room acoustics,
    providing depth and spatial characteristics to the audio.

    Parameters
    ----------
    signal : np.ndarray
        The synthesized guitar tone, typically a 1D array representing a monophonic audio signal.
    ir : np.ndarray
        The impulse response used for convolution, which can be mono (1D) or stereo (2D).

    Returns
    -------
    np.ndarray
        The convolved audio signal, with the characteristics of the acoustic space applied to it.
    """

    # Check if the impulse response is stereo (2D) or mono (1D)
    if len(ir.shape) == 2:
        # Stereo IR: Convolve separately for each channel (left and right)
        left_channel = fftconvolve(signal, ir[:, 0])[:len(signal)]
        right_channel = fftconvolve(signal, ir[:, 1])[:len(signal)]
        return np.vstack((left_channel, right_channel)).T  # Combine left and right channels
    else:
        # Mono IR: Apply convolution directly
        return fftconvolve(signal, ir)[:len(signal)]


def concatenate_add(array1: np.ndarray, array2: np.ndarray, shifted_by: int = 0) -> np.ndarray:
    """
    Concatenate two signals, merging them with a time offset, mimicking natural delays and overlapping tones.

    Parameters
    ----------
    array1 : np.ndarray
        The primary buffer holding the existing signal, typically from prior synthesis.
    array2 : np.ndarray
        The secondary signal representing a new note or sound event.
    shifted_by : int, optional
        The time shift (in samples) at which `array2` is added to `array1`. Default is 0 (no shift).

    Returns
    -------
    np.ndarray
        The merged array containing both signals with appropriate overlap and time shift.
    """

    # If the primary buffer is empty, simply return the new signal.
    if len(array1) == 0:
        return array2

    # Truncate `array1` at the overlap point to prevent interference.
    if len(array1) > shifted_by:
        array1 = array1[:shifted_by]

    # The new total length after merging.
    total_length = max(len(array1), shifted_by + len(array2))

    # Extend array1 to accommodate the new tone at the shifted position
    extended_array1 = np.pad(array1, (0, total_length - len(array1)))

    # Extend array2 to fit into array1 at the correct position
    extended_array2 = np.pad(array2, (shifted_by, total_length - shifted_by - len(array2)))

    return extended_array1 + extended_array2


def fret_to_frequency(string: String, fret: int) -> float:
    """
    Calculate the fundamental frequency of a note based on the string's open frequency and fret number,
    following the well-tempered tuning system of Western music.

    Parameters
    ----------
    string : String
        The guitar string object, encapsulating physical properties including the base or open string frequency.
    fret : int
        The fret number pressed, which alters the vibrating length and thus the frequency.

    Returns
    -------
    float
        The resultant frequency in Hertz (Hz), following the 12-tone equal temperament system.
    """

    # The standard formula for calculating frequency on fretted instruments.
    return string.base_frequency * (2 ** (fret / 12.0))


def modal_adjustment(harmonic: int, pluck_position: float) -> float:
    """
    Compute the adjustment factor for harmonic amplitudes based on plucking position and harmonic mode,
    accounting for the influence of standing wave nodes and antinodes.

    Parameters
    ----------
    harmonic : int
        The harmonic overtone number, representing which harmonic mode is being calculated.
    pluck_position : float
        The relative position on the string where the pluck occurs (normalized to [0, 1]).

    Returns
    -------
    float
        The adjustment factor applied to the harmonic amplitude, attenuating harmonics when plucked near a node.
    """

    # Positions of standing wave nodes.
    node_positions = [(harmonic - 1) / (2 * harmonic) for _ in range(harmonic)]

    for node in node_positions:
        # If plucking near a node, minimal harmonic vibration occurs.
        if abs(pluck_position - node) < 0.005:
            return 0

    # Default adjustment for harmonics if no node interference occurs.
    return 1.0


def attack_curve(t, attack_duration):
    """
    Generate an envelope for the attack phase of the sound, simulating the dynamics of plucking or bowing a string.

    Parameters
    ----------
    t : np.ndarray
        Time array for the signal.
    attack_duration : float
        The time duration for the attack phase; short values represent a sharp pluck,
        while longer values emulate bowing.

    Returns
    -------
    np.ndarray
        The calculated envelope curve for the attack phase.
    """

    # Sigmoid curve for smoother attack.
    sigmoid_curve = 1 / (1 + np.exp(-12 * (t / attack_duration - 1)))

    # Sinusoidal for faster attack.
    sinusoidal_curve = np.where(t < attack_duration, np.sin(np.pi * t / (2 * attack_duration)), 1.0)

    # Adjust blend based on attack duration.
    blend_factor = np.clip(attack_duration * 200, 0, 1)

    # Blending sigmoid and sinusoidal curves.
    return (1 - blend_factor) * sigmoid_curve + blend_factor * sinusoidal_curve


def release_curve(t: np.ndarray, string: String, max_duration: float) -> np.ndarray:
    """
    Compute the release or decay envelope of the note, incorporating the specific decay characteristics of the string.

    Parameters
    ----------
    t : np.ndarray
        Time array for the signal.
    string : String
        The guitar string object encapsulating fast, mid, and slow decay rates and weights.
    max_duration : float
        The maximum sustain duration of the note before silence.

    Returns
    -------
    np.ndarray
        The computed release envelope for the note's decay phase.
    """

    # Fast initial decay phase.
    fast_decay = np.exp(-string.fast_decay_rate * t)

    # Mid-level decay phase.
    mid_decay = np.exp(-string.mid_decay_rate * t)

    # Extended, slow decay.
    very_slow_decay = np.exp(-string.very_slow_decay_rate * t)

    # Weighted sum of all decay phases.
    combined_decay = (string.fast_decay_weight * fast_decay +
                      string.mid_decay_weight * mid_decay +
                      string.very_slow_decay_weight * very_slow_decay)

    # Mask to limit the release curve within the maximum duration.
    duration_mask = np.where(t < max_duration, 1, 0)

    return combined_decay * duration_mask


def calculate_vibrato(string: String, t: np.ndarray) -> np.ndarray:
    """
    Generate vibrato modulation by varying the frequency over time, adding expressive nuances to the tone.

    Parameters
    ----------
    string : String
        The guitar string object containing vibrato properties, such as frequency and amplitude.
    t : np.ndarray
        Time array over which the vibrato is applied.

    Returns
    -------
    np.ndarray
        Vibrato modulation array, oscillating between 1 and the vibrato amplitude.
    """

    # Sine wave vibrato modulation.
    return 1 + string.vibrato_amplitude * np.sin(2 * np.pi * string.vibrato_frequency * t)


def calculate_harmonics(
        base_frequency: float,
        string: String,
        vibrato: np.ndarray,
        pluck_position: float,
        decay_t0: float,
        t: np.ndarray
) -> np.ndarray:
    """
    Synthesize the harmonic components of a guitar tone, using the base frequency, string characteristics,
    vibrato modulation, and pluck position to generate a rich harmonic spectrum.

    Parameters
    ----------
    base_frequency : float
        The fundamental frequency of the note being synthesized.
    string : String
        The guitar string object containing harmonic weights and inharmonicity factors.
    vibrato : np.ndarray
        Vibrato modulation array affecting the frequency over time.
    pluck_position : float
        Position on the string where it was plucked, influencing harmonic amplitudes.
    decay_t0 : float
        Time offset for the decay phase.
    t : np.ndarray
        Time array over which the harmonics are synthesized.

    Returns
    -------
    np.ndarray
        The complete harmonic signal, formed by summing weighted harmonic components.
    """

    # Initialize tone as a zero array.
    signal_tone = np.zeros_like(t)

    for h in range(1, len(string.harmonics_weights) + 1):

        # Adjust for inharmonicity and vibrato.
        harmonic_freq = base_frequency * (h * (1 + string.inharmonicity_coefficient * h ** 2)) * vibrato

        # Decay applied based on harmonic order.
        decay = np.exp(-h / 6 * (t - decay_t0))

        # Harmonic amplitude influenced by pluck position.
        amplitude = string.harmonics_weights[h - 1] * np.sin(np.pi * pluck_position * h)

        # Apply modal adjustments.
        amplitude *= modal_adjustment(h, pluck_position)

        # Add harmonic component to the tone.
        signal_tone += amplitude * np.sin(2 * np.pi * harmonic_freq * t) * decay

    return signal_tone


def add_attack_and_release(
        signal_tone: np.ndarray,
        t: np.ndarray,
        decay_t0: float,
        string: String
) -> np.ndarray:
    """
    Apply both attack and release envelopes to the synthesized guitar tone, shaping its temporal evolution.

    Parameters
    ----------
    signal_tone : np.ndarray
        The synthesized tone signal without dynamic shaping.
    t : np.ndarray
        Time array for the signal.
    decay_t0 : float
        Time offset indicating when the decay phase starts.
    string : String
        The guitar string object containing attack and decay parameters.

    Returns
    -------
    np.ndarray
        The dynamically shaped signal with both attack and release curves applied.
    """

    # Apply the attack curve.
    signal_tone *= attack_curve(t - decay_t0, attack_duration=string.attack_duration)

    # Apply the release (decay) curve.
    signal_tone *= release_curve(t - decay_t0, string, max_duration=string.max_duration)

    return signal_tone


def add_white_noise(signal_tone, t, decay_t0):
    """
    Add a subtle layer of white noise to the synthesized tone,
    simulating the natural imperfections of real guitar sound.

    Parameters
    ----------
    signal_tone : np.ndarray
        The synthesized tone signal.
    t : np.ndarray
        Time array for the signal.
    decay_t0 : float
        Time offset for when the decay starts.

    Returns
    -------
    np.ndarray
        The tone with added white noise, modulated by an envelope for realism.
    """

    # Generate white noise.
    white_noise = np.random.randn(len(t))

    # Envelope to attenuate the white noise over time.
    noise_envelope = np.exp(-15 * (t - decay_t0))

    return signal_tone + 0.01 * white_noise * noise_envelope


def synthesize_tone(
        instrument: Instrument,
        string_number: int,
        fret: int,
        duration: float = 0.1,
        pluck_position: float = 0.7,
        decay_t0: float = 0.0,
        sr: int = 44100
) -> np.ndarray:
    """
    Synthesize a guitar tone for a specific string, fret, and duration,
    leveraging the physical properties of the string.

    Parameters
    ----------
    instrument : Instrument
        The instrument object containing string properties, such as inharmonicity and dynamic range.
    string_number : int
        The string number (1 to 6) representing the particular string of the guitar.
    fret : int
        The fret number pressed to determine the pitch of the note.
    duration : float, optional
        The duration of the tone in seconds, default is 0.1s, which simulates short plucks.
    pluck_position : float, optional
        The relative position along the string where the pluck occurs, influencing harmonic content.
        Default is 0.7 (near the bridge).
    decay_t0 : float, optional
        The time offset for the decay phase, simulating the fading sound of a note, default is 0.0.
    sr : int, optional
        The sample rate for the audio signal, default is 44100 Hz (CD quality).

    Returns
    -------
    np.ndarray
        The synthesized tone as a NumPy array, representing the full harmonic and temporal characteristics of the note.
    """

    # Time array, sampled at the given sample rate over the note duration
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)

    # Retrieve the specific string based on the string number, e.g., bass or treble strings
    string = instrument.strings[string_number - 1]

    # Calculate the base frequency for the given fret using standard equal temperament tuning
    base_frequency = fret_to_frequency(string, fret)

    # Modulate the frequency with vibrato if the instrument supports it, creating pitch oscillations
    vibrato = calculate_vibrato(string, t) if instrument.supports_vibrato else 1

    # Compute the harmonic structure of the note, considering string inharmonicity and plucking position
    signal_tone = calculate_harmonics(base_frequency, string, vibrato, pluck_position, decay_t0, t)

    # Apply attack and release (decay) envelopes to shape the dynamic contour of the sound
    signal_tone = add_attack_and_release(signal_tone, t, decay_t0 + 0.01, string)

    # Add very subtle white noise for realism
    signal_tone = add_white_noise(signal_tone, t, decay_t0)

    # Apply dynamic range factor
    signal_tone *= string.dynamic_range_factor

    return signal_tone


def normalize_audio(tones: np.ndarray) -> np.ndarray:
    """
    Normalize the audio signal to ensure the loudest peak is capped at 0.95 of full scale, preventing clipping.

    Parameters
    ----------
    tones : np.ndarray
        Array representing the audio waveform, typically containing multiple tones summed together.

    Returns
    -------
    np.ndarray
        The normalized audio signal, scaled such that the peak amplitude is 0.95.
    """
    return tones / np.max(np.abs(tones)) * 0.95


def process_stroke(
        instrument: Instrument,
        stroke: Stroke,
        capo_fret: int,
        tempo: float,
        pluck_position: float,
        string_buffers: List[np.ndarray],
        total_time: float,
        sr: int
) -> float:
    """
    Process a single guitar stroke, generating tones for all notes in the stroke
    and updating the corresponding string buffers.

    Parameters
    ----------
    instrument : Instrument
        The instrument object containing string and playstyle characteristics.
    stroke : Stroke
        The stroke object representing a set of notes played together on different frets of a single string.
    capo_fret : int
        The position of the capo on the guitar neck, affecting the pitch of each note.
    tempo : float
        A multiplier to adjust note durations based on tempo (BPM).
    pluck_position : float
        The position on the string where it is plucked, affecting harmonic balance.
    string_buffers : List[np.ndarray]
        A list of arrays where each string's signal is accumulated.
    total_time : float
        The current total time in the sequence, used to place new tones correctly in the timeline.
    sr : int
        The sample rate of the signal, default is 44100 Hz.

    Returns
    -------
    float
        The total time after processing the stroke, accounting for all notes in the stroke.
    """

    assert len(stroke.frets) == len(stroke.values)

    stroke_time = 0

    # Iterate over all notes in the stroke (frets and note durations)
    # Apply smooth transitions (hammer on, pull off) if the instrument supports that
    for fret, value in zip(stroke.frets, stroke.values):

        # Adjust duration according to the note's value and the tempo
        duration = value.value * tempo

        # Synthesize the tone for the current note, with optional letting the note ring
        tone = synthesize_tone(
            instrument=instrument,
            string_number=stroke.string_number,
            fret=capo_fret + fret,
            duration=tempo if stroke.letRing else duration,  # Use whole note if the note should "let ring"
            pluck_position=pluck_position,
            decay_t0=-stroke_time + 0.005 if instrument.supports_transitions else 0,
            sr=sr
        )

        # Calculate where the tone should start in the output buffer, relative to the total time
        start_position = int((total_time + stroke_time) * sr)

        # Add the new tone to the appropriate string buffer with time-shifted overlap
        string_buffer = string_buffers[stroke.string_number - 1]
        updated_tone = concatenate_add(string_buffer, tone, shifted_by=start_position)

        # Update the buffer with the new tone
        string_buffers[stroke.string_number - 1] = updated_tone

        stroke_time += duration

    # Return the total time spent processing this stroke
    return stroke_time


def process_sequence_element(
        instrument: Instrument,
        element: SequenceElement,
        capo_fret: int,
        tempo: float,
        pluck_position: float,
        string_buffers: List[np.ndarray],
        total_time: float,
        sr: int
) -> float:
    """
    Process a sequence element, updating string buffers with the synthesized tones for each stroke.

    Parameters
    ----------
    instrument : Instrument
        The instrument object representing the guitar.
    element : SequenceElement
        A musical phrase composed of multiple strokes.
    capo_fret : int
        The capo position on the guitar.
    tempo : float
        Multiplier to adjust note durations.
    pluck_position : float
        The position where the string is plucked.
    string_buffers : List[np.ndarray]
        Buffers for each string, where the audio signals are accumulated.
    total_time : float
        The current time in the sequence.
    sr : int
        The sample rate of the signal, default is 44100 Hz.

    Returns
    -------
    float
        The updated total time after processing the sequence element.
    """

    element_time = 0

    for stroke in element.strokes:
        stroke_time = process_stroke(
            instrument=instrument,
            stroke=stroke,
            capo_fret=capo_fret,
            tempo=tempo,
            pluck_position=pluck_position,
            string_buffers=string_buffers,
            total_time=total_time,
            sr=sr
        )

        # Track the longest stroke time
        element_time = max(element_time, stroke_time)

    # Update the total time after processing the element
    total_time += element_time

    return total_time


def synthesize_sequence(
        instrument: Instrument,
        sequence: List[SequenceElement],
        capo_fret: int,
        tempo: float,
        pluck_position: float = 0.7,
        sr: int = 44100
) -> np.ndarray:
    """
    Synthesize the entire sequence of guitar notes into a continuous audio signal, with ringing tones for each string.

    Parameters
    ----------
    instrument : Instrument
        The instrument object, containing string and performance characteristics.
    sequence : List[SequenceElement]
        The list of sequence elements to synthesize into an audio signal.
    capo_fret : int
        The capo position, affecting the pitch of all notes.
    tempo : float
        A multiplier to adjust the duration of notes according to tempo.
    pluck_position : float, optional
        The position along the string where the pluck occurs, affecting harmonic structure. Default is 0.7.
    sr : int
        The sample rate of the signal, default is 44100 Hz.

    Returns
    -------
    np.ndarray
        The final synthesized audio signal for the entire sequence.
    """

    # Initialize buffers for each string (1-6) for guitars
    string_buffers = [np.array([]) for _ in range(len(instrument.strings))]
    total_time = 0

    for element in sequence:

        # Ensure that buffers for each string are padded to the maximum current length
        max_length = max(len(buffer) for buffer in string_buffers)
        string_buffers = [np.pad(buffer, (0, max_length - len(buffer))) for buffer in string_buffers]

        # Process the sequence element, updating the string buffers and total time
        total_time = process_sequence_element(
            instrument=instrument,
            element=element,
            capo_fret=capo_fret,
            tempo=tempo,
            pluck_position=pluck_position,
            string_buffers=string_buffers,
            total_time=total_time,
            sr=sr
        )

    # Pad all string buffers to the length of the longest buffer
    max_length = max(len(buffer) for buffer in string_buffers)
    padded_buffers = [np.pad(buffer, (0, max_length - len(buffer))) for buffer in string_buffers]

    # Sum all string buffers to create the final mixed audio signal
    final_tone = np.sum(padded_buffers, axis=0)

    return final_tone


def to_guitar_sequence(
        instrument: Instrument,
        sequence: List[SequenceElement],
        bpm: int = 60,
        capo_fret: int = 0,
        pluck_position: float = 0.7,
        sr: int = 44100
) -> np.ndarray:
    """
    Convert a sequence of guitar strokes into a complete audio waveform, representing the entire musical passage.
    This function handles tempo adjustments and normalizes the output to prepare it for listening or further processing.

    Parameters
    ----------
    instrument : Instrument
        The instrument object containing all string properties such as inharmonicity, decay rates, and dynamic range.
    sequence : List[SequenceElement]
        A list of sequence elements, each consisting of one or more strokes representing the musical passage.
    bpm : int, optional
        The tempo of the piece in beats per minute (BPM), default is 60 BPM (adagio tempo).
    capo_fret : int, optional
        The fret at which the capo is placed, default is 0 (no capo).
    pluck_position : float, optional
        The position along the string where the pluck occurs, affecting harmonic structure. Default is 0.7.
    sr : int, optional
        The sample rate for the audio sequence, default is 44100 Hz (CD-quality audio).

    Returns
    -------
    np.ndarray
        The complete normalized audio sequence, representing the guitar performance.
    """
    tempo = 60 / bpm
    tones = synthesize_sequence(
        instrument=instrument,
        sequence=sequence,
        capo_fret=capo_fret,
        tempo=tempo,
        pluck_position=pluck_position,
        sr=sr
    )
    audio_sequence = normalize_audio(tones)

    return audio_sequence


def generate_guitar_signal_from_sheet(
        instrument: Instrument,
        sheet: GuitarSheet,
        pluck_position: float = 0.7,
        sr: int = 44100,
        apply_convolution: bool = True,
        impulse_response_file: Optional[str] = None,
        apply_echo: bool = True,
        echo_delay: float = 0.2,
        echo_decay: float = 0.2
) -> np.ndarray:
    """
    Generate a processed guitar signal from a GuitarSheet object, with optional impulse response convolution and echo.

    Parameters
    ----------
    instrument : Instrument
        The instrument object containing string properties.
    sheet : GuitarSheet
        The GuitarSheet object containing musical metadata such as the sequence of notes, tempo, and capo position.
    pluck_position : float, optional
        The pluck position on the string, affecting harmonic structure, default is 0.7.
    sr : int, optional
        The sample rate for the audio signal, default is 44100 Hz.
    apply_convolution : bool, optional
        Whether to apply impulse response convolution, default is True.
    impulse_response_file : str, optional
        The file path to a custom impulse response WAV file. If not provided, the default impulse response is used.
    apply_echo : bool, optional
        Whether to apply an echo effect, default is True.
    echo_delay : float, optional
        The delay of the echo in seconds, default is 0.2s.
    echo_decay : float, optional
        The decay factor of the echo, default is 0.2.

    Returns
    -------
    np.ndarray
        The fully processed audio signal, ready for playback or further processing.
    """

    # Extract sequence, bpm, and capo_fret from the GuitarSheet object
    sequence = sheet.sequence
    bpm = sheet.bpm
    capo_fret = sheet.capo_fret

    # Generate the base guitar sequence audio
    signal = to_guitar_sequence(
        instrument=instrument,
        sequence=sequence,
        capo_fret=capo_fret,
        bpm=bpm,
        pluck_position=pluck_position,
        sr=sr
    )

    # Convolve with impulse response if applicable
    if apply_convolution:
        if impulse_response_file:

            # Load custom impulse response if file is provided
            impulse_response = load_impulse_response(impulse_response_file)
        elif default_impulse_response is not None:

            # Use the default impulse response if no file is provided
            impulse_response = default_impulse_response
        else:
            raise ValueError("No impulse response file or default provided for convolution.")

        # Apply convolution with the impulse response
        signal = convolve_with_impulse_response(signal, impulse_response)

    # Apply echo effect if applicable
    if apply_echo:
        signal = add_echo(signal, delay=echo_delay, decay=echo_decay)

    # Normalize the audio to ensure no clipping
    signal = normalize_audio(signal)

    return signal

"""
py_guitar_synth.tab_parser
==========================

Project Overview
----------------
    The `py_guitar_synth` project aims to generate realistic guitar music from tab sheets by modeling the physical and
    musical characteristics of guitar strings and performance techniques. The project translates written guitar tabs
    into audio by simulating strokes, note durations, transitions, and string properties.

Script Purpose
--------------
    This module provides functions to parse guitar tab notation into structured data, such as strokes, sequences, and
    guitar sheets. It translates tab files into `GuitarSheet` objects by identifying notes, frets, and timing symbols.
    The parsed data is then used for synthesis and performance playback within the larger project.

Author
------
    Mustafa Alotbah
    Email: mustafa.alotbah@gmail.com
"""
from .types import Stroke, NoteValue, SequenceElement, GuitarSheet
from typing import List, Dict
import re

# String-to-number mapping for guitar strings (standard tuning)
string_to_number = {
    'e': 1,  # High E string
    'B': 2,  # B string
    'G': 3,  # G string
    'D': 4,  # D string
    'A': 5,  # A string
    'E': 6   # Low E string
}


# Mapping symbols to note values for note duration
symbol_to_note_value = {
    '': NoteValue.quarterNote,  # No symbol defaults to a quarter note
    '!': NoteValue.eighthNote,
    '!!': NoteValue.sixteenthNote,
    '+': NoteValue.halfNote,
    '++': NoteValue.wholeNote
}

# Mapping letters a-f to fret numbers 10-15, often used in tabs
letter_to_fret = {
    'a': 10,
    'b': 11,
    'c': 12,
    'd': 13,
    'e': 14,
    'f': 15
}


def parse_fret_with_symbol(fret: str, symbol: str) -> (int, NoteValue):
    """
    Parse a fret and its associated symbol to return the fret number and corresponding note value.

    Parameters
    ----------
    fret : str
        The fret number as a string (can be a number or letter).
    symbol : str
        The symbol associated with the fret for note duration (e.g., '!', '++').

    Returns
    -------
    int
        The fret number.
    NoteValue
        The corresponding note value.
    """

    fret_number = 0
    if fret.isdigit():
        fret_number = int(fret)
    elif fret in letter_to_fret:
        fret_number = letter_to_fret.get(fret, 0)

    note_value = symbol_to_note_value.get(symbol, NoteValue.eighthNote)  # Default to eighth note for grouped frets
    return fret_number, note_value


def extract_frets_and_symbols(line: str, i: int, num_positions: int) -> (str, str, int):
    """
    Extract the fret and symbol for note duration from the given tab line.

    Parameters
    ----------
    line : str
        The string's tab line.
    i : int
        The current position (column) in the tab.
    num_positions : int
        The total number of positions in the tab.

    Returns
    -------
    str
        The fret number as a string.
    str
        The symbol associated with the fret (e.g., '!', '++').
    int
        The index of the next non-fret character.
    """
    fret = line[i]
    symbol = ""

    # Look ahead to capture symbols like '+', '!', etc.
    next_idx = i + 1
    while next_idx < num_positions and (line[next_idx] in ['+', '!']):
        symbol += line[next_idx]
        next_idx += 1

    return fret, symbol, next_idx


def process_frets_in_column(tab_lines: Dict[int, str], i: int, num_positions: int) -> (List[Stroke], int):
    """
    Process a single vertical slice of the tab (a column) and return the strokes and how much to advance the index.

    Parameters
    ----------
    tab_lines : Dict[int, str]
        The dictionary mapping string numbers to their tab content.
    i : int
        The current position (column) in the tab.
    num_positions : int
        The number of positions (columns) in the tab.

    Returns
    -------
    List[Stroke]
        The list of strokes for the current column.
    int
        The number of positions to advance after processing.
    """
    strokes = []
    max_fret_span = 1
    let_ring = False  # Default is False

    # Check if the column ends with 'r' to indicate the letRing parameter
    for string_number, line in tab_lines.items():
        next_idx = i
        while next_idx < num_positions and line[next_idx] != '-':
            if line[next_idx] == 'r':
                # Set let_ring to True if 'r' is found
                let_ring = True
                break
            next_idx += 1

        # Exit early if 'r' is found in any string
        if let_ring:
            break

    for string_number, line in tab_lines.items():
        # Check if the index exists
        if i < len(line):
            frets = []
            values = []
            next_idx = i

            # Handle consecutive frets and symbols within a single stroke
            while next_idx < num_positions and (
                    line[next_idx].isdigit() or
                    line[next_idx] in letter_to_fret or
                    line[next_idx] in ['+', '!']
            ):
                if line[next_idx].isdigit() or line[next_idx] in letter_to_fret:
                    fret, symbol, next_idx = extract_frets_and_symbols(line, next_idx, num_positions)
                    fret_number, note_value = parse_fret_with_symbol(fret, symbol)
                    frets.append(fret_number)
                    values.append(note_value)

            # If we gathered any frets, create a stroke for them
            if frets:
                strokes.append(Stroke(string_number=string_number, frets=frets, values=values, letRing=let_ring))

            # Update max_fret_span to the number of characters processed
            max_fret_span = max(max_fret_span, next_idx - i)

    return strokes, max_fret_span


def advance_index(i: int, max_fret_span: int) -> int:
    """
    Advance the index by the number of positions based on the maximum fret span.

    Parameters
    ----------
    i : int
        The current position or index in the tab (i.e., the current column being processed).
    max_fret_span : int
        The number of columns processed for the current note or chord. This is determined by
        how many characters were consumed to fully capture the notes (including fret numbers and symbols).

    Returns
    -------
    int
        The updated index or position, advanced by the number of columns processed.
    """
    return i + max_fret_span


def parse_guitar_tab(tab: str) -> List[SequenceElement]:
    """
    Parse a guitar tab string into a list of SequenceElement objects.

    Parameters
    ----------
    tab : str
        A string representing guitar tab lines.

    Returns
    -------
    List[SequenceElement]
        A list of SequenceElement objects representing the parsed strokes.
    """
    lines = tab.strip().splitlines()

    # Parse the lines into a dictionary mapping string numbers to tab content
    tab_lines = parse_lines_to_tab_lines(lines)

    # Get the number of positions (columns) in the tab
    num_positions = len(next(iter(tab_lines.values())))

    # Initialize list to hold the parsed strokes
    sequence = []

    # Iterate through each vertical slice of the tab (each column)
    i = 0
    while i < num_positions:
        # Process each column and get the strokes and how far to advance
        strokes, max_fret_span = process_frets_in_column(tab_lines, i, num_positions)

        # If there are strokes, create a new SequenceElement and add it to the sequence
        if strokes:
            sequence.append(SequenceElement(strokes=strokes))

        # Advance the index
        i = advance_index(i, max_fret_span)

    return sequence


def parse_lines_to_tab_lines(lines: List[str]) -> Dict[int, str]:
    """
    Parse the tab lines and map each string line to its corresponding string number.

    Parameters:
    - lines (List[str]): The list of tab lines.

    Returns:
    - Dict[int, str]: A dictionary mapping string numbers to their tab content.
    """
    tab_lines = {}
    for line in lines:
        line = line.strip()  # Remove leading/trailing spaces
        if not line or line[0] not in string_to_number:  # Skip invalid lines
            continue
        string_number = string_to_number[line[0]]  # Get string number from the first character
        tab_lines[string_number] = line[2:]  # The actual tab content starts from index 2
    return tab_lines


def parse_guitar_tab_from_file(file_path: str) -> GuitarSheet:
    """
    Read a guitar tab from a file, process multiple sections separated by blank lines,
    and parse each section into a list of SequenceElement objects. The function will ignore
    metadata such as title, author, BPM, and capo fret.

    Parameters
    ----------
    file_path : str
        The path to the file containing the guitar tab.

    Returns
    -------
    GuitarSheet
        A GuitarSheet object representing the parsed strokes, with default BPM and capo fret values.
    """
    with open(file_path, 'r') as file:
        tab_content = file.read()

    # Initialize bpm and capo_fret
    bpm = 60
    capo_fret = 0
    title = "Unknown Title"
    author = "Unknown Author"

    # Check for bpm and capo fret in the tab content using regex
    bpm_match = re.search(r'bpm\s*:\s*(\d+)', tab_content, re.IGNORECASE)
    capo_match = re.search(r'capo\s*fret\s*:\s*(\d+)', tab_content, re.IGNORECASE)
    title_match = re.search(r'title\s*:\s*(.*)', tab_content, re.IGNORECASE)
    author_match = re.search(r'author\s*:\s*(.*)', tab_content, re.IGNORECASE)

    if bpm_match:
        bpm = int(bpm_match.group(1))

    if capo_match:
        capo_fret = int(capo_match.group(1))

    if title_match:
        title = title_match.group(1).strip()

    if author_match:
        author = author_match.group(1).strip()

    # Remove metadata lines (title, author, bpm, and capo fret) before processing the tab content
    cleaned_tab_content = "\n".join(
        line for line in tab_content.splitlines()
        if not re.match(r'(title|author|bpm|capo\s*fret)\s*', line, re.IGNORECASE)
    )

    # Split the cleaned content into sections by blank lines (one or more newlines)
    sections = cleaned_tab_content.strip().split('\n\n')

    # Initialize the final sequence that will accumulate all parsed sequences
    final_sequence = []

    # Process each section of the tab
    for section in sections:
        if section.strip():  # Ignore empty sections
            # Remove comment lines starting with #
            lines = section.splitlines()
            non_comment_lines = [line for line in lines if not line.strip().startswith('#')]

            # Join the filtered lines back into a section
            non_comment_section = "\n".join(non_comment_lines)

            if non_comment_section.strip():  # If the section has valid content
                section_sequence = parse_guitar_tab(non_comment_section)
                final_sequence.extend(section_sequence)

    # Return a GuitarSheet object with the parsed sequence, bpm, and capo fret
    return GuitarSheet(title=title, author=author, sequence=final_sequence, bpm=bpm, capo_fret=capo_fret)

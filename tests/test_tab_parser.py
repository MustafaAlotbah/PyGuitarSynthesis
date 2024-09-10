from py_guitar_synth.tab_parser import parse_guitar_tab, parse_guitar_tab_from_file


def test_parse_guitar_tab():
    tab_content = """
    e |----------------|
    B |----------------|
    G |----------------|
    D |--2-------------|
    A |--0-------------|
    E |----------------|
    """

    sequence = parse_guitar_tab(tab_content)

    assert len(sequence) == 1  #
    assert len(sequence[0].strokes) == 2
    assert len(sequence[0].strokes[0].values) == 1
    assert len(sequence[0].strokes[0].frets) == 1


def test_parse_guitar_tab_from_file():
    sheet = parse_guitar_tab_from_file('py_guitar_synth/assets/law_bass.txt')

    assert sheet is not None
    assert len(sheet.sequence) > 0  # There should be a sequence of strokes in the sheet

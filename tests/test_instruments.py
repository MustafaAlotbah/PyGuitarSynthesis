from py_guitar_synth.instrument_parser import load_instrument_from_json


def test_load_instrument_from_json():
    # Use the default classical guitar file from assets
    instrument = load_instrument_from_json('py_guitar_synth/assets/classical_guitar.json')

    assert instrument is not None
    assert len(instrument.strings) > 0  # The instrument should have strings
    assert instrument.supports_vibrato is True  # The classical guitar does support a vibrato

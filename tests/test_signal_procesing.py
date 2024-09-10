import numpy as np
from py_guitar_synth.signal_processing import add_echo, normalize_audio


def test_normalize_audio():
    signal = np.array([0.5, 1.0, -1.0, 0.0])
    normalized_signal = normalize_audio(signal)

    assert np.max(np.abs(normalized_signal)) == 0.95  # Normalized peak should be 0.95

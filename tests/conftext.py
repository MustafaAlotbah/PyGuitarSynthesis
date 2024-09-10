import pytest
from py_guitar_synth import default_classical_guitar, law_bass_f_aini

@pytest.fixture
def classical_guitar():
    return default_classical_guitar

@pytest.fixture
def law_bass_sheet():
    return law_bass_f_aini

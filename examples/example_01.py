from py_guitar_synth import *
import sounddevice

if __name__ == '__main__':

    print(default_classical_guitar)
    print(law_bass_f_aini)
    print(agua_marina)

    # Select a GuitarSheet object
    sheet = law_bass_f_aini
    sr = 44100

    # Generate the guitar signal from the GuitarSheet
    signal = generate_guitar_signal_from_sheet(
        instrument=default_classical_guitar,
        sheet=sheet,
        pluck_position=0.7,
        sr=sr,
        apply_convolution=True,
        impulse_response_file=None,  # Use default impulse response
        apply_echo=True,
        echo_delay=0.2,
        echo_decay=0.2
    )

    # Play the generated signal
    sounddevice.play(signal, sr)
    sounddevice.wait()

import argparse
import sounddevice as sd
import threading

from py_guitar_synth import (
    default_classical_guitar,
    default_violine,
    default_piano,
    law_bass_f_aini,
    agua_marina,
    generate_guitar_signal_from_sheet,
    parse_guitar_tab_from_file
)

# Dictionary mapping instrument names to instrument objects
INSTRUMENTS = {
    'classical_guitar': default_classical_guitar,
    'violin': default_violine,
    'piano': default_piano
}

# Dictionary mapping sheet names to GuitarSheet objects
SHEETS = {
    'law_bass_f_aini': law_bass_f_aini,
    'agua_marina': agua_marina
}


def main():
    parser = argparse.ArgumentParser(
        description="py_guitar_synth: A tool for synthesizing guitar audio from tab sheets."
    )

    # Instrument choice
    parser.add_argument(
        '-i', '--instrument', choices=INSTRUMENTS.keys(),
        default='classical_guitar', help="Choose an instrument (default: classical_guitar)."
    )

    # Sheet choice or file path
    parser.add_argument(
        '-s', '--sheet', type=str,
        default='law_bass_f_aini',
        help="Choose a sheet to synthesize or provide a path to a tab file (default: law_bass_f_aini)."
    )

    # Pluck position
    parser.add_argument(
        '-p', '--pluck_position', type=float, default=0.7,
        help="Set the pluck position on the string (0 to 1, default: 0.7)."
    )

    # Sample rate
    parser.add_argument(
        '--sr', type=int, default=44100,
        help="Set the sample rate for the audio output (default: 44100)."
    )

    # Option to apply impulse response convolution
    parser.add_argument(
        '--no-convolution', action='store_true',
        help="Disable convolution with an impulse response."
    )

    # Custom impulse response file path
    parser.add_argument(
        '--ir-file', type=str, help="Path to a custom impulse response file (WAV)."
    )

    # Option to apply echo effect
    parser.add_argument(
        '--no-echo', action='store_true', help="Disable the echo effect."
    )

    # Echo delay time
    parser.add_argument(
        '--echo-delay', type=float, default=0.2,
        help="Set the echo delay time in seconds (default: 0.2s)."
    )

    # Echo decay factor
    parser.add_argument(
        '--echo-decay', type=float, default=0.2,
        help="Set the echo decay factor (default: 0.2)."
    )

    args = parser.parse_args()

    # Load the selected instrument and sheet
    instrument = INSTRUMENTS[args.instrument]

    print(f"Reading Sheet {args.sheet}")

    # Load the sheet, either from predefined sheets or from a file
    if args.sheet in SHEETS:
        sheet = SHEETS[args.sheet]
    else:
        # Attempt to load the sheet from a file path
        try:
            sheet = parse_guitar_tab_from_file(args.sheet)
        except Exception as e:
            print(f"Error loading sheet from '{args.sheet}': {e}")
            return

    # Generate the guitar signal
    signal = generate_guitar_signal_from_sheet(
        instrument=instrument,
        sheet=sheet,
        pluck_position=args.pluck_position,
        sr=args.sr,
        apply_convolution=not args.no_convolution,
        impulse_response_file=args.ir_file,
        apply_echo=not args.no_echo,
        echo_delay=args.echo_delay,
        echo_decay=args.echo_decay
    )

    def play():
        # Play the generated audio using sounddevice
        print(f"Playing '{sheet.title}' by '{sheet.author}' with {args.instrument}...")
        sd.play(signal, args.sr)
        sd.wait()

    # Start the playback in a separate thread
    play_thread = threading.Thread(target=play)
    play_thread.start()

    # Main thread continues to run
    try:
        while play_thread.is_alive():
            play_thread.join(timeout=1)
    except KeyboardInterrupt:
        sd.stop()
        print("Playback stopped.")


if __name__ == '__main__':
    main()

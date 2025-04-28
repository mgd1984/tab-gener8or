from basic_pitch.inference import predict
from tayuya import MIDIParser
import os
import sys
from io import StringIO
import contextlib
import argparse
from pathlib import Path

# Helper function to capture stdout
@contextlib.contextmanager
def capture_stdout():
    stdout = sys.stdout
    string_io = StringIO()
    sys.stdout = string_io
    yield string_io
    sys.stdout = stdout

def process_audio_file(mp3_path):
    """
    Process an audio file to generate MIDI and tablature.
    
    Args:
        mp3_path (str): Path to the MP3 file
        
    Returns:
        dict: Results containing MIDI and tab data
    """
    # Create output filenames based on input filename
    base_name = Path(mp3_path).stem
    midi_path = f"{base_name}_processed.mid"
    tab_path = f"{base_name}_tab.txt"
    
    print(f"Processing {mp3_path}...")
    # Check if input file exists
    if not os.path.exists(mp3_path):
        print(f"ERROR: Input file does not exist: {mp3_path}")
        return None

    try:
        # 1. mp3 ➜ midi (in-memory)
        print("Running basic-pitch inference...")
        model_out, midi_data, note_events = predict(mp3_path)

        print(f"Saving MIDI data to {midi_path}...")
        midi_data.write(midi_path)        # save to disk for step-2
        
        # Verify MIDI file was created
        if os.path.exists(midi_path):
            print(f"MIDI file successfully created at: {midi_path}")
            print(f"MIDI file size: {os.path.getsize(midi_path)} bytes")
        else:
            print(f"ERROR: MIDI file was not created at: {midi_path}")
            return None

        # 2. midi ➜ tab (focusing on track 1 which contains the note data)
        print(f"Parsing MIDI file {midi_path}...")
        try:
            print("Rendering tabs from track 1...")
            mid = MIDIParser(midi_path, track=1)  # Track 1 has the notes
            
            # Since render_tabs() returns None but prints to stdout, we'll capture the output
            with capture_stdout() as captured:
                mid.render_tabs()
                tabs = captured.getvalue()
            
            # Check if we captured any tabs
            if tabs and len(tabs.strip()) > 0:
                print("\n--- Guitar Tab ---")
                print(tabs)
                print("------------------\n")
                
                # Save to file
                with open(tab_path, "w") as f:
                    f.write(tabs)
                print(f"Tab saved to {tab_path}")
                
                return {
                    "tabs": tabs,
                    "midi_path": midi_path,
                    "tab_path": tab_path
                }
            else:
                print("\nWARNING: No tabs were generated (empty output)")
                print("The MIDI file was successfully created and can be opened in any MIDI software.")
                return None
            
        except Exception as e:
            print(f"Failed to render tabs: {e}")
            return None
        
    except FileNotFoundError:
        print(f"Error: Input file '{mp3_path}' not found.")
        print("Please make sure the MP3 file exists in the same directory as the script.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    """
    Main entry point for command line interface.
    Handles argument parsing and processing.
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Convert MP3 guitar recordings to tablature")
    parser.add_argument("mp3_file", nargs="?", default="trade-war-surfin.mp3",
                       help="MP3 file to process (default: trade-war-surfin.mp3)")
    args = parser.parse_args()
    
    # Process the audio file
    results = process_audio_file(args.mp3_file)
    
    if results:
        print("Done!")
    else:
        print("Processing failed.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
from tayuya import MIDIParser
import sys

def render_tab_with_debug():
    # Default values
    midi_path = "trade-war-surfin_processed.mid"
    track_num = 1
    
    # Check for command line arguments (optional)
    if len(sys.argv) > 1:
        midi_path = sys.argv[1]
    if len(sys.argv) > 2:
        track_num = int(sys.argv[2])
    
    print(f"Loading MIDI file: {midi_path}")
    print(f"Using track: {track_num}")
    
    try:
        # Create the MIDIParser object
        mid = MIDIParser(midi_path, track=track_num)
        
        # Inspect the MIDIParser object
        print(f"MIDIParser attributes: {dir(mid)}")
        
        # Attempt to render tabs
        print("Attempting to render tabs...")
        tabs = mid.render_tabs()
        
        if tabs is not None:
            print("\n--- Guitar Tab ---")
            print(tabs)
            print("------------------\n")
            
            # Save to file
            with open(f"track_{track_num}_tab.txt", "w") as f:
                f.write(tabs)
            print(f"Tab saved to track_{track_num}_tab.txt")
        else:
            print("No tabs were generated (render_tabs() returned None)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    render_tab_with_debug() 
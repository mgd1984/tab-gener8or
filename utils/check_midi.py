import mido

# Path to your MIDI file
midi_path = "trade-war-surfin_processed.mid"

try:
    # Load the MIDI file
    midi_file = mido.MidiFile(midi_path)
    
    # Print basic information
    print(f"MIDI File: {midi_path}")
    print(f"Number of tracks: {len(midi_file.tracks)}")
    print(f"MIDI file type: {midi_file.type}")
    print(f"MIDI ticks per beat: {midi_file.ticks_per_beat}")
    
    # Print information about each track
    for i, track in enumerate(midi_file.tracks):
        note_count = sum(1 for msg in track if msg.type == 'note_on')
        print(f"\nTrack {i}: '{track.name}' - {len(track)} messages, {note_count} notes")
        
        # Count message types
        message_types = {}
        for msg in track:
            msg_type = msg.type
            if msg_type in message_types:
                message_types[msg_type] += 1
            else:
                message_types[msg_type] = 1
        
        # Print message type counts
        print("Message types:")
        for msg_type, count in message_types.items():
            print(f"  {msg_type}: {count}")
            
        # Print the first few notes if they exist
        notes = [msg for msg in track if msg.type == 'note_on' and msg.velocity > 0]
        if notes:
            print("\nFirst 5 notes:")
            for note in notes[:5]:
                print(f"  Note: {note.note} (velocity: {note.velocity})")
    
except Exception as e:
    print(f"Error: {e}") 
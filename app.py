import streamlit as st
import os
import sys
import tempfile
from io import StringIO
import contextlib
import time
import logging
from basic_pitch.inference import predict
from tayuya import MIDIParser
import base64
import re
from pathlib import Path
import html

# Configure logging to suppress Basic Pitch debug messages
logging.getLogger().setLevel(logging.WARNING)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging

# Initialize session state for theme and app state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Default to dark theme

if 'version' not in st.session_state:
    st.session_state.version = '1.0.0'  # App version

if 'show_landing' not in st.session_state:
    st.session_state.show_landing = True

# Custom CSS to improve tablature display
st.set_page_config(
    page_title="MP3 to Guitar Tab Converter",
    page_icon="🎸",
    layout="wide"
)

# Dark theme CSS
dark_css = """
<style>
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 100%;
    margin: 0;
    padding: 0;
    background-color: #0a0a0a;
    color: #ffffff;
}

.stApp {
    max-width: 100vw;
    background-color: #0a0a0a;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {
    visibility: hidden;
}

/* Sidebar styling */
.sidebar-content {
    width: 25rem;
    background-color: #0a0a0a;
}

[data-testid="stSidebar"] {
    background-color: #0a0a0a !important;
}

[data-testid="stSidebarContent"] {
    background-color: #0a0a0a !important;
}

/* Title and headings */
h1, h2, h3, h4, h5, h6 {
    font-weight: 700 !important;
    color: #ffffff !important;
}

h1 {
    font-size: 2.5rem !important;
    letter-spacing: -0.025em !important;
    margin-bottom: 2rem !important;
}

h2 {
    font-size: 1.8rem !important;
    margin-top: 2rem !important;
}

/* Standard text */
p, li, div {
    color: #e0e0e0;
}

/* Links */
a {
    color: #ff4d4d !important;
    text-decoration: none !important;
}

a:hover {
    text-decoration: underline !important;
}

/* Button styling */
.stButton button {
    background-color: #ff4d4d !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stButton button:hover {
    background-color: #e63939 !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 77, 77, 0.3);
}

/* Divider */
hr {
    border-color: #333333 !important;
    margin: 2rem 0 !important;
}

/* File uploader */
.stFileUploader {
    background-color: #121212 !important;
    border: 2px dashed #333333 !important;
    border-radius: 8px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Tablature styling */
.tab-container {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    white-space: pre !important;
    overflow-x: auto !important;
    width: 100% !important;
    max-width: 100% !important;
    background-color: #121212 !important;
    padding: 1.5rem !important;
    border-radius: 8px !important;
    border: 1px solid #333333 !important;
    line-height: 1.2;
    box-sizing: border-box !important;
    display: block !important;
    margin-top: 1rem !important;
    color: #e0e0e0 !important;
}

/* Success message */
.stSuccess {
    background-color: rgba(76, 175, 80, 0.2) !important;
    color: #4CAF50 !important;
    border: 1px solid #4CAF50 !important;
}

/* Error message */
.stError {
    background-color: rgba(255, 77, 77, 0.2) !important;
    color: #ff4d4d !important;
    border: 1px solid #ff4d4d !important;
}

/* Info message */
.stInfo {
    background-color: rgba(33, 150, 243, 0.2) !important;
    color: #2196F3 !important;
    border: 1px solid #2196F3 !important;
}

/* Download button styling */
.download-btn {
    display: inline-block;
    background-color: #121212 !important;
    color: white !important;
    padding: 12px 24px !important;
    text-align: center;
    text-decoration: none !important;
    border-radius: 4px !important;
    border: 1px solid #ff4d4d !important;
    cursor: pointer;
    font-size: 16px;
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
    transition: all 0.2s ease;
    font-weight: 600;
}

.download-btn:hover {
    background-color: #ff4d4d !important;
    color: white !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 77, 77, 0.3);
}

/* Audio player styling */
audio {
    width: 100% !important;
    margin: 1rem 0 !important;
    border-radius: 8px !important;
    background-color: #121212 !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #ff4d4d !important;
}

/* Fix for tablature display */
pre {
    white-space: pre;
    overflow-x: auto;
    max-width: 100%;
    font-size: 13px;
    margin: 0;
    padding: 0;
    color: #e0e0e0 !important;
}

/* Blocks */
.stBlock {
    background-color: #121212 !important;
    border-radius: 8px !important;
    padding: 1.5rem !important;
    margin: 1.5rem 0 !important;
    border: 1px solid #333333 !important;
}

/* Theme toggle switch styling */
.theme-toggle-container {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
}

.theme-toggle-label {
    margin-right: 10px;
    color: #e0e0e0;
}

/* Tooltip styling */
.tooltip {
    position: relative;
    display: inline-block;
    cursor: help;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 250px;
    background-color: #1a1a1a;
    color: #e0e0e0;
    text-align: center;
    border-radius: 6px;
    padding: 10px;
    position: absolute;
    z-index: 1000;
    bottom: 125%;
    left: 50%;
    margin-left: -125px;
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 14px;
    font-weight: normal;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
    border: 1px solid #333333;
    pointer-events: none;
}

.tooltip .tooltiptext::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: #1a1a1a transparent transparent transparent;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}

/* Footer styling */
.app-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    padding: 10px 20px;
    background-color: #0a0a0a;
    color: #666;
    font-size: 12px;
    text-align: center;
    border-top: 1px solid #333;
}

/* Hero section styling */
.hero-container {
    position: relative;
    width: 100%;
    height: 500px;
    overflow: hidden;
    border-radius: 12px;
    margin-bottom: 3rem;
    background-color: #121212;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
}

.hero-image {
    position: absolute;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.5;
}

.hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
    padding: 0 2rem;
    max-width: 800px;
}

.hero-title {
    font-size: 3.5rem !important;
    margin-bottom: 1rem !important;
    color: #ffffff !important;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.7);
}

.hero-subtitle {
    font-size: 1.5rem;
    margin-bottom: 2rem;
    color: #e0e0e0;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.7);
}

.cta-button {
    background-color: #ff4d4d;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 28px;
    font-size: 1.2rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(255, 77, 77, 0.5);
}

.cta-button:hover {
    background-color: #e63939;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(255, 77, 77, 0.6);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    h1 {
        font-size: 1.8rem !important;
    }
    
    .download-btn {
        padding: 8px 16px !important;
        font-size: 14px;
        width: 100%;
        text-align: center;
    }
    
    .tab-container {
        padding: 0.8rem !important;
    }
    
    .hero-title {
        font-size: 2.5rem !important;
    }
    
    .hero-subtitle {
        font-size: 1.2rem !important;
    }
    
    .cta-button {
        padding: 12px 24px;
        font-size: 1rem;
    }
}

/* Audio visualizer */
.audio-player-container {
    width: 100%;
    background-color: #121212;
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0;
    border: 1px solid #333333;
}

.waveform {
    width: 100%;
    height: 100px;
    margin-bottom: 10px;
    background-color: #121212;
}

.audio-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 10px;
}

.audio-control-button {
    background-color: #ff4d4d;
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    margin-right: 10px;
}

.audio-control-button:hover {
    background-color: #e63939;
    transform: scale(1.05);
}

.audio-time {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: #e0e0e0;
    margin: 0 10px;
}

.audio-progress {
    flex-grow: 1;
    height: 5px;
    background-color: #333333;
    border-radius: 3px;
    position: relative;
    cursor: pointer;
}

.audio-progress-bar {
    height: 100%;
    background-color: #ff4d4d;
    border-radius: 3px;
    width: 0%;
}

.audio-volume-container {
    display: flex;
    align-items: center;
    margin-left: 15px;
}

.audio-volume {
    width: 80px;
    height: 5px;
    background-color: #333333;
    border-radius: 3px;
    position: relative;
    cursor: pointer;
}

.audio-volume-bar {
    height: 100%;
    background-color: #ff4d4d;
    border-radius: 3px;
    width: 70%;
}
</style>
"""

# Light theme CSS
light_css = """
<style>
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 100%;
    margin: 0;
    padding: 0;
    background-color: #ffffff;
    color: #333333;
}

.stApp {
    max-width: 100vw;
    background-color: #ffffff;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {
    visibility: hidden;
}

/* Sidebar styling */
.sidebar-content {
    width: 25rem;
    background-color: #ffffff;
}

[data-testid="stSidebar"] {
    background-color: #ffffff !important;
}

[data-testid="stSidebarContent"] {
    background-color: #ffffff !important;
}

/* Title and headings */
h1, h2, h3, h4, h5, h6 {
    font-weight: 700 !important;
    color: #1a1a1a !important;
}

h1 {
    font-size: 2.5rem !important;
    letter-spacing: -0.025em !important;
    margin-bottom: 2rem !important;
}

h2 {
    font-size: 1.8rem !important;
    margin-top: 2rem !important;
}

/* Standard text */
p, li, div {
    color: #444444;
}

/* Links */
a {
    color: #ff4d4d !important;
    text-decoration: none !important;
}

a:hover {
    text-decoration: underline !important;
}

/* Button styling */
.stButton button {
    background-color: #ff4d4d !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 0.5rem 1.5rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stButton button:hover {
    background-color: #e63939 !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 77, 77, 0.3);
}

/* Divider */
hr {
    border-color: #e0e0e0 !important;
    margin: 2rem 0 !important;
}

/* File uploader */
.stFileUploader {
    background-color: #f8f9fa !important;
    border: 2px dashed #dddddd !important;
    border-radius: 8px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
}

/* Tablature styling */
.tab-container {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    white-space: pre !important;
    overflow-x: auto !important;
    width: 100% !important;
    max-width: 100% !important;
    background-color: #f8f9fa !important;
    padding: 1.5rem !important;
    border-radius: 8px !important;
    border: 1px solid #dee2e6 !important;
    line-height: 1.2;
    box-sizing: border-box !important;
    display: block !important;
    margin-top: 1rem !important;
    color: #333333 !important;
}

/* Success message */
.stSuccess {
    background-color: rgba(76, 175, 80, 0.1) !important;
    color: #4CAF50 !important;
    border: 1px solid #4CAF50 !important;
}

/* Error message */
.stError {
    background-color: rgba(255, 77, 77, 0.1) !important;
    color: #ff4d4d !important;
    border: 1px solid #ff4d4d !important;
}

/* Info message */
.stInfo {
    background-color: rgba(33, 150, 243, 0.1) !important;
    color: #2196F3 !important;
    border: 1px solid #2196F3 !important;
}

/* Download button styling */
.download-btn {
    display: inline-block;
    background-color: #ffffff !important;
    color: #ff4d4d !important;
    padding: 12px 24px !important;
    text-align: center;
    text-decoration: none !important;
    border-radius: 4px !important;
    border: 1px solid #ff4d4d !important;
    cursor: pointer;
    font-size: 16px;
    margin-top: 1.5rem !important;
    margin-bottom: 1.5rem !important;
    transition: all 0.2s ease;
    font-weight: 600;
}

.download-btn:hover {
    background-color: #ff4d4d !important;
    color: white !important;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(255, 77, 77, 0.3);
}

/* Audio player styling */
audio {
    width: 100% !important;
    margin: 1rem 0 !important;
    border-radius: 8px !important;
    background-color: #f8f9fa !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #ff4d4d !important;
}

/* Fix for tablature display */
pre {
    white-space: pre;
    overflow-x: auto;
    max-width: 100%;
    font-size: 13px;
    margin: 0;
    padding: 0;
    color: #333333 !important;
}

/* Blocks */
.stBlock {
    background-color: #f8f9fa !important;
    border-radius: 8px !important;
    padding: 1.5rem !important;
    margin: 1.5rem 0 !important;
    border: 1px solid #dee2e6 !important;
}

/* Theme toggle switch styling */
.theme-toggle-container {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
}

.theme-toggle-label {
    margin-right: 10px;
    color: #333333;
}

/* Tooltip styling */
.tooltip {
    position: relative;
    display: inline-block;
    cursor: help;
}

.tooltip .tooltiptext {
    visibility: hidden;
    width: 250px;
    background-color: #ffffff;
    color: #333333;
    text-align: center;
    border-radius: 6px;
    padding: 10px;
    position: absolute;
    z-index: 1000;
    bottom: 125%;
    left: 50%;
    margin-left: -125px;
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 14px;
    font-weight: normal;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    border: 1px solid #dee2e6;
    pointer-events: none;
}

.tooltip .tooltiptext::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: #ffffff transparent transparent transparent;
}

.tooltip:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
}

/* Footer styling */
.app-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    padding: 10px 20px;
    background-color: #ffffff;
    color: #999;
    font-size: 12px;
    text-align: center;
    border-top: 1px solid #eee;
}

/* Hero section styling */
.hero-container {
    position: relative;
    width: 100%;
    height: 500px;
    overflow: hidden;
    border-radius: 12px;
    margin-bottom: 3rem;
    background-color: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.hero-image {
    position: absolute;
    width: 100%;
    height: 100%;
    object-fit: cover;
    opacity: 0.7;
}

.hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
    padding: 0 2rem;
    max-width: 800px;
}

.hero-title {
    font-size: 3.5rem !important;
    margin-bottom: 1rem !important;
    color: #1a1a1a !important;
    text-shadow: 0 2px 10px rgba(255, 255, 255, 0.7);
}

.hero-subtitle {
    font-size: 1.5rem;
    margin-bottom: 2rem;
    color: #333333;
    text-shadow: 0 2px 8px rgba(255, 255, 255, 0.7);
}

.cta-button {
    background-color: #ff4d4d;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 12px 28px;
    font-size: 1.2rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(255, 77, 77, 0.5);
}

.cta-button:hover {
    background-color: #e63939;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(255, 77, 77, 0.6);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    h1 {
        font-size: 1.8rem !important;
    }
    
    .download-btn {
        padding: 8px 16px !important;
        font-size: 14px;
        width: 100%;
        text-align: center;
    }
    
    .tab-container {
        padding: 0.8rem !important;
    }
    
    .hero-title {
        font-size: 2.5rem !important;
    }
    
    .hero-subtitle {
        font-size: 1.2rem !important;
    }
    
    .cta-button {
        padding: 12px 24px;
        font-size: 1rem;
    }
}

/* Audio visualizer */
.audio-player-container {
    width: 100%;
    background-color: #f8f9fa;
    border-radius: 8px;
    padding: 15px;
    margin: 15px 0;
    border: 1px solid #dee2e6;
}

.waveform {
    width: 100%;
    height: 100px;
    margin-bottom: 10px;
    background-color: #f8f9fa;
}

.audio-controls {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 10px;
}

.audio-control-button {
    background-color: #ff4d4d;
    color: white;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
    margin-right: 10px;
}

.audio-control-button:hover {
    background-color: #e63939;
    transform: scale(1.05);
}

.audio-time {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: #333333;
    margin: 0 10px;
}

.audio-progress {
    flex-grow: 1;
    height: 5px;
    background-color: #dee2e6;
    border-radius: 3px;
    position: relative;
    cursor: pointer;
}

.audio-progress-bar {
    height: 100%;
    background-color: #ff4d4d;
    border-radius: 3px;
    width: 0%;
}

.audio-volume-container {
    display: flex;
    align-items: center;
    margin-left: 15px;
}

.audio-volume {
    width: 80px;
    height: 5px;
    background-color: #dee2e6;
    border-radius: 3px;
    position: relative;
    cursor: pointer;
}

.audio-volume-bar {
    height: 100%;
    background-color: #ff4d4d;
    border-radius: 3px;
    width: 70%;
}
</style>
"""

# Helper function to capture stdout
@contextlib.contextmanager
def capture_stdout():
    stdout = sys.stdout
    string_io = StringIO()
    sys.stdout = string_io
    yield string_io
    sys.stdout = stdout

def process_audio(audio_file):
    """Process an audio file to generate MIDI and tablature."""
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_audio:
        # Write uploaded file to a temporary file
        tmp_audio.write(audio_file.getvalue())
        tmp_audio_path = tmp_audio.name
    
    with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as tmp_midi:
        tmp_midi_path = tmp_midi.name
    
    try:
        with st.spinner("🎵 Analyzing audio using Basic Pitch..."):
            # Suppress stdout for Basic Pitch prediction
            with contextlib.redirect_stdout(StringIO()):
                # 1. mp3 ➜ midi (in-memory)
                model_out, midi_data, note_events = predict(tmp_audio_path)
            
            # Save MIDI to temporary file
            midi_data.write(tmp_midi_path)
        
        with st.spinner("🎸 Generating guitar tablature..."):
            # 2. midi ➜ tab (focusing on track 1 which contains the note data)
            # Since render_tabs() returns None but prints to stdout, we'll capture the output
            mid = MIDIParser(tmp_midi_path, track=1)  # Track 1 has the notes
            
            with capture_stdout() as captured:
                mid.render_tabs()
                tabs = captured.getvalue()
        
        # Read the MIDI file for download
        with open(tmp_midi_path, "rb") as f:
            midi_bytes = f.read()
        
        return {
            "tabs": tabs,
            "midi_bytes": midi_bytes,
            "midi_filename": os.path.basename(audio_file.name).replace(".mp3", ".mid")
        }
    
    finally:
        # Clean up temporary files
        try:
            os.unlink(tmp_audio_path)
            os.unlink(tmp_midi_path)
        except:
            pass

def format_tab_for_display(tab_text):
    """
    Format tablature text to better fit screen width.
    
    Args:
        tab_text (str): The raw tablature text
        
    Returns:
        str: Formatted tablature text with properly split lines
    """
    # Clean up any ANSI escape codes or terminal control sequences
    tab_text = re.sub(r'\x1B\[[0-9;]*[mK]', '', tab_text)
    
    lines = tab_text.strip().split('\n')
    if not lines:
        return tab_text
    
    # Identify guitar string lines (usually have string names like "e|---" or "E|---")
    formatted_lines = []
    i = 0
    
    while i < len(lines):
        # Check if we have at least 6 lines (standard guitar tab)
        if i + 5 < len(lines) and all('|' in line for line in lines[i:i+6]):
            chunk = lines[i:i+6]
            
            # Find max line length in this chunk
            max_length = max(len(line) for line in chunk)
            
            # If lines are too long, split them into smaller segments
            if max_length > 80:  # Increased from 60 to 80 for better display
                # How many segments we need
                segment_width = 80
                segments = (max_length + segment_width - 1) // segment_width
                
                for seg in range(segments):
                    start = seg * segment_width
                    end = min(start + segment_width, max_length)
                    
                    # Don't create empty segments
                    if start >= len(chunk[0]):
                        break
                        
                    # Extract the segment from each string line
                    segment_lines = []
                    for line in chunk:
                        # Make sure we include the string name (E, A, D, G, B, e) in each segment
                        if seg > 0 and '|' in line:
                            # Find the string identifier and separator
                            separator_index = line.index('|')
                            prefix = line[:separator_index + 1]
                            
                            # Create segment with the prefix
                            if start < len(line):
                                # Get content after prefix, starting from our segment start
                                # Calculate offset correctly to avoid cutting in wrong place
                                content_start = start - separator_index - 1
                                if content_start < 0:
                                    content_start = 0
                                content_part = line[separator_index+1:]
                                if content_start < len(content_part):
                                    segment = prefix + content_part[content_start:content_start+segment_width]
                                else:
                                    segment = prefix
                            else:
                                segment = prefix
                        else:
                            # First segment or line without separator
                            segment = line[start:end] if start < len(line) else ''
                        
                        segment_lines.append(segment)
                    
                    # Add a segment label for clarity
                    if segments > 1:
                        segment_lines.insert(0, f"--- Part {seg+1}/{segments} ---")
                    
                    formatted_lines.extend(segment_lines)
                    
                    # Add a blank line between segments
                    if seg < segments - 1:
                        formatted_lines.append("")
            else:
                # Lines are short enough, no need to split
                formatted_lines.extend(chunk)
            
            # Add a blank line after each chunk of 6 lines
            formatted_lines.append("")
            i += 6
        else:
            # If it's not a complete chunk of 6 lines, just add the line as is
            formatted_lines.append(lines[i])
            i += 1
    
    # Add CSS class for scrollable container to handle really wide tabs
    formatted_text = '\n'.join(formatted_lines)
    
    return formatted_text

def get_download_link(binary_file, filename, text, class_name=""):
    """Generate a download link for a binary file."""
    b64 = base64.b64encode(binary_file).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" class="download-btn {class_name}">{text}</a>'
    return href

def add_tooltip(text, tooltip_text):
    """Add a tooltip to any text element"""
    return f'<span class="tooltip">{text} ⓘ<span class="tooltiptext">{tooltip_text}</span></span>'

def get_image_as_base64(image_path):
    """Convert an image to base64 encoding for inline HTML use"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def render_hero_section():
    """Render the landing page hero section with background image"""
    # Check if player-piano-5.png exists in the assets/images directory
    image_path = "assets/images/player-piano-5.png"
    
    # Try to locate the image file
    if not os.path.exists(image_path):
        # If not in current directory, check common image directories
        possible_paths = [
            "images/player-piano-5.png",
            "static/player-piano-5.png",
            "assets/player-piano-5.png",
            "../player-piano-5.png"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                image_path = path
                break
    
    if os.path.exists(image_path):
        # Convert image to base64 for inline embedding
        img_base64 = get_image_as_base64(image_path)
        img_html = f'<img src="data:image/png;base64,{img_base64}" class="hero-image" alt="Mechanical hands playing piano">'
    else:
        # Fallback if image not found
        img_html = ""
    
    hero_html = f"""
    <div class="hero-container">
        {img_html}
        <div class="hero-content">
            <h1 class="hero-title">Transform Music into Tablature</h1>
            <p class="hero-subtitle">Convert your guitar recordings to easy-to-read tabs with our advanced AI-powered tool</p>
            <button onclick="document.getElementById('get-started').scrollIntoView({{behavior: 'smooth'}})" class="cta-button">Get Started</button>
        </div>
    </div>
    """
    
    st.markdown(hero_html, unsafe_allow_html=True)

def main():
    # Add theme toggle in sidebar
    with st.sidebar:
        st.title("Settings")
        theme_options = ["Dark Mode", "Light Mode"]
        selected_theme = st.radio("Choose Theme:", theme_options, 
                                index=0 if st.session_state.theme == 'dark' else 1)
        
        # Update session state based on selection
        st.session_state.theme = 'dark' if selected_theme == "Dark Mode" else 'light'
        
        if st.session_state.show_landing:
            if st.button("Skip Intro"):
                st.session_state.show_landing = False
                st.rerun()
        else:
            if st.button("Show Landing Page"):
                st.session_state.show_landing = True
                st.rerun()
        
        st.divider()
        
        # Help section
        st.subheader("ℹ️ How to use")
        st.markdown("""
        1. Upload your MP3 guitar recording
        2. Click "Convert to Guitar Tab"
        3. View and download the generated tab
        """)
        
        st.markdown("""
        Best results with:
        - Clean guitar recordings
        - Single instrument tracks
        - Well-defined notes
        """)
        
        st.divider()
        
        # About section
        st.subheader("🧠 How it works")
        tooltip_pitch = "Uses machine learning to analyze audio and detect musical notes and their timing, converting audio to structured MIDI data."
        tooltip_tayuya = "Processes MIDI data to generate guitar-specific tablature notation, determining string and fret positions."
        
        pitch_text = add_tooltip("Basic Pitch", tooltip_pitch)
        tayuya_text = add_tooltip("Tayuya", tooltip_tayuya)
        
        st.markdown(f"""
        This app uses {pitch_text} for audio-to-MIDI conversion and {tayuya_text} for MIDI-to-tablature rendering.
        """, unsafe_allow_html=True)
    
    # Apply the appropriate CSS based on theme choice
    if st.session_state.theme == 'dark':
        st.markdown(dark_css, unsafe_allow_html=True)
    else:
        st.markdown(light_css, unsafe_allow_html=True)
    
    # Custom CSS to make the main content area wider
    st.markdown("""
    <style>
    .block-container {
        max-width: 95% !important;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display landing page or main app based on state
    if st.session_state.show_landing:
        render_hero_section()
        
        # Add a marker for the "Get Started" scroll target
        st.markdown('<div id="get-started"></div>', unsafe_allow_html=True)
    
    # Always show the main app content after the hero section (or immediately if hero is hidden)
    st.title("🎸 MP3 to Guitar Tab Converter")
    
    st.write("""
    Transform your guitar recordings into easy-to-read tablature. Perfect for documenting your riffs, 
    learning songs by ear, or sharing your musical ideas.
    """)
    
    # File uploader with custom styling
    file_uploader_label = "Choose an MP3 file"
    uploaded_file = st.file_uploader(file_uploader_label, type=['mp3'])
    
    if uploaded_file is not None:
        # Show the file information with a remove option
        file_size_kb = len(uploaded_file.getvalue()) / 1024
        
        # Custom CSS for file display
        file_html = f"""
        <div style="display: flex; align-items: center; margin-bottom: 15px; background-color: {'#121212' if st.session_state.theme == 'dark' else '#f8f9fa'}; padding: 10px; border-radius: 5px; border: 1px solid {'#333' if st.session_state.theme == 'dark' else '#dee2e6'};">
            <div style="margin-right: 10px;">
                <i class="fas fa-file-audio" style="color: #ff4d4d;"></i>
            </div>
            <div style="flex-grow: 1;">
                <div style="font-weight: 500; color: {'#e0e0e0' if st.session_state.theme == 'dark' else '#333333'};">{uploaded_file.name}</div>
                <div style="font-size: 12px; color: {'#999' if st.session_state.theme == 'dark' else '#666'};">{file_size_kb:.1f} KB</div>
            </div>
        </div>
        """
        st.markdown(file_html, unsafe_allow_html=True)
        
        # Main content area
        col1, col2 = st.columns([1, 2], gap="large")
        
        with col1:
            # Audio preview section
            st.subheader("Audio Preview")
            st.audio(uploaded_file, format="audio/mp3")
            st.caption("Note: Processing large audio files may take longer")
            
            # Convert button with full width and better styling
            convert_button = st.button("Convert to Guitar Tab", use_container_width=True, type="primary")
        
        if convert_button:
            try:
                # Add a progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Process in stages
                status_text.info("Starting conversion process...")
                progress_bar.progress(10)
                time.sleep(0.5)
                
                status_text.info("Converting audio to MIDI...")
                progress_bar.progress(30)
                
                results = process_audio(uploaded_file)
                
                status_text.info("Processing tablature...")
                progress_bar.progress(70)
                time.sleep(0.5)
                
                progress_bar.progress(100)
                status_text.empty()
                
                if results and "tabs" in results and len(results["tabs"].strip()) > 0:
                    st.success("🎉 Conversion successful! Guitar tab has been generated.")
                    
                    # Download buttons with improved styling
                    col1, col2 = st.columns(2)
                    with col1:
                        # MIDI Download button
                        midi_download = get_download_link(
                            results["midi_bytes"], 
                            results["midi_filename"],
                            "⬇️ Download MIDI File",
                            "download-midi"
                        )
                        st.markdown(midi_download, unsafe_allow_html=True)
                    
                    with col2:
                        # Tab Download button
                        tab_download = get_download_link(
                            results["tabs"].encode(),
                            results["midi_filename"].replace(".mid", ".txt"),
                            "⬇️ Download Tab as Text File",
                            ""
                        )
                        st.markdown(tab_download, unsafe_allow_html=True)
                    
                    # Display the tab with a better heading
                    st.subheader("Guitar Tablature")
                    
                    # Add tab explanation with better styling
                    st.markdown("""
                    <div style="margin-bottom: 1rem; padding: 10px; background-color: rgba(255, 77, 77, 0.1); border-radius: 5px; border-left: 3px solid #ff4d4d;">
                        <small>
                            <strong>How to read:</strong> Each line represents a guitar string (e, B, G, D, A, E from top to bottom).
                            Numbers indicate which fret to press on that string.
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create a full-width container for the tab
                    tab_container = st.container()
                    with tab_container:
                        formatted_tab = format_tab_for_display(results["tabs"])
                        # Use a monospace pre tag for better rendering with proper HTML escaping
                        st.markdown(f'<div class="tab-container"><pre>{html.escape(formatted_tab)}</pre></div>', unsafe_allow_html=True)
                else:
                    st.error("Failed to generate guitar tab. The audio may not contain distinct notes or may be too complex.")
                    st.info("Try with a cleaner recording or a simpler melody for better results.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please try with a different audio file or ensure your MP3 is not corrupted.")
    
    st.divider()
    
    # App footer with version
    footer_html = f"""
    <div class="app-footer">
        Created with ❤️ using Python, Basic Pitch, and Tayuya | v{st.session_state.version}
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
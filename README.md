<p align="center">
  <img src="assets/images/player-piano-5.png" alt="Tab Gener8or Logo" width="100%">
</p>

# Tab Gener8or: MP3 ➔ Guitar Tabs & MIDI 🎸➡️📄

Got a riff stuck in your head or need to decode a guitar part from an MP3? **Tab Gener8or** is a tool for that.

Using Spotify Basic Pitch for note detection and Tayuya for tab-generation, Tab Gener8or analyzes recordings and generates corresponding tablature (tabs) and MIDI files. Useful for:

-   **Capturing Ideas:** Nail down riffs before they vanish.
-   **Learning by Ear:** Get a starting point for transcribing.
-   **Sharing Parts:** Pass along guitar ideas in a standard format.
-   **AI Music Exploration:** See how machines interpret audio.

## How's it Work? ✨

Tab Gener8or links together two key open-source libraries:

1.  **[Basic Pitch](https://github.com/spotify/basic-pitch)** (from Spotify): Analyzes the audio, detects notes and timing, and outputs a MIDI file. It's the digital ear.
2.  **[Tayuya](https://github.com/vipul-sharma20/tayuya)**: Takes that MIDI data and translates it into playable guitar tablature, estimating string and fret positions. It's the digital fingers.

## Getting Started Locally

Want to run it yourself? Here's the setup:

1.  **Clone the Repo:**
    Get the code onto your local machine.
    ```bash
    git clone https://github.com/mgd1984/tab-gener8or.git
    cd tab-gener8or
    ```

2.  **Set Up a Virtual Environment:**
    Keep dependencies tidy. Create and activate a virtual environment.
    ```bash
    # Create (use python3 if needed)
    python -m venv venv
    # Activate
    # macOS/Linux: 
    source venv/bin/activate
    # Windows:
    # venv\Scripts\activate
    ```
    *(Your prompt should now start with `(venv)`)*

3.  **Install Dependencies:**
    Inside the active `(venv)`, install the required libraries:
    ```bash
    pip install -r requirements.txt
    ```
    *(This might take a moment, especially downloading TensorFlow for Basic Pitch).* 

4.  **Run the App:**
    With the `(venv)` still active, launch the Streamlit interface:
    ```bash
    streamlit run app.py
    ```
    This should open the app in your default web browser (usually `http://localhost:8501`).

5.  **Generate Tabs:**
    -   Upload an MP3 with guitar audio.
    -   Hit "Convert to Guitar Tab".
    -   Let the AI process.
    -   Check out the generated tab and download the `.txt` or `.mid` file.

## Tips for Better Results & Tinkering 🛠️

-   **Input Quality Matters:** Cleaner audio (less noise/effects, isolated guitar) generally yields better note detection.
-   **Single Instrument:** Basic Pitch works best analyzing one instrument at a time. Feed it isolated guitar tracks if possible.
-   **Complexity Limits:** Very fast, distorted, or complex polyphonic passages can challenge the AI. Clearer tones and simpler lines often transcribe more accurately.
-   **Command Line Option:** If you prefer, use `main.py` directly (ensure `venv` is active):
    ```bash
    python main.py path/to/your/audio.mp3
    ```
    (Outputs `.mid` and `.txt` files in the same directory).
-   **Code Dive:**
    -   `app.py`: The Streamlit UI, audio processing (`process_audio`), tab formatting (`format_tab_for_display`).
    -   `main.py`: The script for command-line use.
    -   `requirements.txt`: The list of Python dependencies.

## Project Structure

```
tab-gener8or/
├── app.py                  # Main Streamlit application UI and logic
├── main.py                 # Command-line interface script
├── requirements.txt        # Project dependencies
├── runtime.txt             # Python version target for deployment
├── Dockerfile              # For building a Docker container
├── Procfile                # For Heroku deployment
├── .slugignore             # Files to ignore for Heroku slugs
├── .gitignore              # Files for Git to ignore
├── assets/                 # Static assets (images, etc.)
│   └── images/
└── venv/                   # Virtual environment directory (if created)
```

## Deployment Notes ☁️

-   **Streamlit Cloud:** Convenient for sharing. Push to GitHub, connect the repo. *Heads-up: As of this writing, Streamlit Cloud's default Python (3.12) conflicts with `basic-pitch==0.4.0`'s dependencies. Deployment requires ensuring the environment uses Python 3.9 or 3.10.*
-   **Docker:** `Dockerfile` provided for containerized deployment if you need more environment control.

## Contributing

Ideas and improvements welcome via Pull Requests.

## License

MIT License.

## Acknowledgements 🙏

Built using these great open-source projects:

-   [Basic Pitch](https://github.com/spotify/basic-pitch) by Spotify
-   [Tayuya](https://github.com/vipul-sharma20/tayuya) by @vipul-sharma20
-   [Streamlit](https://streamlit.io)


# 🎶 Gesture-Controlled Music Band Simulator

A Python-based, voice-controlled, and gesture-enabled music loop simulator. This application lets you record, play, and mix instrument loops using voice inputs and hand gestures. Powered by **Pygame**, **MediaPipe**, **OpenCV**, and **PyDub**.

## download link -> https://drive.google.com/file/d/1lMYTiUJugiZeZNNNuNoYh_3GTwTQy3TN/view?usp=drive_link
---

## ✨ Key Features

- **🎹 Multiple Instruments**: Record loops for Piano, Drums, Guitar, and Flute.
- **🎤 Vocal Recording**: Record your voice for up to 30 seconds.
- **🧠 Gesture Control**: Control the application entirely using hand tracking (MediaPipe + OpenCV).
- **🎛️ Hybrid Input**: Manual button control using the mouse or pinch gestures.
- **🔁 Dynamic Looping**: Support for up to 16 notes per instrument sequence.
- **🎧 Auto-Mixing**: Mix your final song from multiple loops (automatically applies fade-in/fade-out).
- **🗑️ Easy Management**: Easily delete, pause, and replay instrument tracks.

---

## 🖐️ Gesture Controls

Control the application without touching your mouse! 
- **Move Cursor**: The cursor follows the movement of your **index finger**.
- **Click**: Perform an **Index + Thumb pinch** (bring your thumb close to your index finger) to simulate a left-click.

> **💡 Tip:** Gestures work best with your right hand. Use the `ESC` key to quit the gesture tracking window.

---

## 🧩 Tech Stack

- `pygame` - GUI rendering and sound playback
- `mediapipe` - Real-time hand tracking
- `opencv-python` - Webcam feed and gesture recognition
- `pyautogui` - Simulating mouse control
- `pydub` - Audio mixing and looping
- `sounddevice` + `scipy` - Voice recording
- `FFmpeg` - Backend engine used by PyDub for processing audio

---

## 🚀 Installation & Setup

You can run this project either from the source code or by using the standalone Windows executable.

### Option 1: Running from Source Code

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/voice-band-simulator.git
   cd voice-band-simulator
   ```

2. **Install dependencies:**
   Ensure you have Python installed, then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install FFmpeg (Required for audio export):**
   - Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Add the `bin` folder path (where `ffmpeg.exe` is located) to your system's Environment Variables (`PATH`).
   - Restart your terminal.

4. **Run the App:**
   ```bash
   python main.py
   ```

### Option 2: Standalone Windows Executable

If you downloaded the packaged version (the `play game (main)` folder):
1. **Launch the Application**: Simply double-click `main.exe`.
2. **Permissions**: Allow webcam and microphone access when prompted.
3. *No Python installation or internet connection is required!*

> ⚠️ **Note for Executable version:** Do not delete or rename the included folders (`assets`, `sounds`, `instruments`, `final`, `ffmpeg`), as they are required for the game to function properly.

---

## 📁 Folder Structure

```text
📦voice-band-simulator/
 ┣ 📂assets/          # UI backgrounds and instrument icons
 ┣ 📂sounds/          # Preloaded instrument note sounds (0-9)
 ┣ 📂instruments/     # Saved instrument loops (.wav files)
 ┣ 📂final/           # Final mixed songs
 ┣ 📂ffmpeg/          # Audio processing backend (if packaged)
 ┣ 📜gesture.py       # Hand gesture control script
 ┣ 📜main.py          # Main Pygame GUI and audio logic
 ┗ 📜README.md        # Project documentation
```

---

## ⚠️ Troubleshooting

- **Camera doesn't open:** Make sure no other application (like Zoom or Teams) is using the webcam. Try running the app as an administrator.
- **No sound:** Check your system volume and default audio output device.
- **Cannot save loops:** Ensure the application has write permissions for the `instruments/` and `final/` folders.

---

## 👨‍💻 Developed By

**Siddhant Saxena**  
B.Tech CSE, JIIT Noida (Sector 62)  
**Project:** Gesture-Controlled Voice Band Simulator  
**For:** Summer Internship 2025

![Screenshot 1](screenshots/s%20(1).png)
![Screenshot 2](screenshots/s%20(2).png)
![Screenshot 3](screenshots/s%20(3).png)
![Screenshot 4](screenshots/s%20(4).png)
![Screenshot 5](screenshots/s%20(5).png)
![Screenshot 6](screenshots/s%20(6).png)

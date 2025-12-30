# 🎶 Music Band Simulator with Gesture Control

A Python-based music loop simulator that lets you record, play, and mix instrument loops using voice and gesture inputs. Powered by **Pygame**, **MediaPipe**, **OpenCV**, and **PyDub**.

dowbnload link -> https://drive.google.com/file/d/1lMYTiUJugiZeZNNNuNoYh_3GTwTQy3TN/view?usp=drive_link

## ✨ Features

- 🎹 Record instrument loops (Piano, Drums, Guitar, Flute, Vocals)
- 🎤 Vocal recording (30s max duration)
- 🧠 Gesture control with hand tracking (MediaPipe + OpenCV)
- 🎛 Manual button control using mouse or gestures
- 🔁 Looping support with up to 16 notes per instrument
- 🎧 Mix final song from multiple loops (with fade in/out)
- 🗑 Easily delete, pause, and replay instrument tracks

---

## 📷 Gesture Control

- **Index + Thumb pinch** → Simulates mouse click  
- Cursor follows your **index finger**
- OpenCV window on **left**, Pygame GUI on **right**

---

## 🧩 Tech Stack

- `pygame` - GUI and sound playback
- `mediapipe` - Hand tracking
- `opencv-python` - Webcam + gestures
- `pyautogui` - Simulate mouse control
- `pydub` - Audio mixing and looping
- `sounddevice` + `scipy` - Voice recording
- `FFmpeg ` - Backend used by PyDub to process audio

---

## 🚀 Installation

1. Clone the repo:

```bash
git clone https://github.com/your-username/voice-band-simulator.git
cd voice-band-simulator
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## 🎬 FFmpeg (Required for audio export)
- Download FFmpeg: https://ffmpeg.org/download.html

- Add it to your system PATH so pydub can use it.

- On Windows:
    Download the ZIP for Windows from FFmpeg builds

- Extract and copy the bin folder path (where ffmpeg.exe is)

- Add it to Environment Variables → System PATH

- Restart your terminal or IDE


> 📝 Make sure your environment has access to a webcam and microphone.

---

## 🧪 Run the App

```bash
python main.py
```

---

## 📁 Folder Structure

```
📦voice-band-simulator/
 ┣ 📂assets/          # Background and instrument images
 ┣ 📂sounds/          # Instrument note sounds (0-9 per instrument)
 ┣ 📂instruments/     # Saved instrument loop .wav files
 ┣ 📂final/           # Final mixed song
 ┣ 📜gesture.py       # Hand gesture control script
 ┣ 📜main.py          # Main Pygame GUI and audio logic
 ┗ 📜README.md
```

---

## 🔧 Notes

* All loops are auto-trimmed or looped to exactly **30 seconds**
* Gestures only work with **one hand** (right-hand index + thumb)
* Pygame and OpenCV windows are placed **side-by-side** for optimal experience (1920×1200 recommended)

---
![Screenshot 1](screenshots/s%20(1).png)
![Screenshot 2](screenshots/s%20(2).png)
![Screenshot 3](screenshots/s%20(3).png)
![Screenshot 4](screenshots/s%20(4).png)
![Screenshot 5](screenshots/s%20(5).png)
![Screenshot 6](screenshots/s%20(6).png)

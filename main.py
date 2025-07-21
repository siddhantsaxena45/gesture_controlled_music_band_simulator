import pygame
import sys
import threading
import sounddevice as sd
from pydub import AudioSegment
from gesture import gesture_mouse_control
import pygame
import time
import os
from pydub.utils import which
from pydub import AudioSegment

# Tell pydub to use the ffmpeg in the bundled folder


os.environ['SDL_VIDEO_WINDOW_POS'] = '900,300'

pygame.init()

current_screen = "menu"
selected_instrument = None
is_recording = False
recording_thread = None

status_message = "Waiting for command..."

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Voice Band Simulator")

if getattr(sys, '_MEIPASS', False):
    base_dir = sys._MEIPASS  
else:
    base_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
    
ffmpeg_path = os.path.join(base_dir, "ffmpeg", "bin", "ffmpeg.exe")
AudioSegment.converter = ffmpeg_path

asset_dir = os.path.join(base_dir, "assets")
instruments_dir = os.path.join(base_dir, "instruments")
final_dir = os.path.join(base_dir, "final")
sounds_dir = os.path.join(base_dir, "sounds")

background_file = os.path.join(asset_dir, "background.jpg")
background_image = pygame.image.load(background_file)
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))


font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 22)

class Button:
    """Custom button for GUI with shadow and hover effects."""
    def __init__(self, x, y, w, h, text, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.color = (10, 40, 100)
        self.text_color = (255, 255, 255)
        self.border_color = (255, 255, 255)
        self.shadow_offset = 4
        self.radius = 12

    def draw(self):
        """Draw button with shadow and label."""
        shadow_rect = self.rect.copy()
        shadow_rect.x += self.shadow_offset
        shadow_rect.y += self.shadow_offset
        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=self.radius)

        pygame.draw.rect(screen, self.color, self.rect, border_radius=self.radius)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=self.radius)

        label = small_font.render(self.text, True, self.text_color)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def handle_event(self, event):
        """Execute action if button is clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.action:
                threading.Thread(target=self.action).start()

def reset_mixer():
    """Stops and re-initializes the mixer safely."""
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        time.sleep(0.3)
    pygame.mixer.init()

pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN])

def remove_wav_file(filepath, retries=5, delay=0.5):
    """Try to remove a file, retrying if it's still in use."""
    stop_audio()  # 🔥 Force stop playback
    for _ in range(retries):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
            return True
        except PermissionError:
            time.sleep(delay)
    update_status(f"Could not delete {os.path.basename(filepath)}. Still in use.")
    return False



def ensure_dirs():
    os.makedirs(instruments_dir, exist_ok=True)
    os.makedirs(final_dir, exist_ok=True)

def fade_audio(audio):
    return audio.fade_in(2000).fade_out(2000)

def cut_or_loop(audio, duration):
    if len(audio) > duration:
        return audio[:duration]
    else:
        loops = duration // len(audio)
        remainder = duration % len(audio)
        return (audio * loops) + audio[:remainder]


def record_vocals(filename=os.path.join(instruments_dir, "vocals_loop.wav")):
    global is_recording
    is_recording = True

    update_status("Recording vocals (max 30s)...")

    samplerate = 44100  # CD quality
    channels = 1
    duration = 30  # seconds

    try:
        # Start recording for 30s in background
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=channels, dtype='int16')
        start_time = time.time()

        while is_recording and (time.time() - start_time) < duration:
            time.sleep(0.1)

        # Stop recording (if not already auto-finished)
        sd.stop()

        # Export to WAV
        temp_wav_path = os.path.join(instruments_dir, "temp_vocals.wav")
        from scipy.io.wavfile import write as wav_write
        wav_write(temp_wav_path, samplerate, recording)

        # Always load it with pydub and trim or pad
        audio = AudioSegment.from_file(temp_wav_path)
        audio = cut_or_loop(audio, 30_000)  # always make it 30s
        audio.export(filename, format="wav")

        os.remove(temp_wav_path)
        update_status(f"Saved 30s vocals to {filename}")

    except Exception as e:
        update_status(f"Recording error: {e}")


def stop_recording():
    global is_recording

    if is_recording:
        is_recording = False
        update_status("Stopped recording.")
    else:
        update_status("Not recording yet.")



note_lock = threading.Lock()  # Declare this at the top of your file (only once)

def process_notes(instrument, notes):
    with note_lock:  # 🛡 Prevent multiple threads from writing the same file
        ensure_dirs()
        files = []

        # 🔹 Validate notes
        for note in notes:
            note_file = os.path.join(sounds_dir, instrument, f"{note}.wav")
            if not os.path.exists(note_file):
                update_status(f"Note {note} not found for {instrument}. Loop not saved.")
                return

        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            time.sleep(0.3)  # ⏳ Ensure file is free

        for note in notes:
            note_file = os.path.join(sounds_dir, instrument, f"{note}.wav")
            files.append(AudioSegment.from_file(note_file))

        combined = sum(files, AudioSegment.empty())
        output_file = os.path.join(instruments_dir, f"{instrument}_loop.wav")

        # 🔧 Make sure the file is deletable
        remove_wav_file(output_file)

        try:
            combined.export(output_file, format='wav')
            update_status(f"Saved instrument loop: {output_file}")
        except PermissionError:
            update_status(f"Could not write to {output_file}. It may still be in use.")



def delete_final_song():
    """Delete the final mixed song file if it exists."""
    file = os.path.join(final_dir, "final_song.wav")
    stop_audio()  # Safely stop any playback
    if os.path.exists(file):
        remove_wav_file(file)
        update_status("Final song deleted.")
    else:
        update_status("No final song to delete.")


def select_instrument(inst):
    global selected_instrument, current_screen
    selected_instrument = inst
    current_screen = inst
    note_sequence.clear() 
    update_status(f"Switched to {inst}")

def make_song_cmd():
    instrument_loops = [f for f in os.listdir(instruments_dir) if f.endswith(".wav") and not f.startswith("vocals")]
    
    if not instrument_loops:
        update_status("No instrument loops available. Cannot mix song.")
        return

    file_path = os.path.join(final_dir, "final_song.wav")
    if os.path.exists(file_path):
        update_status("Final song already exists. Delete it first.")
        return

    update_status("Mixing song...")
    reset_mixer()
    create_final_song()
    status_message = "Song mixed!"
    update_status(status_message)


def play_song_cmd():
    global status_message
    file = os.path.join(final_dir, "final_song.wav")

    if os.path.exists(file):
        status_message = "Playing final song..."
        update_status(status_message)
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
    else:
        status_message = "Final song not found."
        update_status(status_message)



def set_menu():
    """Switch back to main menu."""
    global current_screen, status_message
    current_screen = "menu"
    status_message = "Waiting for command..."




def create_final_song(output_file=os.path.join(final_dir, "final_song.wav"), duration_ms=30_000):
    """Mix all instrument loops and optional vocals into one final song (30s, no overwrite)."""
    ensure_dirs()
    
    vocals_file = os.path.join(instruments_dir, "vocals_loop.wav")

    # If file already exists, prevent overwrite
    if os.path.exists(output_file):
        update_status("Final song already exists. Please delete it first.")
        return

    # Stop mixer safely
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        time.sleep(0.5)
    pygame.mixer.init()

    # Create silent base
    final_mix = AudioSegment.silent(duration=duration_ms)

    for filename in os.listdir(instruments_dir):
        if filename.endswith(".wav"):
            filepath = os.path.join(instruments_dir, filename)
            try:
                audio = AudioSegment.from_file(filepath)
                audio = audio - 6  # reduce volume a bit
                processed = fade_audio(cut_or_loop(audio, duration_ms))
                final_mix = final_mix.overlay(processed)
            except Exception as e:
                update_status(f"Error loading {filename}: {e}")

    # Add vocals if present
    if os.path.exists(vocals_file):
        try:
            vocals = AudioSegment.from_file(vocals_file)
            vocals = vocals + 12  # boost vocal volume
            aligned_vocals = fade_audio(cut_or_loop(vocals, duration_ms))
            final_mix = final_mix.overlay(aligned_vocals)
        except Exception as e:
            update_status(f"Error loading vocals: {e}")

    try:
        final_mix.export(output_file, format="wav")
        update_status(f"Final song exported to {output_file}")
    except PermissionError:
        update_status(f"Cannot save final song. File may still be in use.")
    
    return output_file


def pause_song_cmd():
    """Pause final song safely."""
    global status_message

    if not pygame.mixer.get_init():
        update_status("Nothing is playing. Can't pause.")
        return

    if not pygame.mixer.music.get_busy():
        update_status("Final song is not playing.")
        return

    status_message = "Pausing final song..."
    pause_final_song()
    status_message = "Paused"
    update_status(status_message)



def play_instr_cmd(instr):
    global status_message
    filename = os.path.join(instruments_dir, f"{instr}_loop.wav")

    if os.path.exists(filename):
        status_message = f"Playing {instr} loop..."
        play_file(filename)
    else:
        status_message = f"{instr.capitalize()} loop not found."
    update_status(status_message)



def pause_instr_cmd(instr):
    """Pause a single instrument's loop."""
    global status_message
    status_message = f"Pausing {instr} loop..."
    pause_instrument()
    status_message = "Paused"

def play_file(filename):
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play(-1) 

def pause_playback():
    """Pause currently playing audio."""
    pygame.mixer.music.pause()
    pygame.mixer.music.stop()

def play_instrument(instr):
    """Play the previously recorded loop for this instrument."""
    
    filename = os.path.join(instruments_dir, f"{instr}_loop.wav")

    if os.path.exists(filename):
        play_file(filename)
    else:
        update_status(f"Instrument file {filename} not found.")

def pause_instrument():
    """Pause currently playing instrument loop."""
    pause_playback()
    pygame.mixer.music.stop()


def pause_final_song():
    """Pause the final song."""
    pause_playback()
    pygame.mixer.music.stop()


def play_final_song(filename):
    """Play back the final song."""
    play_file(filename)
    pygame.mixer.music.stop()

def cut_or_loop(audio, duration_ms=30_000):
    """Repeat or cut audio to exactly `duration_ms` milliseconds."""
    if len(audio) >= duration_ms:
        return audio[:duration_ms]
    else:
        
        times = (duration_ms // len(audio)) + 1
        looped = AudioSegment.empty()
        for i in range(times):
            looped += audio
        return looped[:duration_ms]
    
def fade_audio(audio, fade_duration_ms=2000):
    """Add fade in and fade out to audio."""
    return audio.fade_in(fade_duration_ms).fade_out(fade_duration_ms)

def align_vocal_to_instrument(vocal, instrument):
    """Make sure vocal is the same length as the instrument by looping or cutting."""
    if len(vocal) < len(instrument):
       
        return cut_or_loop(vocal, len(instrument))
    else:
        
        return vocal[:len(instrument)]


def create_menu_buttons():
    """Create main menu button set."""
    button_width, button_height = 200, 50
    padding = 20
    col_gap = 60
    total_columns = 2
    
    instruments = ["piano", "drum", "guitar", "vocals", "flute"]
    actions = [(f"Select {inst.capitalize()}", lambda inst=inst: select_instrument(inst)) for inst in instruments]
    actions += [("Make Final Song", make_song_cmd),
                ("Play Final Song", play_song_cmd),
                ("Pause Final Song", pause_song_cmd),
                ("Delete Final Song", delete_final_song)]

    total = len(actions)
    num_rows = (total + 1) // 2
    total_height = num_rows * button_height + (num_rows - 1) * padding
    start_y = (HEIGHT - total_height) // 2

    total_width = total_columns * button_width + (total_columns - 1) * col_gap
    start_x = (WIDTH - total_width) // 2

    buttons = []

    for i, (label, action) in enumerate(actions):
        col = i % 2
        row = i // 2
        x = start_x + col * (button_width + col_gap)
        y = start_y + row * (button_height + padding)
        button = Button(x, y, button_width, button_height, label, action)
        buttons.append(button)

    return buttons
def update_status(msg):
    global status_message
    status_message = msg

def create_instrument_buttons():
    button_width, button_height = 200, 50
    center_x = WIDTH // 2 - button_width // 2
    buttons = []

    def record_action():
        global recording_thread
        if selected_instrument == "vocals":
            if not is_recording:
                recording_thread = threading.Thread(target=record_vocals)
                recording_thread.start()
            else:
                update_status("Already recording.")
        else:
            loop_file = os.path.join(instruments_dir, f"{selected_instrument}_loop.wav")
            if os.path.exists(loop_file):
                update_status(f"{selected_instrument.capitalize()} loop already exists. Delete it first.")
                return

            if note_sequence:
                process_notes(selected_instrument, note_sequence)
                update_status(f"{selected_instrument.capitalize()} loop saved.")
            else:
                update_status("No notes selected.")


    # 🔹 Always show Delete
    buttons.append(Button(center_x, 210, button_width, button_height, "Delete", delete_instr_loop))
    # 🔹 Only show Save for non-vocals
    if selected_instrument != "vocals":
        buttons.append(Button(center_x, 280, button_width, button_height, "Save", record_action))
    else:
        buttons.append(Button(center_x, 130, button_width, button_height, "Stop", stop_recording))
        
        buttons.append(Button(center_x, 280, button_width, button_height, "Record", record_action))

    # 🔹 Common buttons
    buttons.extend([
        Button(center_x, 350, button_width, button_height, "Play", lambda: (
            play_instr_cmd(selected_instrument) 
            if os.path.exists(os.path.join(instruments_dir, f"{selected_instrument}_loop.wav")) 
            else update_status("No loop to play.")
        )),
        Button(center_x, 420, button_width, button_height, "Pause", lambda: (
            pause_instr_cmd(selected_instrument) 
            if os.path.exists(os.path.join(instruments_dir, f"{selected_instrument}_loop.wav")) 
            else update_status("No loop to pause.")
        )),
        Button(center_x, 490, button_width, button_height, "Back", set_menu),
    ])

    # 🔹 Add note buttons (0–9) only for instruments
   
    if selected_instrument != "vocals":
        note_start_y = 100
        note_button_width = 50
        note_button_height = 40
        note_spacing_x = 60
        total_columns = 5
        total_width = total_columns * note_button_width + (total_columns - 1) * (note_spacing_x - note_button_width)
        start_x = WIDTH // 2 - total_width // 2

        for i in range(10):
            col = i % total_columns
            row = i // total_columns
            x = start_x + col * note_spacing_x
            y = note_start_y + row * 50
            buttons.append(Button(x, y, note_button_width, note_button_height, str(i), lambda n=str(i): add_note_and_generate(n)))


    return buttons

note_sequence = []
def add_note_and_generate(note):
    global note_sequence

    note_file = os.path.join(sounds_dir, selected_instrument, f"{note}.wav")

    if not os.path.exists(note_file):
        update_status(f"Note {note} not found for {selected_instrument}. Skipped.")
        return

    if len(note_sequence) >= 16:
        update_status("Maximum 16 notes allowed.")
        return

    note_sequence.append(note)
    update_status(f"Note {note} added.")


def stop_audio():
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        time.sleep(0.1)


def delete_instr_loop():
    """Delete the loop file of the selected instrument."""
    note_sequence.clear()

    global status_message

    if selected_instrument is None:
        status_message = "No instrument selected."
        return

    file_path = os.path.join(instruments_dir, f"{selected_instrument}_loop.wav")

    stop_audio()  # 🔹 Stop playback before delete

    if os.path.exists(file_path):
        remove_wav_file(file_path)
        status_message = f"{selected_instrument.capitalize()} loop deleted."
        update_status(status_message)
    else:
        status_message = f"No loop found for {selected_instrument}."
        update_status(status_message)

def main():
    """Main GUI Loop with voice and button control."""
    gesture_control_flag = {"active": True}
    gesture_thread = threading.Thread(target=gesture_mouse_control, args=(gesture_control_flag,), daemon=True)
    gesture_thread.start()
    global  current_screen, status_message
    

    clock = pygame.time.Clock()
    menu_buttons = create_menu_buttons()

    instrument_backgrounds = {
    "piano": pygame.transform.scale(
        pygame.image.load(os.path.join(asset_dir, "piano.png")),
        (WIDTH, HEIGHT)
    ),
    "drum": pygame.transform.scale(
        pygame.image.load(os.path.join(asset_dir, "drum.png")),
        (WIDTH, HEIGHT)
    ),
    "guitar": pygame.transform.scale(
        pygame.image.load(os.path.join(asset_dir, "guitar.png")),
        (WIDTH, HEIGHT)
    ),
    "vocals": pygame.transform.scale(
        pygame.image.load(os.path.join(asset_dir, "mic.png")),
        (WIDTH, HEIGHT)
    ),
    "flute": pygame.transform.scale(
        pygame.image.load(os.path.join(asset_dir, "flute.png")),
        (WIDTH, HEIGHT)
    )
}


    running = True
    while running:
        clock.tick(30)
        screen.blit(background_image, (0, 0))

        if current_screen == "menu":
            for button in menu_buttons:
                button.draw()
        else:
            bg = instrument_backgrounds.get(current_screen)
            if bg:
                screen.blit(bg, (0, 0))
            title = font.render(f"{current_screen.capitalize()} Instrument", True, (255, 255, 255))
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

            for button in create_instrument_buttons():
                button.draw()

        status = font.render(status_message, True, (255, 255, 0))
        screen.blit(status, (50, HEIGHT - 40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if current_screen == "menu":
                for button in menu_buttons:
                    button.handle_event(event)
            else:
                for button in create_instrument_buttons():
                    button.handle_event(event)
        
       
        pygame.display.flip()

    pygame.quit()
    gesture_control_flag["active"] = False

    sys.exit()

if __name__ == "__main__":
    main()

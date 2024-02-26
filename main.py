import os
import shutil
import numpy as np
from pydub import AudioSegment
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from pytube import YouTube
from moviepy.editor import AudioFileClip
import soundfile as sf
from pedalboard import Pedalboard, Reverb
from tkinter import filedialog, ttk
import tkinter as tk
import threading
import time


class SoundManipulator:
    def apply_effects(self, input_file: str, output_file: str = None, period: int = 150):
        output_text.set("Applying 8d effect...")
        period = abs(period)
        audio = AudioSegment.from_file(input_file, format='mp3')
        audio += AudioSegment.silent(duration=150)
        file_info = MP3(input_file, ID3=EasyID3)
        pan = 0.9 * np.sin(np.linspace(0, 2 * np.pi, period))
        eight_d = sum(chunk.pan(pan[i % period]) for i, chunk in enumerate(audio[::100]) if len(chunk) >= 100)

        if output_file is None:
            output_file = input_file.rsplit(".", 1)[0] + ".wav"

        output_text.set("Slowing down the audio & adding reverb...")
        eight_d.export(output_file, format='wav', bitrate=str(file_info.info.bitrate), tags=dict(file_info))
        audio, sample_rate = sf.read(output_file)
        sample_rate = int(sample_rate * 0.92)  # Slow down the sample rate
        pedalboard = Pedalboard([Reverb(room_size=0.75, damping=0.5, wet_level=0.08, dry_level=0.2)])
        effected_audio = pedalboard(audio, sample_rate)
        sf.write(output_file, effected_audio, sample_rate)
        return output_file

    def process_task(self, url):
        try:
            file = self.download(url)
            if not file:
                output_text.set("Failed to download file. Please check the URL.")
                return
            global output_file
            output_file = self.apply_effects(file)
            os.remove(file)
            output_dir = os.path.join(os.getcwd(), "output")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            output_file = shutil.copyfile(output_file, os.path.join(output_dir, os.path.basename(output_file)))
            shutil.rmtree("downloads", ignore_errors=True)
            output_text.set("Finished!")
            output_text.set("Processing completed successfully!")
            open_button.grid(row=4, column=0, padx=10, pady=10)
        except Exception as e:
            output_text.set(f"Error: {str(e)}")

    def download(self, url):
        yt = YouTube(url)
        title = yt.title
        author = yt.author
        output_text.set(f"Downloading {title}...")
        video = yt.streams.filter(only_audio=True).first()
        mp4_file = self.download_file(video, output_path="downloads")
        mp3_file = self.convert_to_mp3(mp4_file)
        os.remove(mp4_file)
        output_text.set("Metadata set.")
        return mp3_file

    @staticmethod
    def download_file(stream, output_path):
        filename = stream.download(output_path=output_path)
        return filename

    @staticmethod
    def convert_to_mp3(input_file):
        output_file = os.path.splitext(input_file)[0] + '.mp3'
        audio = AudioFileClip(input_file)
        audio.write_audiofile(output_file)
        audio.close()
        return output_file

def start_process():
    url = url_entry.get()
    open_button.grid_remove()
    if not url:
        output_text.set("Please enter a URL.")
        return

    output_text.set("") 

    sound_manipulator = SoundManipulator()
    threading.Thread(target=sound_manipulator.process_task, args=(url,)).start()

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])
    url_entry.delete(0, tk.END)
    url_entry.insert(0, file_path)

def open_result():
    output_dir = os.path.join(os.getcwd(), "output")
    os.startfile(os.path.join(output_dir, output_file))

# GUI
root = tk.Tk()
root.title("Sound Manipulation Application")

frame = tk.Frame(root, padx=10, pady=10)
frame.grid(row=0, column=0)

url_label = tk.Label(frame, text="Enter YouTube URL or browse a local MP3 file:")
url_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

url_entry = tk.Entry(frame, width=50)
url_entry.grid(row=1, column=0, padx=5, pady=5)

browse_button = tk.Button(frame, text="Browse", command=browse_file)
browse_button.grid(row=1, column=1, padx=5, pady=5)

start_button = tk.Button(root, text="Start Process", command=start_process)
start_button.grid(row=1, column=0, padx=10, pady=10)

# task_bar_frame = tk.Frame(root)
# task_bar_frame.grid(row=2, column=0, padx=10, pady=10)

# task_bar_label = tk.Label(task_bar_frame, text="Progress:")
# task_bar_label.grid(row=0, column=0, padx=5, pady=5)

# task_bar = ttk.Progressbar(task_bar_frame, orient="horizontal", length=400, mode="determinate")
# task_bar.grid(row=0, column=1, padx=5, pady=5)

output_text = tk.StringVar()
output_label = tk.Label(root, textvariable=output_text)
output_label.grid(row=3, column=0, padx=10, pady=10)

open_button = tk.Button(root, text="Open Result", command=open_result)
open_button.grid(row=4, column=0, padx=10, pady=10)
open_button.grid_remove()

root.mainloop()
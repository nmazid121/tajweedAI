import tkinter as tk
from tkinter import ttk, messagebox
from pydub import AudioSegment
from pydub.playback import play
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tempfile
import shutil

# Create a local temp directory
TEMP_DIR = os.path.join(os.getcwd(), 'temp_audio')
os.makedirs(TEMP_DIR, exist_ok=True)

def play_audio(audio_segment):
    """Custom play function that uses local temp directory"""
    with tempfile.NamedTemporaryFile(suffix='.wav', dir=TEMP_DIR, delete=False) as f:
        audio_segment.export(f.name, format='wav')
        os.startfile(f.name)  # This works on Windows

class QalqalahAnnotator:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Qalqalah Annotator")
        self.window.geometry("800x900")  # Larger window for waveform

        # Reciter selection
        self.reciters = {
            "mishary": "Mishary Rashid Alafasy",
            "abdul_basit": "Abdul Basit Abdul Samad",
            "husary": "Mahmoud Khalil Al-Husary",
            "maher": "Maher Al Muaiqly",
            "minshawi": "Mohamed Siddiq El-Minshawi",
            "shuraim": "Saud Al-Shuraim",
            "yasser": "Yasser Al-Dosari"
        }
        
        # Progress tracking
        self.progress = {
            "total": 35,
            "completed": 0,
            "current_reciter": "mishary",
            "current_ayah": 1
        }

        self.setup_gui()
        self.setup_shortcuts()
        self.load_current_sample()

    def setup_gui(self):
        # Selection frame for both reciter and ayah
        selection_frame = tk.Frame(self.window, pady=10)
        selection_frame.pack()
        
        # Reciter selection
        reciter_frame = tk.Frame(selection_frame)
        reciter_frame.pack(side='left', padx=10)
        tk.Label(reciter_frame, text="Select Reciter:").pack(side='left')
        self.reciter_var = tk.StringVar(value="mishary")
        self.reciter_dropdown = ttk.Combobox(
            reciter_frame,
            textvariable=self.reciter_var,
            values=list(self.reciters.keys())
        )
        self.reciter_dropdown.pack(side='left', padx=5)
        self.reciter_dropdown.bind('<<ComboboxSelected>>', self.on_reciter_change)

        # Ayah selection
        ayah_frame = tk.Frame(selection_frame)
        ayah_frame.pack(side='left', padx=10)
        tk.Label(ayah_frame, text="Select Ayah:").pack(side='left')
        self.ayah_var = tk.StringVar(value="1")
        self.ayah_dropdown = ttk.Combobox(
            ayah_frame,
            textvariable=self.ayah_var,
            values=["1", "2", "3", "4", "5"],
            width=5
        )
        self.ayah_dropdown.pack(side='left', padx=5)
        self.ayah_dropdown.bind('<<ComboboxSelected>>', self.on_ayah_change)

        # Progress display
        self.progress_label = tk.Label(
            self.window,
            text="Progress: 0/35 samples",
            pady=10
        )
        self.progress_label.pack()

        # Current sample info
        self.info_label = tk.Label(
            self.window,
            text="",
            font=('Arial', 12),
            pady=10
        )
        self.info_label.pack()

        # Waveform display
        self.fig, self.ax = plt.subplots(figsize=(8, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(pady=10)

        # Controls
        controls_frame = tk.Frame(self.window)
        controls_frame.pack(pady=10)
        
        tk.Button(
            controls_frame,
            text="Play Word (Space)",
            command=self.play_word
        ).pack(side='left', padx=5)
        
        tk.Button(
            controls_frame,
            text="Loop Selection (Ctrl+Space)",
            command=self.loop_selection
        ).pack(side='left', padx=5)

        # Markers
        self.start_marker = tk.Scale(
            self.window,
            from_=0,
            to=100,
            orient='horizontal',
            length=600,
            label="Qalqalah Start (ms)",
            command=self.update_waveform_markers
        )
        self.start_marker.pack(pady=5)

        self.end_marker = tk.Scale(
            self.window,
            from_=0,
            to=100,
            orient='horizontal',
            length=600,
            label="Qalqalah End (ms)",
            command=self.update_waveform_markers
        )
        self.end_marker.pack(pady=5)

        # Quality rating
        rating_frame = tk.Frame(self.window)
        rating_frame.pack(pady=10)
        tk.Label(rating_frame, text="Qalqalah Clarity:").pack()
        self.rating_var = tk.IntVar(value=5)
        for i in range(1, 6):
            tk.Radiobutton(
                rating_frame,
                text=str(i),
                variable=self.rating_var,
                value=i
            ).pack(side='left')

        # Save button
        tk.Button(
            self.window,
            text="Save and Next (Enter)",
            command=self.save_annotation
        ).pack(pady=10)

        # Status
        self.status_label = tk.Label(self.window, text="", pady=10)
        self.status_label.pack()

    def setup_shortcuts(self):
        self.window.bind('<space>', lambda e: self.play_word())
        self.window.bind('<Control-space>', lambda e: self.loop_selection())
        self.window.bind('<Return>', lambda e: self.save_annotation())
        self.window.bind('<Right>', lambda e: self.advance_to_next_sample())

    def load_current_sample(self):
        try:
            # Load annotations
            json_file = f'falaq_tajweed_annotations_{self.progress["current_reciter"]}.json'
            with open(json_file, 'r', encoding='utf-8') as f:
                annotations = json.load(f)
                ayah_data = annotations['ayahs'][str(self.progress["current_ayah"])]

            # Find Qalqalah word
            qalqalah_word = None
            for word in ayah_data['words']:
                if word['has_qalqalah']:
                    qalqalah_word = word
                    break

            if not qalqalah_word:
                raise ValueError(f"No Qalqalah found in ayah {self.progress['current_ayah']}")

            # Get word timing
            word_idx = qalqalah_word['word_index'] - 1
            word_timing = ayah_data['segments'][word_idx]

            # Load audio
            audio_path = ayah_data['local_audio_path']
            audio = AudioSegment.from_mp3(audio_path)
            self.current_audio = audio[word_timing[1]:word_timing[2]]
            
            # Update UI
            self.update_waveform()
            
            # Set slider ranges and initial positions
            audio_duration = len(self.current_audio)
            self.start_marker.configure(to=audio_duration)
            self.end_marker.configure(to=audio_duration)
            
            # Set initial positions - start at 1/3 and end at 2/3 of the word
            self.start_marker.set(audio_duration // 3)
            self.end_marker.set(audio_duration * 2 // 3)
            
            # Update info display
            reciter_name = self.reciters[self.progress["current_reciter"]]
            info_text = (
                f"Reciter: {reciter_name}\n"
                f"Ayah {self.progress['current_ayah']}: {qalqalah_word['word_text']}\n"
                f"Letter: {qalqalah_word['qalqalah_details'][0]['letter']}"
            )
            self.info_label.configure(text=info_text)

            # Save context
            self.current_context = {
                'ayah': self.progress['current_ayah'],
                'word': qalqalah_word['word_text'],
                'letter': qalqalah_word['qalqalah_details'][0]['letter'],
                'type': qalqalah_word['qalqalah_details'][0]['type'],
                'word_timing': word_timing
            }

        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}")

    def update_waveform(self):
        if hasattr(self, 'current_audio'):
            # Convert audio to numpy array
            samples = np.array(self.current_audio.get_array_of_samples())
            
            # Clear previous plot
            self.ax.clear()
            
            # Plot waveform
            self.ax.plot(samples, color='blue', alpha=0.5)
            self.ax.set_xlabel('Samples')
            self.ax.set_ylabel('Amplitude')
            self.ax.set_title('Word Waveform (Drag markers to select Qalqalah)')
            
            # Update canvas
            self.canvas.draw()

    def update_waveform_markers(self, _=None):
        if hasattr(self, 'current_audio'):
            samples = np.array(self.current_audio.get_array_of_samples())
            start = int(self.start_marker.get() * len(samples) / len(self.current_audio))
            end = int(self.end_marker.get() * len(samples) / len(self.current_audio))
            
            self.ax.clear()
            self.ax.plot(samples, color='blue', alpha=0.5)
            self.ax.axvline(x=start, color='green', linestyle='--')
            self.ax.axvline(x=end, color='red', linestyle='--')
            self.ax.set_xlabel('Samples')
            self.ax.set_ylabel('Amplitude')
            self.canvas.draw()

    def play_word(self):
        if hasattr(self, 'current_audio'):
            play_audio(self.current_audio)

    def loop_selection(self):
        if hasattr(self, 'current_audio'):
            start = self.start_marker.get()
            end = self.end_marker.get()
            selection = self.current_audio[start:end]
            play_audio(selection)

    def save_annotation(self, _=None):
        if not hasattr(self, 'current_audio') or not hasattr(self, 'current_context'):
            return

        start = self.start_marker.get()
        end = self.end_marker.get()
        duration = end - start

        # Validate duration
        if duration < 50:
            if not messagebox.askyesno("Warning", "Selection might be too short for Qalqalah. Save anyway?"):
                return
        elif duration > 300:
            if not messagebox.askyesno("Warning", "Selection might be too long for Qalqalah. Save anyway?"):
                return

        # Create output directory
        output_dir = os.path.join(
            "qalqalah_samples",
            self.current_context['letter'],
            self.progress['current_reciter'],
            f"ayah_{self.current_context['ayah']}"
        )
        os.makedirs(output_dir, exist_ok=True)

        # Save audio segment
        qalqalah_audio = self.current_audio[start:end]
        audio_filename = f"qalqalah_{self.current_context['word']}_{start}_{end}.mp3"
        qalqalah_audio.export(
            os.path.join(output_dir, audio_filename),
            format="mp3"
        )

        # Save annotation
        annotation = {
            "ayah": self.current_context['ayah'],
            "word": self.current_context['word'],
            "letter": self.current_context['letter'],
            "type": self.current_context['type'],
            "timing": {
                "qalqalah_start": start,
                "qalqalah_end": end,
                "qalqalah_duration_ms": duration
            },
            "quality_rating": self.rating_var.get(),
            "audio_file": audio_filename
        }

        with open(os.path.join(output_dir, "annotation.json"), 'w', encoding='utf-8') as f:
            json.dump(annotation, f, indent=2, ensure_ascii=False)

        # Update progress
        self.progress['completed'] += 1
        self.progress_label.configure(
            text=f"Progress: {self.progress['completed']}/35 samples"
        )
        self.status_label.configure(
            text=f"Saved! Duration: {duration}ms"
        )

        # Move to next sample
        self.advance_to_next_sample()

    def advance_to_next_sample(self):
        if self.progress['current_ayah'] < 5:
            self.progress['current_ayah'] += 1
        else:
            # Move to next reciter
            current_idx = list(self.reciters.keys()).index(
                self.progress['current_reciter']
            )
            if current_idx < len(self.reciters) - 1:
                self.progress['current_reciter'] = list(
                    self.reciters.keys()
                )[current_idx + 1]
                self.progress['current_ayah'] = 1
                self.reciter_var.set(self.progress['current_reciter'])
            else:
                # All done!
                messagebox.showinfo(
                    "Complete!",
                    "All 35 samples have been annotated!"
                )
                return

        self.load_current_sample()

    def on_reciter_change(self, _):
        self.progress['current_reciter'] = self.reciter_var.get()
        self.load_current_sample()

    def on_ayah_change(self, _):
        """Handle ayah selection change"""
        self.progress['current_ayah'] = int(self.ayah_var.get())
        self.load_current_sample()

    def run(self):
        try:
            self.window.mainloop()
        finally:
            # Cleanup temp files when closing
            if os.path.exists(TEMP_DIR):
                shutil.rmtree(TEMP_DIR)

if __name__ == "__main__":
    app = QalqalahAnnotator()
    app.run() 
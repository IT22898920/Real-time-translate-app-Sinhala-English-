import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
import urllib.request
import urllib.parse
import json

# Try importing speech recognition
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("Warning: SpeechRecognition not installed. Install with: py -m pip install SpeechRecognition")

class RealtimeTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-time Voice Translator - සජීවී හඬ පරිවර්තකය")
        self.root.geometry("800x600")

        # Initialize speech availability
        self.speech_available = SPEECH_AVAILABLE

        if self.speech_available:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
            except Exception as e:
                print(f"Microphone initialization failed: {e}")
                print("PyAudio not installed. Voice features disabled.")
                self.speech_available = False
                self.recognizer = None
                self.microphone = None
        else:
            self.recognizer = None
            self.microphone = None

        self.is_listening = False
        self.audio_queue = queue.Queue()

        self.input_lang = 'en'
        self.output_lang = 'si'

        self.setup_ui()

        if self.speech_available and self.microphone:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
            except:
                pass

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="Real-time Voice Translator",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        subtitle_label = ttk.Label(main_frame, text="සජීවී හඬ පරිවර්තකය",
                                   font=('Arial', 12))
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=5)

        lang_frame = ttk.LabelFrame(main_frame, text="Language Settings / භාෂා සැකසුම්",
                                    padding="10")
        lang_frame.grid(row=2, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))

        ttk.Label(lang_frame, text="Input Language:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.input_lang_combo = ttk.Combobox(lang_frame, width=20)
        self.input_lang_combo.grid(row=0, column=1, padx=5)

        ttk.Label(lang_frame, text="Output Language:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.output_lang_combo = ttk.Combobox(lang_frame, width=20)
        self.output_lang_combo.grid(row=0, column=3, padx=5)

        common_languages = {
            'en': 'English',
            'si': 'Sinhala (සිංහල)',
            'ta': 'Tamil (தமிழ்)',
            'hi': 'Hindi (हिन्दी)',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh-CN': 'Chinese (Simplified)'
        }

        lang_values = [f"{name} ({code})" for code, name in common_languages.items()]
        self.input_lang_combo['values'] = lang_values
        self.output_lang_combo['values'] = lang_values

        self.input_lang_combo.set("English (en)")
        self.output_lang_combo.set("Sinhala (සිංහල) (si)")

        self.input_lang_combo.bind('<<ComboboxSelected>>', self.update_languages)
        self.output_lang_combo.bind('<<ComboboxSelected>>', self.update_languages)

        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=3, column=0, columnspan=3, pady=20)

        self.listen_button = ttk.Button(control_frame, text="🎤 Start Listening / සවන් දීම ආරම්භ කරන්න",
                                       command=self.toggle_listening, width=30)
        self.listen_button.grid(row=0, column=0, padx=10)

        self.text_mode_button = ttk.Button(control_frame, text="📝 Text Mode / පෙළ මාදිලිය",
                                          command=self.toggle_text_mode, width=20)
        self.text_mode_button.grid(row=0, column=1, padx=10)

        self.clear_button = ttk.Button(control_frame, text="Clear / මකන්න",
                                      command=self.clear_text, width=15)
        self.clear_button.grid(row=0, column=2, padx=10)

        text_frame = ttk.LabelFrame(main_frame, text="Conversation / සංවාදය", padding="10")
        text_frame.grid(row=4, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.text_display = scrolledtext.ScrolledText(text_frame, width=80, height=20,
                                                      wrap=tk.WORD, font=('Arial', 11))
        self.text_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.text_display.tag_config("original", foreground="blue")
        self.text_display.tag_config("translated", foreground="green", font=('Arial', 11, 'bold'))
        self.text_display.tag_config("error", foreground="red")
        self.text_display.tag_config("status", foreground="gray", font=('Arial', 9, 'italic'))

        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))

        # Text input area (initially hidden)
        self.text_input_frame = ttk.LabelFrame(main_frame, text="Text Input / පෙළ ඇතුළත් කිරීම", padding="10")

        self.text_input_area = scrolledtext.ScrolledText(self.text_input_frame, height=4, wrap=tk.WORD,
                                                        font=('Arial', 11))
        self.text_input_area.pack(fill=tk.BOTH, expand=True, pady=5)

        text_button_frame = ttk.Frame(self.text_input_frame)
        text_button_frame.pack(fill=tk.X, pady=5)

        self.translate_text_button = ttk.Button(text_button_frame, text="🌐 Translate Text",
                                               command=self.translate_input_text)
        self.translate_text_button.pack(side=tk.LEFT, padx=5)

        self.clear_input_button = ttk.Button(text_button_frame, text="Clear Input",
                                            command=self.clear_input_text)
        self.clear_input_button.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(status_frame, text="Ready to start / ආරම්භ කිරීමට සූදානම්",
                                     foreground="green")
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

    def update_languages(self, event=None):
        input_selection = self.input_lang_combo.get()
        output_selection = self.output_lang_combo.get()

        self.input_lang = input_selection.split('(')[-1].rstrip(')')
        self.output_lang = output_selection.split('(')[-1].rstrip(')')

    def toggle_listening(self):
        if not self.speech_available or not self.microphone:
            messagebox.showwarning("Speech Recognition Not Available",
                                 "Microphone features are not available.\n"
                                 "PyAudio needs to be installed.\n\n"
                                 "To install PyAudio on Windows:\n"
                                 "1. Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio\n"
                                 "2. Install with: py -m pip install downloaded_file.whl\n\n"
                                 "Or use Text Mode for translation.")
            return

        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.is_listening = True
        self.listen_button.configure(text="⏹ Stop Listening / සවන් දීම නතර කරන්න")
        self.status_label.configure(text="Listening... / සවන් දෙමින්...", foreground="blue")

        self.text_display.insert(tk.END, "\n--- Started listening / සවන් දීම ආරම්භ කළා ---\n", "status")
        self.text_display.see(tk.END)

        self.listen_thread = threading.Thread(target=self.listen_continuously, daemon=True)
        self.listen_thread.start()

        self.process_thread = threading.Thread(target=self.process_audio, daemon=True)
        self.process_thread.start()

    def stop_listening(self):
        self.is_listening = False
        self.listen_button.configure(text="🎤 Start Listening / සවන් දීම ආරම්භ කරන්න")
        self.status_label.configure(text="Stopped / නතර කළා", foreground="orange")

        self.text_display.insert(tk.END, "\n--- Stopped listening / සවන් දීම නතර කළා ---\n", "status")
        self.text_display.see(tk.END)

    def listen_continuously(self):
        with self.microphone as source:
            while self.is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    self.audio_queue.put(audio)
                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    print(f"Error in listening: {e}")

    def process_audio(self):
        while self.is_listening:
            try:
                if not self.audio_queue.empty():
                    audio = self.audio_queue.get()
                    self.recognize_and_translate(audio)
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error in processing: {e}")

    def recognize_and_translate(self, audio):
        try:
            self.root.after(0, lambda: self.status_label.configure(
                text="Recognizing speech... / කථනය හඳුනා ගනිමින්...", foreground="purple"))

            text = self.recognizer.recognize_google(audio, language=self.input_lang)

            self.root.after(0, lambda: self.text_display.insert(
                tk.END, f"\n📢 Original ({self.input_lang}): {text}\n", "original"))

            self.root.after(0, lambda: self.status_label.configure(
                text="Translating... / පරිවර්තනය කරමින්...", foreground="purple"))

            # Use Google Translate API directly
            translated_text = self.translate_text(text)

            if translated_text:
                self.root.after(0, lambda: self.text_display.insert(
                    tk.END, f"🌐 Translation ({self.output_lang}): {translated_text}\n", "translated"))

                self.root.after(0, lambda: self.text_display.insert(tk.END, "-" * 50 + "\n", "status"))

                self.root.after(0, lambda: self.text_display.see(tk.END))

            self.root.after(0, lambda: self.status_label.configure(
                text="Listening... / සවන් දෙමින්...", foreground="blue"))

        except sr.UnknownValueError:
            self.root.after(0, lambda: self.status_label.configure(
                text="Could not understand audio / ශබ්දය තේරුම් ගැනීමට නොහැකි විය", foreground="orange"))
        except sr.RequestError as e:
            self.root.after(0, lambda: self.text_display.insert(
                tk.END, f"\n❌ Speech recognition error: {e}\n", "error"))
            self.root.after(0, lambda: self.status_label.configure(
                text="Speech recognition error / කථන හඳුනාගැනීමේ දෝෂයක්", foreground="red"))
        except Exception as e:
            self.root.after(0, lambda: self.text_display.insert(
                tk.END, f"\n❌ Translation error: {e}\n", "error"))
            self.root.after(0, lambda: self.status_label.configure(
                text="Translation error / පරිවර්තන දෝෂයක්", foreground="red"))

    def translate_text(self, text):
        """Translate text using Google Translate API"""
        try:
            base_url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': self.input_lang,
                'tl': self.output_lang,
                'dt': 't',
                'q': text
            }

            url = base_url + '?' + urllib.parse.urlencode(params)
            headers = {'User-Agent': 'Mozilla/5.0'}

            request = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(request, timeout=10)
            result = json.loads(response.read().decode('utf-8'))

            # Extract translated text
            translated_text = ''
            if result and len(result) > 0 and result[0]:
                for sentence in result[0]:
                    if sentence[0]:
                        translated_text += sentence[0]

            return translated_text

        except Exception as e:
            print(f"Translation error: {e}")
            return None

    def toggle_text_mode(self):
        """Toggle text input area visibility"""
        if self.text_input_frame.winfo_viewable():
            self.text_input_frame.grid_remove()
            self.text_mode_button.configure(text="📝 Text Mode / පෙළ මාදිලිය")
        else:
            self.text_input_frame.grid(row=3, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
            self.text_mode_button.configure(text="📝 Hide Text / පෙළ සඟවන්න")
            self.text_input_area.focus()

    def translate_input_text(self):
        """Translate text from input area"""
        text = self.text_input_area.get(1.0, tk.END).strip()
        if not text:
            return

        # Display original text
        self.text_display.insert(tk.END, f"\n📝 Input Text: {text}\n", "original")

        # Translate
        self.status_label.configure(text="Translating... / පරිවර්තනය කරමින්...", foreground="orange")
        translated_text = self.translate_text(text)

        if translated_text:
            self.text_display.insert(tk.END, f"🌐 Translation: {translated_text}\n", "translated")
            self.text_display.insert(tk.END, "-" * 50 + "\n", "system")
            self.status_label.configure(text="Translation complete / පරිවර්තනය සම්පූර්ණයි", foreground="green")
        else:
            self.text_display.insert(tk.END, "❌ Translation failed\n", "error")
            self.status_label.configure(text="Translation error / පරිවර්තන දෝෂය", foreground="red")

        self.text_display.see(tk.END)

    def clear_input_text(self):
        """Clear input text area"""
        self.text_input_area.delete(1.0, tk.END)

    def clear_text(self):
        self.text_display.delete(1.0, tk.END)
        self.status_label.configure(text="Cleared / මකා දැමුවා", foreground="green")

def main():
    root = tk.Tk()
    app = RealtimeTranslator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
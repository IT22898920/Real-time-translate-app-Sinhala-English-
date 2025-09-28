import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
import urllib.request
import urllib.parse
import json

# Try to import speech recognition
try:
    import speech_recognition as sr
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("Speech Recognition not installed. Voice features will be disabled.")
    print("To enable voice features, run: py -m pip install SpeechRecognition pyaudio")

class VoiceTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice & Text Translator - හඬ සහ පෙළ පරිවර්තකය")
        self.root.geometry("950x700")
        self.root.configure(bg='#f0f0f0')

        # Initialize speech recognition if available
        if SPEECH_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()

        self.input_lang = 'en'
        self.output_lang = 'si'

        # Translation history
        self.history = []

        self.setup_ui()

        # Adjust for ambient noise if speech is available
        if SPEECH_AVAILABLE:
            try:
                with self.microphone as source:
                    self.status_label.config(text="Adjusting for ambient noise... / පරිසර ශබ්ද සකසමින්...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    self.status_label.config(text="Ready / සූදානම්")
            except:
                self.status_label.config(text="Microphone not found / මයික්‍රෆෝනය හමු නොවිය")

    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title Frame
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        title_label = ttk.Label(title_frame, text="🎤 Real-time Voice Translator",
                                font=('Segoe UI', 20, 'bold'))
        title_label.pack()

        subtitle_label = ttk.Label(title_frame, text="සජීවී හඬ පරිවර්තකය",
                                   font=('Segoe UI', 14))
        subtitle_label.pack()

        # Language Selection Frame
        lang_frame = ttk.LabelFrame(main_container, text="Language Settings / භාෂා සැකසුම්",
                                    padding="10")
        lang_frame.pack(fill=tk.X, pady=(0, 10))

        # Language options
        languages = [
            ('English', 'en'),
            ('Sinhala (සිංහල)', 'si'),
            ('Tamil (தமிழ்)', 'ta'),
            ('Hindi (हिन्दी)', 'hi'),
            ('Spanish', 'es'),
            ('French', 'fr'),
            ('German', 'de'),
            ('Italian', 'it'),
            ('Japanese', 'ja'),
            ('Korean', 'ko'),
            ('Chinese', 'zh-CN'),
            ('Russian', 'ru'),
            ('Arabic', 'ar')
        ]

        self.lang_dict = {name: code for name, code in languages}
        lang_names = [name for name, code in languages]

        # Input language
        ttk.Label(lang_frame, text="Speak in / කතා කරන්න:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.input_lang_combo = ttk.Combobox(lang_frame, width=20, values=lang_names)
        self.input_lang_combo.grid(row=0, column=1, padx=5)
        self.input_lang_combo.set("English")

        # Output language
        ttk.Label(lang_frame, text="Translate to / පරිවර්තනය:").grid(row=0, column=2, padx=20, sticky=tk.W)
        self.output_lang_combo = ttk.Combobox(lang_frame, width=20, values=lang_names)
        self.output_lang_combo.grid(row=0, column=3, padx=5)
        self.output_lang_combo.set("Sinhala (සිංහල)")

        # Swap button
        swap_btn = ttk.Button(lang_frame, text="⇄", width=3,
                             command=self.swap_languages)
        swap_btn.grid(row=0, column=4, padx=10)

        self.input_lang_combo.bind('<<ComboboxSelected>>', self.update_languages)
        self.output_lang_combo.bind('<<ComboboxSelected>>', self.update_languages)

        # Control Panel
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Voice controls
        voice_frame = ttk.LabelFrame(control_frame, text="Voice Controls / හඬ පාලන", padding="10")
        voice_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        if SPEECH_AVAILABLE:
            self.mic_button = ttk.Button(voice_frame, text="🎤 Start Listening",
                                        command=self.toggle_listening, width=20)
            self.mic_button.pack(side=tk.LEFT, padx=5)

            # Voice indicator
            self.voice_indicator = tk.Canvas(voice_frame, width=30, height=30)
            self.voice_indicator.pack(side=tk.LEFT, padx=10)
            self.indicator_circle = self.voice_indicator.create_oval(5, 5, 25, 25,
                                                                    fill='gray', outline='')
        else:
            no_voice_label = ttk.Label(voice_frame,
                                      text="Voice features disabled. Install SpeechRecognition",
                                      foreground='orange')
            no_voice_label.pack()

        # Text controls
        text_frame = ttk.LabelFrame(control_frame, text="Text Input / පෙළ ඇතුළත් කිරීම", padding="10")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.text_mode_btn = ttk.Button(text_frame, text="📝 Text Mode",
                                       command=self.show_text_input, width=15)
        self.text_mode_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(text_frame, text="🗑️ Clear",
                                   command=self.clear_all, width=10)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Text input area (initially hidden)
        self.text_input_frame = ttk.Frame(main_container)

        input_label = ttk.Label(self.text_input_frame, text="Type here / මෙහි ටයිප් කරන්න:")
        input_label.pack(anchor=tk.W)

        self.text_input = tk.Text(self.text_input_frame, height=3, font=('Segoe UI', 11))
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=5)

        translate_text_btn = ttk.Button(self.text_input_frame, text="Translate Text",
                                       command=self.translate_text_input)
        translate_text_btn.pack()

        # Conversation Display
        display_frame = ttk.LabelFrame(main_container, text="Conversation / සංවාදය", padding="10")
        display_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Create notebook for tabbed display
        self.notebook = ttk.Notebook(display_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Main conversation tab
        conv_tab = ttk.Frame(self.notebook)
        self.notebook.add(conv_tab, text="Live / සජීවී")

        self.conversation_display = scrolledtext.ScrolledText(conv_tab, wrap=tk.WORD,
                                                             font=('Segoe UI', 11),
                                                             height=15)
        self.conversation_display.pack(fill=tk.BOTH, expand=True)

        # Configure text tags
        self.conversation_display.tag_config("timestamp", foreground="gray", font=('Segoe UI', 9))
        self.conversation_display.tag_config("original", foreground="blue", font=('Segoe UI', 11))
        self.conversation_display.tag_config("translated", foreground="green", font=('Segoe UI', 12, 'bold'))
        self.conversation_display.tag_config("error", foreground="red")
        self.conversation_display.tag_config("system", foreground="purple", font=('Segoe UI', 9, 'italic'))

        # History tab
        history_tab = ttk.Frame(self.notebook)
        self.notebook.add(history_tab, text="History / ඉතිහාසය")

        self.history_display = scrolledtext.ScrolledText(history_tab, wrap=tk.WORD,
                                                        font=('Segoe UI', 11),
                                                        height=15)
        self.history_display.pack(fill=tk.BOTH, expand=True)

        # Status bar
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X)

        self.status_label = ttk.Label(status_frame, text="Ready / සූදානම්",
                                     font=('Segoe UI', 10))
        self.status_label.pack(side=tk.LEFT)

        self.connection_label = ttk.Label(status_frame, text="",
                                         font=('Segoe UI', 10))
        self.connection_label.pack(side=tk.RIGHT)

        # Start processing thread
        self.process_thread = threading.Thread(target=self.process_text_queue, daemon=True)
        self.process_thread.start()

    def update_languages(self, event=None):
        input_selection = self.input_lang_combo.get()
        output_selection = self.output_lang_combo.get()

        self.input_lang = self.lang_dict.get(input_selection, 'en')
        self.output_lang = self.lang_dict.get(output_selection, 'si')

    def swap_languages(self):
        input_val = self.input_lang_combo.get()
        output_val = self.output_lang_combo.get()
        self.input_lang_combo.set(output_val)
        self.output_lang_combo.set(input_val)
        self.update_languages()

    def toggle_listening(self):
        if not SPEECH_AVAILABLE:
            messagebox.showwarning("Not Available",
                                  "Speech recognition not installed.\nRun: py -m pip install SpeechRecognition pyaudio")
            return

        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()

    def start_listening(self):
        self.is_listening = True
        self.mic_button.configure(text="⏹ Stop Listening")
        self.voice_indicator.itemconfig(self.indicator_circle, fill='red')
        self.status_label.configure(text="Listening... / සවන් දෙමින්...")

        # Add system message
        timestamp = time.strftime("%H:%M:%S")
        self.conversation_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.conversation_display.insert(tk.END, "Started listening\n", "system")
        self.conversation_display.see(tk.END)

        # Start listening thread
        self.listen_thread = threading.Thread(target=self.listen_continuously, daemon=True)
        self.listen_thread.start()

        # Start processing audio
        self.audio_process_thread = threading.Thread(target=self.process_audio_queue, daemon=True)
        self.audio_process_thread.start()

    def stop_listening(self):
        self.is_listening = False
        self.mic_button.configure(text="🎤 Start Listening")
        self.voice_indicator.itemconfig(self.indicator_circle, fill='gray')
        self.status_label.configure(text="Stopped / නතර කළා")

        # Add system message
        timestamp = time.strftime("%H:%M:%S")
        self.conversation_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.conversation_display.insert(tk.END, "Stopped listening\n", "system")
        self.conversation_display.see(tk.END)

    def listen_continuously(self):
        with self.microphone as source:
            while self.is_listening:
                try:
                    # Listen with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    self.audio_queue.put(audio)

                    # Flash indicator
                    self.root.after(0, lambda: self.voice_indicator.itemconfig(
                        self.indicator_circle, fill='yellow'))
                    time.sleep(0.1)
                    self.root.after(0, lambda: self.voice_indicator.itemconfig(
                        self.indicator_circle, fill='red'))

                except sr.WaitTimeoutError:
                    pass
                except Exception as e:
                    print(f"Listening error: {e}")

    def process_audio_queue(self):
        while self.is_listening:
            try:
                if not self.audio_queue.empty():
                    audio = self.audio_queue.get()
                    self.recognize_speech(audio)
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"Processing error: {e}")

    def recognize_speech(self, audio):
        try:
            # Update status
            self.root.after(0, lambda: self.status_label.configure(
                text="Recognizing... / හඳුනා ගනිමින්..."))

            # Recognize speech
            text = self.recognizer.recognize_google(audio, language=self.input_lang)

            # Add to text queue for translation
            self.text_queue.put(text)

        except sr.UnknownValueError:
            self.root.after(0, lambda: self.status_label.configure(
                text="Could not understand / තේරුම් ගැනීමට නොහැකි විය"))
        except sr.RequestError as e:
            self.root.after(0, lambda: self.status_label.configure(
                text="Recognition error / හඳුනාගැනීමේ දෝෂය"))
        except Exception as e:
            print(f"Recognition error: {e}")

    def process_text_queue(self):
        """Process text queue for translation"""
        while True:
            try:
                if not self.text_queue.empty():
                    text = self.text_queue.get()
                    self.translate_and_display(text)
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"Text processing error: {e}")

    def translate_and_display(self, text):
        """Translate text and display in conversation"""
        timestamp = time.strftime("%H:%M:%S")

        # Display original text
        self.root.after(0, lambda: self.conversation_display.insert(
            tk.END, f"\n[{timestamp}] ", "timestamp"))
        self.root.after(0, lambda: self.conversation_display.insert(
            tk.END, f"📢 {self.input_lang.upper()}: ", "original"))
        self.root.after(0, lambda: self.conversation_display.insert(
            tk.END, f"{text}\n", "original"))

        # Update status
        self.root.after(0, lambda: self.status_label.configure(
            text="Translating... / පරිවර්තනය කරමින්..."))

        # Translate
        try:
            translated = self.translate_text(text)

            if translated:
                # Display translated text
                self.root.after(0, lambda: self.conversation_display.insert(
                    tk.END, f"🌐 {self.output_lang.upper()}: ", "translated"))
                self.root.after(0, lambda: self.conversation_display.insert(
                    tk.END, f"{translated}\n", "translated"))
                self.root.after(0, lambda: self.conversation_display.insert(
                    tk.END, "-" * 60 + "\n", "system"))

                # Add to history
                self.history.append({
                    'time': timestamp,
                    'original': text,
                    'translated': translated,
                    'from': self.input_lang,
                    'to': self.output_lang
                })

                # Update history display
                self.update_history_display()

            # Update status
            self.root.after(0, lambda: self.status_label.configure(
                text="Ready / සූදානම්" if not self.is_listening else "Listening... / සවන් දෙමින්..."))

            # Auto-scroll
            self.root.after(0, lambda: self.conversation_display.see(tk.END))

        except Exception as e:
            self.root.after(0, lambda: self.conversation_display.insert(
                tk.END, f"❌ Translation error: {e}\n", "error"))

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

    def show_text_input(self):
        """Toggle text input area"""
        if self.text_input_frame.winfo_viewable():
            self.text_input_frame.pack_forget()
            self.text_mode_btn.configure(text="📝 Text Mode")
        else:
            self.text_input_frame.pack(fill=tk.BOTH, pady=10, before=self.notebook.master)
            self.text_mode_btn.configure(text="📝 Hide Text")
            self.text_input.focus()

    def translate_text_input(self):
        """Translate text from input field"""
        text = self.text_input.get(1.0, tk.END).strip()
        if text:
            self.text_queue.put(text)
            self.text_input.delete(1.0, tk.END)

    def clear_all(self):
        """Clear all displays"""
        self.conversation_display.delete(1.0, tk.END)
        self.status_label.configure(text="Cleared / මකා දැමුවා")

    def update_history_display(self):
        """Update history tab"""
        self.history_display.delete(1.0, tk.END)
        for item in self.history[-20:]:  # Show last 20 translations
            self.history_display.insert(tk.END, f"[{item['time']}]\n", "timestamp")
            self.history_display.insert(tk.END, f"{item['from']}: {item['original']}\n", "original")
            self.history_display.insert(tk.END, f"{item['to']}: {item['translated']}\n", "translated")
            self.history_display.insert(tk.END, "-" * 40 + "\n", "system")

def main():
    root = tk.Tk()
    app = VoiceTranslator(root)

    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()

if __name__ == "__main__":
    main()
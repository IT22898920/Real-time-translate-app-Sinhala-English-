import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import urllib.request
import urllib.parse
import json

# Alternative voice recognition using Windows Speech API
try:
    import win32com.client
    WINDOWS_SPEECH_AVAILABLE = True
except ImportError:
    WINDOWS_SPEECH_AVAILABLE = False

class SimpleVoiceTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Voice Translator - සරල හඬ පරිවර්තකය")
        self.root.geometry("900x650")

        self.input_lang = 'en'
        self.output_lang = 'si'
        self.is_listening = False

        # Initialize Windows Speech Recognition
        if WINDOWS_SPEECH_AVAILABLE:
            try:
                self.speech_engine = win32com.client.Dispatch("SAPI.SpVoice")
                self.recognition_engine = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
                self.speech_available = True
            except:
                self.speech_available = False
        else:
            self.speech_available = False

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="🎤 Simple Voice Translator",
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=10)

        subtitle_label = ttk.Label(main_frame, text="සරල හඬ පරිවර්තකය",
                                  font=('Arial', 14))
        subtitle_label.pack(pady=5)

        # Language selection
        lang_frame = ttk.LabelFrame(main_frame, text="Languages / භාෂා", padding="10")
        lang_frame.pack(fill=tk.X, pady=10)

        languages = [
            ('English', 'en'),
            ('Sinhala (සිංහල)', 'si'),
            ('Tamil (தமிழ்)', 'ta'),
            ('Hindi (हिन्दी)', 'hi'),
            ('Spanish', 'es'),
            ('French', 'fr'),
            ('German', 'de'),
            ('Japanese', 'ja'),
            ('Korean', 'ko'),
            ('Chinese', 'zh-CN')
        ]

        self.lang_dict = {name: code for name, code in languages}
        lang_names = [name for name, code in languages]

        ttk.Label(lang_frame, text="From:").grid(row=0, column=0, padx=5)
        self.input_combo = ttk.Combobox(lang_frame, values=lang_names, width=20)
        self.input_combo.grid(row=0, column=1, padx=5)
        self.input_combo.set("English")

        ttk.Label(lang_frame, text="To:").grid(row=0, column=2, padx=5)
        self.output_combo = ttk.Combobox(lang_frame, values=lang_names, width=20)
        self.output_combo.grid(row=0, column=3, padx=5)
        self.output_combo.set("Sinhala (සිංහල)")

        self.input_combo.bind('<<ComboboxSelected>>', self.update_languages)
        self.output_combo.bind('<<ComboboxSelected>>', self.update_languages)

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=10)

        # Voice button
        if self.speech_available:
            self.voice_btn = ttk.Button(control_frame, text="🎤 Voice Input",
                                       command=self.voice_input, width=15)
            self.voice_btn.pack(side=tk.LEFT, padx=5)
        else:
            no_voice_label = ttk.Label(control_frame,
                                      text="Voice: Install pywin32 for Windows Speech API",
                                      foreground="orange")
            no_voice_label.pack(side=tk.LEFT, padx=5)

        # Text input button
        self.text_btn = ttk.Button(control_frame, text="📝 Text Input",
                                  command=self.show_text_input, width=15)
        self.text_btn.pack(side=tk.LEFT, padx=5)

        # Clear button
        self.clear_btn = ttk.Button(control_frame, text="🗑️ Clear",
                                   command=self.clear_display, width=10)
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Text input area (hidden initially)
        self.text_frame = ttk.LabelFrame(main_frame, text="Text Input", padding="10")

        self.text_input = tk.Text(self.text_frame, height=3, font=('Arial', 11))
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=5)

        text_controls = ttk.Frame(self.text_frame)
        text_controls.pack()

        ttk.Button(text_controls, text="Translate",
                  command=self.translate_text_input).pack(side=tk.LEFT, padx=5)
        ttk.Button(text_controls, text="Clear Input",
                  command=lambda: self.text_input.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)

        # Results display
        result_frame = ttk.LabelFrame(main_frame, text="Results / ප්‍රතිඵල", padding="10")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.result_display = scrolledtext.ScrolledText(result_frame, height=15,
                                                       font=('Arial', 11))
        self.result_display.pack(fill=tk.BOTH, expand=True)

        # Configure text tags
        self.result_display.tag_config("input", foreground="blue", font=('Arial', 11))
        self.result_display.tag_config("output", foreground="green", font=('Arial', 12, 'bold'))
        self.result_display.tag_config("timestamp", foreground="gray", font=('Arial', 9))
        self.result_display.tag_config("error", foreground="red")

        # Status
        self.status_label = ttk.Label(main_frame, text="Ready / සූදානම්")
        self.status_label.pack(pady=5)

    def update_languages(self, event=None):
        input_selection = self.input_combo.get()
        output_selection = self.output_combo.get()

        self.input_lang = self.lang_dict.get(input_selection, 'en')
        self.output_lang = self.lang_dict.get(output_selection, 'si')

    def voice_input(self):
        """Simple voice input dialog"""
        if not self.speech_available:
            messagebox.showwarning("Voice Not Available",
                                 "Windows Speech API not available.\n"
                                 "Install with: pip install pywin32")
            return

        # Simple voice input prompt
        voice_text = tk.simpledialog.askstring("Voice Input",
                                              "Click OK and speak your text.\n"
                                              "Press Enter when done.")
        if voice_text:
            self.process_text(voice_text, "🎤 Voice")

    def show_text_input(self):
        """Toggle text input area"""
        if self.text_frame.winfo_viewable():
            self.text_frame.pack_forget()
            self.text_btn.config(text="📝 Text Input")
        else:
            self.text_frame.pack(fill=tk.X, pady=10, before=self.result_display.master)
            self.text_btn.config(text="📝 Hide Text")
            self.text_input.focus()

    def translate_text_input(self):
        """Translate text from input area"""
        text = self.text_input.get(1.0, tk.END).strip()
        if text:
            self.process_text(text, "📝 Text")
            self.text_input.delete(1.0, tk.END)

    def process_text(self, text, input_type):
        """Process and translate text"""
        timestamp = time.strftime("%H:%M:%S")

        # Display input
        self.result_display.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
        self.result_display.insert(tk.END, f"{input_type} ({self.input_lang}): ", "input")
        self.result_display.insert(tk.END, f"{text}\n", "input")

        # Update status
        self.status_label.config(text="Translating... / පරිවර්තනය කරමින්...")

        # Translate in separate thread
        thread = threading.Thread(target=self.translate_and_display, args=(text,))
        thread.daemon = True
        thread.start()

    def translate_and_display(self, text):
        """Translate text and display result"""
        try:
            translated = self.translate_text(text)

            if translated:
                # Display translation
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, f"🌐 Translation ({self.output_lang}): ", "output"))
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, f"{translated}\n", "output"))
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, "-" * 60 + "\n", "timestamp"))

                # Update status
                self.root.after(0, lambda: self.status_label.config(
                    text="Translation complete / පරිවර්තනය සම්පූර්ණයි"))

                # Auto-scroll
                self.root.after(0, lambda: self.result_display.see(tk.END))
            else:
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, "❌ Translation failed\n", "error"))

        except Exception as e:
            self.root.after(0, lambda: self.result_display.insert(
                tk.END, f"❌ Error: {e}\n", "error"))

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

    def clear_display(self):
        """Clear result display"""
        self.result_display.delete(1.0, tk.END)
        self.status_label.config(text="Cleared / මකා දැමුවා")

def main():
    # Import simpledialog
    import tkinter.simpledialog
    tk.simpledialog = tkinter.simpledialog

    root = tk.Tk()
    app = SimpleVoiceTranslator(root)

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
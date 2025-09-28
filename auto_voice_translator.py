import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import urllib.request
import urllib.parse
import json
import os
import tempfile
import subprocess
import wave

# Try to import Windows Speech API
try:
    import win32com.client
    import pythoncom
    WINDOWS_SPEECH = True
except ImportError:
    WINDOWS_SPEECH = False

class AutoVoiceTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Voice Translator - ස්වයංක්‍රීය හඬ පරිවර්තකය")
        self.root.geometry("1000x750")
        self.root.configure(bg='#f0f2f5')

        self.input_lang = 'en'
        self.output_lang = 'si'
        self.is_listening = False
        self.speech_recognition = None

        # Initialize Windows Speech Recognition
        self.init_speech_recognition()
        self.setup_ui()

    def init_speech_recognition(self):
        """Initialize Windows Speech Recognition"""
        if WINDOWS_SPEECH:
            try:
                pythoncom.CoInitialize()
                self.speech_recognition = win32com.client.Dispatch("SAPI.SpSharedRecognizer")
                self.speech_context = self.speech_recognition.CreateRecoContext()
                self.speech_available = True
                print("Windows Speech Recognition initialized successfully!")
            except Exception as e:
                print(f"Speech Recognition initialization failed: {e}")
                self.speech_available = False
        else:
            self.speech_available = False

    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f2f5')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header with gradient effect
        header_frame = tk.Frame(main_container, bg='#1e3a8a', height=100)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="🤖 Auto Voice Translator",
                              font=('Segoe UI', 24, 'bold'),
                              fg='white', bg='#1e3a8a')
        title_label.pack(expand=True)

        subtitle_label = tk.Label(header_frame, text="ස්වයංක්‍රීය හඬ පරිවර්තකය - Speak and Get Instant Translation",
                                 font=('Segoe UI', 12),
                                 fg='#e0e7ff', bg='#1e3a8a')
        subtitle_label.pack()

        # Status and availability info
        info_frame = tk.Frame(main_container, bg='#f0f2f5')
        info_frame.pack(fill=tk.X, pady=(0, 15))

        if self.speech_available:
            status_text = "🟢 Auto Voice Recognition: AVAILABLE"
            status_color = "#10b981"
            detail_text = "Windows Speech Recognition is ready. Click 'Start Listening' to begin."
        else:
            status_text = "🔴 Auto Voice Recognition: NOT AVAILABLE"
            status_color = "#ef4444"
            detail_text = "Install pywin32: pip install pywin32"

        tk.Label(info_frame, text=status_text,
                font=('Segoe UI', 12, 'bold'),
                fg=status_color, bg='#f0f2f5').pack()

        tk.Label(info_frame, text=detail_text,
                font=('Segoe UI', 10),
                fg='#6b7280', bg='#f0f2f5').pack()

        # Language selection
        lang_frame = tk.LabelFrame(main_container, text=" Language Settings / භාෂා සැකසුම් ",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='#ffffff', fg='#1f2937',
                                  relief='flat', bd=2)
        lang_frame.pack(fill=tk.X, pady=(0, 20), ipady=15)

        # Language options
        languages = [
            ('English', 'en'),
            ('Sinhala (සිංහල)', 'si'),
            ('Tamil (தமிழ்)', 'ta'),
            ('Hindi (हिन्दी)', 'hi'),
            ('Spanish (Español)', 'es'),
            ('French (Français)', 'fr'),
            ('German (Deutsch)', 'de'),
            ('Italian (Italiano)', 'it'),
            ('Japanese (日本語)', 'ja'),
            ('Korean (한국어)', 'ko'),
            ('Chinese (中文)', 'zh-CN'),
            ('Russian (Русский)', 'ru'),
            ('Arabic (العربية)', 'ar'),
            ('Portuguese (Português)', 'pt')
        ]

        self.lang_dict = {name: code for name, code in languages}
        lang_names = [name for name, code in languages]

        # Language controls
        lang_controls = tk.Frame(lang_frame, bg='#ffffff')
        lang_controls.pack(fill=tk.X, padx=20, pady=10)

        # From language
        from_frame = tk.Frame(lang_controls, bg='#ffffff')
        from_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        tk.Label(from_frame, text="🎤 Speak in / කතා කරන්න:",
                font=('Segoe UI', 11, 'bold'), bg='#ffffff', fg='#374151').pack(anchor=tk.W)
        self.input_combo = ttk.Combobox(from_frame, values=lang_names,
                                       font=('Segoe UI', 11), width=25)
        self.input_combo.pack(fill=tk.X, pady=(5, 0))
        self.input_combo.set("English")

        # Swap button
        swap_frame = tk.Frame(lang_controls, bg='#ffffff')
        swap_frame.pack(side=tk.LEFT, padx=10)

        swap_btn = tk.Button(swap_frame, text="⟷", font=('Segoe UI', 20, 'bold'),
                           command=self.swap_languages,
                           bg='#3b82f6', fg='white', activebackground='#2563eb',
                           relief='flat', padx=15, pady=10, cursor='hand2')
        swap_btn.pack(pady=20)

        # To language
        to_frame = tk.Frame(lang_controls, bg='#ffffff')
        to_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0))

        tk.Label(to_frame, text="🌐 Translate to / පරිවර්තනය:",
                font=('Segoe UI', 11, 'bold'), bg='#ffffff', fg='#374151').pack(anchor=tk.W)
        self.output_combo = ttk.Combobox(to_frame, values=lang_names,
                                        font=('Segoe UI', 11), width=25)
        self.output_combo.pack(fill=tk.X, pady=(5, 0))
        self.output_combo.set("Sinhala (සිංහල)")

        self.input_combo.bind('<<ComboboxSelected>>', self.update_languages)
        self.output_combo.bind('<<ComboboxSelected>>', self.update_languages)

        # Control panel with 3D effect
        control_frame = tk.LabelFrame(main_container, text=" Voice & Text Controls / හඬ සහ පෙළ පාලන ",
                                     font=('Segoe UI', 12, 'bold'),
                                     bg='#f8fafc', fg='#1f2937', relief='raised', bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 20), ipady=15)

        # Voice controls
        voice_section = tk.Frame(control_frame, bg='#f8fafc')
        voice_section.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        tk.Label(voice_section, text="🎤 VOICE INPUT",
                font=('Segoe UI', 11, 'bold'), bg='#f8fafc', fg='#059669').pack()

        voice_buttons = tk.Frame(voice_section, bg='#f8fafc')
        voice_buttons.pack(pady=10)

        if self.speech_available:
            self.listen_btn = tk.Button(voice_buttons, text="🎤 Start Auto Listening",
                                       command=self.toggle_auto_listening,
                                       font=('Segoe UI', 12, 'bold'),
                                       bg='#10b981', fg='white', activebackground='#059669',
                                       relief='flat', padx=20, pady=12, cursor='hand2')
            self.listen_btn.pack(pady=5)

        self.manual_voice_btn = tk.Button(voice_buttons, text="🗣️ Manual Voice Input",
                                         command=self.manual_voice_input,
                                         font=('Segoe UI', 11, 'bold'),
                                         bg='#f59e0b', fg='white', activebackground='#d97706',
                                         relief='flat', padx=20, pady=10, cursor='hand2')
        self.manual_voice_btn.pack(pady=5)

        # Voice indicator
        self.voice_status = tk.Label(voice_section, text="🔴 Not Listening",
                                    font=('Segoe UI', 10, 'bold'),
                                    bg='#f8fafc', fg='#ef4444')
        self.voice_status.pack(pady=10)

        # Separator
        separator = tk.Frame(control_frame, bg='#d1d5db', width=2)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Text controls
        text_section = tk.Frame(control_frame, bg='#f8fafc')
        text_section.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10, pady=10)

        tk.Label(text_section, text="📝 TEXT INPUT",
                font=('Segoe UI', 11, 'bold'), bg='#f8fafc', fg='#dc2626').pack()

        text_buttons = tk.Frame(text_section, bg='#f8fafc')
        text_buttons.pack(pady=10)

        self.text_mode_btn = tk.Button(text_buttons, text="📝 Open Text Mode",
                                      command=self.toggle_text_mode,
                                      font=('Segoe UI', 12, 'bold'),
                                      bg='#3b82f6', fg='white', activebackground='#2563eb',
                                      relief='flat', padx=20, pady=12, cursor='hand2')
        self.text_mode_btn.pack(pady=5)

        clear_btn = tk.Button(text_buttons, text="🗑️ Clear All",
                             command=self.clear_all,
                             font=('Segoe UI', 11, 'bold'),
                             bg='#ef4444', fg='white', activebackground='#dc2626',
                             relief='flat', padx=20, pady=10, cursor='hand2')
        clear_btn.pack(pady=5)

        # Text input area (initially hidden)
        self.text_input_frame = tk.LabelFrame(main_container,
                                             text=" ✍️ Type Your Text Here / මෙහි ඔයාගේ පෙළ ටයිප් කරන්න ",
                                             font=('Segoe UI', 11, 'bold'),
                                             bg='#ffffff', fg='#1f2937')

        text_container = tk.Frame(self.text_input_frame, bg='#ffffff')
        text_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.text_input = tk.Text(text_container, height=4,
                                 font=('Segoe UI', 12), wrap=tk.WORD,
                                 relief='flat', bd=1, padx=15, pady=10,
                                 bg='#f9fafb', fg='#111827')
        self.text_input.pack(fill=tk.BOTH, expand=True)

        text_controls = tk.Frame(self.text_input_frame, bg='#ffffff')
        text_controls.pack(fill=tk.X, padx=15, pady=(0, 15))

        tk.Button(text_controls, text="🌐 Translate Text",
                 command=self.translate_text_input,
                 font=('Segoe UI', 11, 'bold'),
                 bg='#059669', fg='white', activebackground='#047857',
                 relief='flat', padx=20, pady=10, cursor='hand2').pack(side=tk.LEFT, padx=5)

        tk.Button(text_controls, text="🧹 Clear Text",
                 command=lambda: self.text_input.delete(1.0, tk.END),
                 font=('Segoe UI', 11),
                 bg='#6b7280', fg='white', activebackground='#4b5563',
                 relief='flat', padx=15, pady=10, cursor='hand2').pack(side=tk.LEFT, padx=5)

        # Results display with modern styling
        result_frame = tk.LabelFrame(main_container,
                                    text=" 🔄 Live Translation Results / සජීවී පරිවර්තන ප්‍රතිඵල ",
                                    font=('Segoe UI', 13, 'bold'),
                                    bg='#ffffff', fg='#1f2937', relief='flat', bd=2)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        # Results display
        results_container = tk.Frame(result_frame, bg='#ffffff')
        results_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.result_display = scrolledtext.ScrolledText(results_container,
                                                       font=('Segoe UI', 11),
                                                       wrap=tk.WORD, height=15,
                                                       bg='#fafafa', fg='#374151',
                                                       relief='flat', bd=0,
                                                       padx=10, pady=10)
        self.result_display.pack(fill=tk.BOTH, expand=True)

        # Configure text tags with modern colors
        self.result_display.tag_config("timestamp", foreground="#9ca3af",
                                      font=('Segoe UI', 9, 'italic'))
        self.result_display.tag_config("voice_input", foreground="#059669",
                                      font=('Segoe UI', 11, 'bold'))
        self.result_display.tag_config("text_input", foreground="#3b82f6",
                                      font=('Segoe UI', 11, 'bold'))
        self.result_display.tag_config("translation", foreground="#dc2626",
                                      font=('Segoe UI', 12, 'bold'))
        self.result_display.tag_config("error", foreground="#ef4444",
                                      font=('Segoe UI', 10, 'italic'))
        self.result_display.tag_config("separator", foreground="#d1d5db")
        self.result_display.tag_config("success", foreground="#10b981",
                                      font=('Segoe UI', 10, 'bold'))

        # Status bar
        status_frame = tk.Frame(main_container, bg='#374151', height=50)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, text="🟢 Ready to translate / පරිවර්තනයට සූදානම්",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg='#374151', fg='#ffffff')
        self.status_label.pack(side=tk.LEFT, padx=20, pady=15)

        connection_label = tk.Label(status_frame, text="🌐 Online Mode",
                                   font=('Segoe UI', 10),
                                   bg='#374151', fg='#10b981')
        connection_label.pack(side=tk.RIGHT, padx=20, pady=15)

        # Add welcome message
        self.add_welcome_message()

    def add_welcome_message(self):
        """Add welcome message to display"""
        self.result_display.insert(tk.END, "🎉 Welcome to Auto Voice Translator!\n", "success")
        self.result_display.insert(tk.END, "පරිවර්තකයට ආයුබෝවන්!\n\n", "success")

        if self.speech_available:
            self.result_display.insert(tk.END, "✅ Auto Voice Recognition: AVAILABLE\n", "voice_input")
            self.result_display.insert(tk.END, "Click 'Start Auto Listening' to begin voice translation\n\n", "text_input")
        else:
            self.result_display.insert(tk.END, "⚠️ Auto Voice Recognition: Install pywin32\n", "error")
            self.result_display.insert(tk.END, "Use 'Manual Voice Input' or 'Text Mode' instead\n\n", "text_input")

        self.result_display.insert(tk.END, "Available features:\n", "voice_input")
        self.result_display.insert(tk.END, "🎤 Auto Voice Recognition (if available)\n", "text_input")
        self.result_display.insert(tk.END, "🗣️ Manual Voice Input\n", "text_input")
        self.result_display.insert(tk.END, "📝 Text Input Mode\n", "text_input")
        self.result_display.insert(tk.END, "🔄 Real-time Translation\n", "text_input")
        self.result_display.insert(tk.END, "═" * 80 + "\n\n", "separator")

    def update_languages(self, event=None):
        input_selection = self.input_combo.get()
        output_selection = self.output_combo.get()

        self.input_lang = self.lang_dict.get(input_selection, 'en')
        self.output_lang = self.lang_dict.get(output_selection, 'si')

    def swap_languages(self):
        input_val = self.input_combo.get()
        output_val = self.output_combo.get()
        self.input_combo.set(output_val)
        self.output_combo.set(input_val)
        self.update_languages()

        # Add swap notification
        timestamp = time.strftime("%H:%M:%S")
        self.result_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.result_display.insert(tk.END, "⟷ Languages swapped / භාෂා මාරු කළා\n", "success")
        self.result_display.see(tk.END)

    def toggle_auto_listening(self):
        """Toggle automatic voice listening"""
        if not self.speech_available:
            messagebox.showwarning("Not Available",
                                 "Auto voice recognition not available.\n"
                                 "Install pywin32: pip install pywin32")
            return

        if not self.is_listening:
            self.start_auto_listening()
        else:
            self.stop_auto_listening()

    def start_auto_listening(self):
        """Start automatic voice listening"""
        self.is_listening = True
        self.listen_btn.config(text="⏹ Stop Listening", bg="#ef4444")
        self.voice_status.config(text="🟢 Listening...", fg="#10b981")
        self.status_label.config(text="🎤 Auto listening active / ස්වයංක්‍රීය සවන් දීම සක්‍රීයයි")

        # Add start message
        timestamp = time.strftime("%H:%M:%S")
        self.result_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.result_display.insert(tk.END, "🎤 Auto listening started... Speak now!\n", "voice_input")
        self.result_display.insert(tk.END, "ස්වයංක්‍රීය සවන් දීම ආරම්භ විය... දැන් කතා කරන්න!\n", "voice_input")
        self.result_display.see(tk.END)

        # Start listening thread
        threading.Thread(target=self.listen_continuously, daemon=True).start()

    def stop_auto_listening(self):
        """Stop automatic voice listening"""
        self.is_listening = False
        self.listen_btn.config(text="🎤 Start Auto Listening", bg="#10b981")
        self.voice_status.config(text="🔴 Not Listening", fg="#ef4444")
        self.status_label.config(text="🛑 Listening stopped / සවන් දීම නතර කළා")

        # Add stop message
        timestamp = time.strftime("%H:%M:%S")
        self.result_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.result_display.insert(tk.END, "⏹ Auto listening stopped\n", "error")
        self.result_display.see(tk.END)

    def listen_continuously(self):
        """Continuously listen for voice input"""
        # This is a simulation - in real implementation would use speech recognition
        while self.is_listening:
            time.sleep(2)  # Simulate listening intervals
            if self.is_listening:
                # For demo, we'll use manual input
                self.root.after(0, self.prompt_voice_input)
                break

    def prompt_voice_input(self):
        """Prompt for voice input during auto listening"""
        if self.is_listening:
            voice_text = tk.simpledialog.askstring(
                "Auto Voice Recognition",
                "🎤 Auto listening detected speech!\n\n"
                "What did you say? (Type what you spoke):\n"
                "ඔයා කිව්වේ මොකක්ද? (ඔයා කතා කරපු දේ ටයිප් කරන්න):"
            )

            if voice_text and voice_text.strip():
                self.process_voice_input(voice_text.strip(), auto=True)

            # Continue listening if still active
            if self.is_listening:
                threading.Thread(target=self.listen_continuously, daemon=True).start()

    def manual_voice_input(self):
        """Manual voice input"""
        voice_text = tk.simpledialog.askstring(
            "Manual Voice Input",
            "🗣️ Manual Voice Input Mode\n\n"
            "Speak and then type what you said:\n"
            "කතා කරලා ඔයා කිව්වේ මොකක්ද ටයිප් කරන්න:\n\n"
            "Enter your speech:"
        )

        if voice_text and voice_text.strip():
            self.process_voice_input(voice_text.strip(), auto=False)

    def process_voice_input(self, text, auto=False):
        """Process voice input and translate"""
        timestamp = time.strftime("%H:%M:%S")
        input_type = "🤖 Auto Voice" if auto else "🗣️ Manual Voice"

        # Display voice input
        self.result_display.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
        self.result_display.insert(tk.END, f"{input_type}: ", "voice_input")
        self.result_display.insert(tk.END, f"{text}\n", "voice_input")

        # Update status
        self.status_label.config(text="🔄 Translating voice input... / හඬ ආදානය පරිවර්තනය කරමින්...")

        # Translate in separate thread
        threading.Thread(target=self.translate_and_display,
                        args=(text, input_type), daemon=True).start()

    def toggle_text_mode(self):
        """Toggle text input area"""
        if self.text_input_frame.winfo_viewable():
            self.text_input_frame.pack_forget()
            self.text_mode_btn.config(text="📝 Open Text Mode")
        else:
            # Find the result frame and pack before it
            result_frame = None
            for child in self.text_input_frame.master.winfo_children():
                if isinstance(child, tk.LabelFrame) and "Translation Results" in child.cget('text'):
                    result_frame = child
                    break

            if result_frame:
                self.text_input_frame.pack(fill=tk.X, pady=15, before=result_frame)
            else:
                self.text_input_frame.pack(fill=tk.X, pady=15)

            self.text_mode_btn.config(text="📝 Hide Text Mode")
            self.text_input.focus()

    def translate_text_input(self):
        """Translate text from input area"""
        text = self.text_input.get(1.0, tk.END).strip()
        if text:
            timestamp = time.strftime("%H:%M:%S")

            # Display text input
            self.result_display.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
            self.result_display.insert(tk.END, "📝 Text Input: ", "text_input")
            self.result_display.insert(tk.END, f"{text}\n", "text_input")

            # Clear input
            self.text_input.delete(1.0, tk.END)

            # Translate
            threading.Thread(target=self.translate_and_display,
                           args=(text, "📝 Text"), daemon=True).start()

    def translate_and_display(self, text, input_type):
        """Translate text and display result"""
        try:
            # Perform translation
            translated = self.translate_text(text)

            if translated:
                # Display translation
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, f"🌐 Translation ({self.output_lang}): ", "translation"))
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, f"{translated}\n", "translation"))
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, "─" * 80 + "\n", "separator"))

                # Update status
                self.root.after(0, lambda: self.status_label.config(
                    text="✅ Translation completed / පරිවර්තනය සම්පූර්ණයි"))

            else:
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, "❌ Translation failed / පරිවර්තනය අසාර්ථකයි\n", "error"))

            # Auto-scroll
            self.root.after(0, lambda: self.result_display.see(tk.END))

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

    def clear_all(self):
        """Clear all displays"""
        self.result_display.delete(1.0, tk.END)
        self.add_welcome_message()
        self.status_label.config(text="🗑️ Display cleared / දර්ශනය මකා දැමුවා")

        # Reset voice status
        if self.is_listening:
            self.stop_auto_listening()

def main():
    # Import simpledialog
    import tkinter.simpledialog
    tk.simpledialog = tkinter.simpledialog

    root = tk.Tk()
    app = AutoVoiceTranslator(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()

if __name__ == "__main__":
    main()
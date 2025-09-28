import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import threading
import time
import urllib.request
import urllib.parse
import json
import subprocess
import os
import tempfile

class VoiceEnabledTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice & Text Translator - හඬ සහ පෙළ පරිවර්තකය")
        self.root.geometry("950x700")
        self.root.configure(bg='#f5f5f5')

        self.input_lang = 'en'
        self.output_lang = 'si'
        self.is_recording = False

        self.setup_ui()

    def setup_ui(self):
        # Main container with modern styling
        main_container = tk.Frame(self.root, bg='#f5f5f5')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Header
        header_frame = tk.Frame(main_container, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="🎤 Voice & Text Translator",
                              font=('Segoe UI', 20, 'bold'),
                              fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        subtitle_label = tk.Label(header_frame, text="හඬ සහ පෙළ පරිවර්තකය",
                                 font=('Segoe UI', 12),
                                 fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()

        # Language selection with modern styling
        lang_frame = tk.LabelFrame(main_container, text=" Language Settings / භාෂා සැකසුම් ",
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='#ecf0f1', fg='#2c3e50',
                                  relief='flat', bd=1)
        lang_frame.pack(fill=tk.X, pady=(0, 15), padx=5, ipady=10)

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
            ('Portuguese (Português)', 'pt'),
            ('Dutch (Nederlands)', 'nl')
        ]

        self.lang_dict = {name: code for name, code in languages}
        lang_names = [name for name, code in languages]

        # From language
        from_frame = tk.Frame(lang_frame, bg='#ecf0f1')
        from_frame.pack(side=tk.LEFT, padx=20, expand=True, fill=tk.X)

        tk.Label(from_frame, text="Speak in / කතා කරන්න:",
                font=('Segoe UI', 10, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(anchor=tk.W)
        self.input_combo = ttk.Combobox(from_frame, values=lang_names,
                                       font=('Segoe UI', 10), width=25)
        self.input_combo.pack(fill=tk.X, pady=5)
        self.input_combo.set("English")

        # Swap button
        swap_frame = tk.Frame(lang_frame, bg='#ecf0f1')
        swap_frame.pack(side=tk.LEFT, padx=10)

        swap_btn = tk.Button(swap_frame, text="⇄", font=('Segoe UI', 16, 'bold'),
                           command=self.swap_languages,
                           bg='#3498db', fg='white',
                           relief='flat', padx=10, pady=5,
                           cursor='hand2')
        swap_btn.pack(pady=25)

        # To language
        to_frame = tk.Frame(lang_frame, bg='#ecf0f1')
        to_frame.pack(side=tk.LEFT, padx=20, expand=True, fill=tk.X)

        tk.Label(to_frame, text="Translate to / පරිවර්තනය:",
                font=('Segoe UI', 10, 'bold'), bg='#ecf0f1', fg='#2c3e50').pack(anchor=tk.W)
        self.output_combo = ttk.Combobox(to_frame, values=lang_names,
                                        font=('Segoe UI', 10), width=25)
        self.output_combo.pack(fill=tk.X, pady=5)
        self.output_combo.set("Sinhala (සිංහල)")

        self.input_combo.bind('<<ComboboxSelected>>', self.update_languages)
        self.output_combo.bind('<<ComboboxSelected>>', self.update_languages)

        # Control panel with modern buttons
        control_frame = tk.Frame(main_container, bg='#f5f5f5')
        control_frame.pack(fill=tk.X, pady=(0, 15))

        # Voice controls
        voice_frame = tk.LabelFrame(control_frame, text=" Voice Input / හඬ ඇතුළත් කිරීම ",
                                   font=('Segoe UI', 10, 'bold'),
                                   bg='#e8f6f3', fg='#27ae60')
        voice_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 7))

        # Voice buttons
        voice_btn_frame = tk.Frame(voice_frame, bg='#e8f6f3')
        voice_btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.record_btn = tk.Button(voice_btn_frame, text="🎤 Start Recording",
                                   command=self.toggle_recording,
                                   font=('Segoe UI', 11, 'bold'),
                                   bg='#27ae60', fg='white',
                                   relief='flat', padx=20, pady=10,
                                   cursor='hand2')
        self.record_btn.pack(side=tk.LEFT, padx=5)

        self.quick_voice_btn = tk.Button(voice_btn_frame, text="⚡ Quick Voice",
                                        command=self.quick_voice_input,
                                        font=('Segoe UI', 11, 'bold'),
                                        bg='#f39c12', fg='white',
                                        relief='flat', padx=15, pady=10,
                                        cursor='hand2')
        self.quick_voice_btn.pack(side=tk.LEFT, padx=5)

        # Recording indicator
        self.record_indicator = tk.Label(voice_frame, text="● Ready to record",
                                        font=('Segoe UI', 9),
                                        bg='#e8f6f3', fg='#27ae60')
        self.record_indicator.pack(pady=5)

        # Text controls
        text_frame = tk.LabelFrame(control_frame, text=" Text Input / පෙළ ඇතුළත් කිරීම ",
                                  font=('Segoe UI', 10, 'bold'),
                                  bg='#fdf2e9', fg='#e67e22')
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(7, 0))

        text_btn_frame = tk.Frame(text_frame, bg='#fdf2e9')
        text_btn_frame.pack(fill=tk.X, padx=10, pady=10)

        self.text_mode_btn = tk.Button(text_btn_frame, text="📝 Text Mode",
                                      command=self.toggle_text_mode,
                                      font=('Segoe UI', 11, 'bold'),
                                      bg='#e67e22', fg='white',
                                      relief='flat', padx=20, pady=10,
                                      cursor='hand2')
        self.text_mode_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = tk.Button(text_btn_frame, text="🗑️ Clear All",
                                  command=self.clear_all,
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='#e74c3c', fg='white',
                                  relief='flat', padx=15, pady=10,
                                  cursor='hand2')
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Text input area (initially hidden)
        self.text_input_frame = tk.LabelFrame(main_container,
                                             text=" Type your text here / මෙහි ඔයාගේ පෙළ ටයිප් කරන්න ",
                                             font=('Segoe UI', 10, 'bold'),
                                             bg='#f8f9fa', fg='#495057')

        text_input_container = tk.Frame(self.text_input_frame, bg='#f8f9fa')
        text_input_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.text_input = tk.Text(text_input_container, height=4,
                                 font=('Segoe UI', 12), wrap=tk.WORD,
                                 relief='flat', bd=1, padx=10, pady=10)
        self.text_input.pack(fill=tk.BOTH, expand=True)

        text_controls = tk.Frame(self.text_input_frame, bg='#f8f9fa')
        text_controls.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(text_controls, text="🌐 Translate Text",
                 command=self.translate_text_input,
                 font=('Segoe UI', 10, 'bold'),
                 bg='#007bff', fg='white',
                 relief='flat', padx=15, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)

        tk.Button(text_controls, text="Clear Input",
                 command=lambda: self.text_input.delete(1.0, tk.END),
                 font=('Segoe UI', 10),
                 bg='#6c757d', fg='white',
                 relief='flat', padx=15, pady=8,
                 cursor='hand2').pack(side=tk.LEFT, padx=5)

        # Results display with tabs
        result_frame = tk.LabelFrame(main_container,
                                    text=" Translation Results / පරිවර්තන ප්‍රතිඵල ",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg='#ffffff', fg='#2c3e50')
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        # Create notebook for tabs
        self.notebook = ttk.Notebook(result_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Live translation tab
        live_tab = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(live_tab, text="🔄 Live Translation")

        self.result_display = scrolledtext.ScrolledText(live_tab,
                                                       font=('Segoe UI', 11),
                                                       wrap=tk.WORD, height=15,
                                                       bg='#ffffff', fg='#2c3e50')
        self.result_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Configure text tags with better styling
        self.result_display.tag_config("timestamp", foreground="#6c757d",
                                      font=('Segoe UI', 9, 'italic'))
        self.result_display.tag_config("input", foreground="#007bff",
                                      font=('Segoe UI', 11))
        self.result_display.tag_config("output", foreground="#28a745",
                                      font=('Segoe UI', 12, 'bold'))
        self.result_display.tag_config("voice", foreground="#e67e22",
                                      font=('Segoe UI', 11, 'bold'))
        self.result_display.tag_config("error", foreground="#dc3545",
                                      font=('Segoe UI', 10, 'italic'))
        self.result_display.tag_config("separator", foreground="#dee2e6")

        # History tab
        history_tab = tk.Frame(self.notebook, bg='#ffffff')
        self.notebook.add(history_tab, text="📚 History")

        self.history_display = scrolledtext.ScrolledText(history_tab,
                                                        font=('Segoe UI', 10),
                                                        wrap=tk.WORD, height=15,
                                                        bg='#f8f9fa', fg='#495057')
        self.history_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Status bar with modern styling
        status_frame = tk.Frame(main_container, bg='#343a40', height=40)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, text="🟢 Ready / සූදානම්",
                                    font=('Segoe UI', 10, 'bold'),
                                    bg='#343a40', fg='#ffffff')
        self.status_label.pack(side=tk.LEFT, padx=15, pady=10)

        connection_label = tk.Label(status_frame, text="🌐 Online",
                                   font=('Segoe UI', 9),
                                   bg='#343a40', fg='#28a745')
        connection_label.pack(side=tk.RIGHT, padx=15, pady=10)

        # History storage
        self.translation_history = []

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

    def toggle_recording(self):
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        self.is_recording = True
        self.record_btn.config(text="⏹ Stop Recording", bg="#e74c3c")
        self.record_indicator.config(text="🔴 Recording... Speak now!", fg="#e74c3c")
        self.status_label.config(text="🎤 Recording... / පටිගත කරමින්...")

        # Simulate recording (in real implementation, use actual speech recognition)
        self.root.after(100, self.simulate_recording)

    def simulate_recording(self):
        if self.is_recording:
            # Flash indicator
            current_color = self.record_indicator.cget('fg')
            new_color = '#e74c3c' if current_color == '#dc3545' else '#dc3545'
            self.record_indicator.config(fg=new_color)
            self.root.after(500, self.simulate_recording)

    def stop_recording(self):
        self.is_recording = False
        self.record_btn.config(text="🎤 Start Recording", bg="#27ae60")
        self.record_indicator.config(text="● Processing...", fg="#f39c12")
        self.status_label.config(text="🔄 Processing speech... / කථනය සකසමින්...")

        # Simulate speech processing
        self.root.after(1000, self.process_recorded_speech)

    def process_recorded_speech(self):
        # For demo purposes, show input dialog
        self.quick_voice_input()

    def quick_voice_input(self):
        """Quick voice input using simple dialog"""
        dialog_text = (
            "🎤 Voice Input Mode\n\n"
            "1. Click OK to activate voice input\n"
            "2. Speak clearly into your microphone\n"
            "3. Type what you said in the text box below\n"
            "4. Or use Windows Speech Recognition\n\n"
            "Enter your spoken text:"
        )

        voice_text = simpledialog.askstring("Voice Input", dialog_text,
                                           initialvalue="")

        if voice_text and voice_text.strip():
            self.process_voice_input(voice_text.strip())
        else:
            self.status_label.config(text="🟡 Voice input cancelled / හඬ ආදානය අවලංගු කරන ලදී")
            self.record_indicator.config(text="● Ready to record", fg="#27ae60")

    def process_voice_input(self, text):
        """Process voice input text"""
        timestamp = time.strftime("%H:%M:%S")

        # Display voice input
        self.result_display.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
        self.result_display.insert(tk.END, "🎤 Voice Input: ", "voice")
        self.result_display.insert(tk.END, f"{text}\n", "input")

        # Update status
        self.status_label.config(text="🔄 Translating voice input... / හඬ ආදානය පරිවර්තනය කරමින්...")
        self.record_indicator.config(text="● Translating...", fg="#f39c12")

        # Translate in separate thread
        thread = threading.Thread(target=self.translate_and_display,
                                 args=(text, "🎤 Voice"), daemon=True)
        thread.start()

    def toggle_text_mode(self):
        """Toggle text input area"""
        if self.text_input_frame.winfo_viewable():
            self.text_input_frame.pack_forget()
            self.text_mode_btn.config(text="📝 Text Mode")
        else:
            # Pack before the result frame
            result_frame = self.notebook.master
            self.text_input_frame.pack(fill=tk.X, pady=10, before=result_frame)
            self.text_mode_btn.config(text="📝 Hide Text")
            self.text_input.focus()

    def translate_text_input(self):
        """Translate text from input area"""
        text = self.text_input.get(1.0, tk.END).strip()
        if text:
            timestamp = time.strftime("%H:%M:%S")

            # Display text input
            self.result_display.insert(tk.END, f"\n[{timestamp}] ", "timestamp")
            self.result_display.insert(tk.END, "📝 Text Input: ", "input")
            self.result_display.insert(tk.END, f"{text}\n", "input")

            # Clear input
            self.text_input.delete(1.0, tk.END)

            # Translate
            thread = threading.Thread(target=self.translate_and_display,
                                     args=(text, "📝 Text"), daemon=True)
            thread.start()

    def translate_and_display(self, text, input_type):
        """Translate text and display result"""
        try:
            # Update status
            self.root.after(0, lambda: self.status_label.config(
                text="🔄 Translating... / පරිවර්තනය කරමින්..."))

            # Perform translation
            translated = self.translate_text(text)

            if translated:
                # Display translation
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, f"🌐 Translation ({self.output_lang}): ", "output"))
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, f"{translated}\n", "output"))
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, "─" * 80 + "\n", "separator"))

                # Add to history
                self.translation_history.append({
                    'time': time.strftime("%H:%M:%S"),
                    'input_type': input_type,
                    'original': text,
                    'translated': translated,
                    'from_lang': self.input_lang,
                    'to_lang': self.output_lang
                })

                # Update history display
                self.update_history()

                # Update status
                self.root.after(0, lambda: self.status_label.config(
                    text="✅ Translation complete / පරිවර්තනය සම්පූර්ණයි"))

                # Reset voice indicator
                self.root.after(0, lambda: self.record_indicator.config(
                    text="● Ready to record", fg="#27ae60"))

            else:
                self.root.after(0, lambda: self.result_display.insert(
                    tk.END, "❌ Translation failed / පරිවර්තනය අසාර්ථකයි\n", "error"))
                self.root.after(0, lambda: self.status_label.config(
                    text="❌ Translation error / පරිවර්තන දෝෂය"))

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

    def update_history(self):
        """Update history display"""
        self.history_display.delete(1.0, tk.END)

        for i, item in enumerate(self.translation_history[-20:], 1):  # Show last 20
            self.history_display.insert(tk.END, f"{i}. [{item['time']}] {item['input_type']}\n")
            self.history_display.insert(tk.END, f"   {item['from_lang']}: {item['original']}\n")
            self.history_display.insert(tk.END, f"   {item['to_lang']}: {item['translated']}\n")
            self.history_display.insert(tk.END, "   " + "─" * 60 + "\n\n")

    def clear_all(self):
        """Clear all displays"""
        self.result_display.delete(1.0, tk.END)
        self.history_display.delete(1.0, tk.END)
        self.translation_history.clear()
        self.status_label.config(text="🗑️ Cleared / මකා දැමුවා")

        # Reset voice indicator
        self.record_indicator.config(text="● Ready to record", fg="#27ae60")
        self.is_recording = False
        self.record_btn.config(text="🎤 Start Recording", bg="#27ae60")

def main():
    root = tk.Tk()
    app = VoiceEnabledTranslator(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Add welcome message
    app.result_display.insert(tk.END, "🎉 Welcome to Voice & Text Translator!\n", "output")
    app.result_display.insert(tk.END, "පරිවර්තකයට ආයුබෝවන්!\n\n", "output")
    app.result_display.insert(tk.END, "Choose your input method:\n", "input")
    app.result_display.insert(tk.END, "🎤 Voice: Click 'Quick Voice' or 'Start Recording'\n", "voice")
    app.result_display.insert(tk.END, "📝 Text: Click 'Text Mode' to type\n", "input")
    app.result_display.insert(tk.END, "─" * 80 + "\n", "separator")

    root.mainloop()

if __name__ == "__main__":
    main()
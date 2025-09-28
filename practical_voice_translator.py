import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import urllib.request
import urllib.parse
import json
import subprocess
import os

class PracticalVoiceTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Practical Voice Translator - ප්‍රායෝගික හඬ පරිවර්තකය")
        self.root.geometry("1000x750")
        self.root.configure(bg='#f8fafc')

        self.input_lang = 'en'
        self.output_lang = 'si'
        self.is_recording = False

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg='#f8fafc')
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        # Header
        header_frame = tk.Frame(main_container, bg='#1e40af', height=90)
        header_frame.pack(fill=tk.X, pady=(0, 25))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="🎙️ Practical Voice Translator",
                              font=('Segoe UI', 22, 'bold'),
                              fg='white', bg='#1e40af')
        title_label.pack(expand=True)

        subtitle_label = tk.Label(header_frame, text="ප්‍රායෝගික හඬ පරිවර්තකය - Easy Voice Translation",
                                 font=('Segoe UI', 11),
                                 fg='#dbeafe', bg='#1e40af')
        subtitle_label.pack()

        # Language selection
        lang_frame = tk.LabelFrame(main_container, text=" 🌐 Language Settings / භාෂා සැකසුම් ",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='#ffffff', fg='#1f2937', padx=20, pady=15)
        lang_frame.pack(fill=tk.X, pady=(0, 20))

        # Languages
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

        lang_controls = tk.Frame(lang_frame, bg='#ffffff')
        lang_controls.pack(fill=tk.X, pady=10)

        # From language
        from_frame = tk.Frame(lang_controls, bg='#ffffff')
        from_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 15))

        tk.Label(from_frame, text="🗣️ Speak in:",
                font=('Segoe UI', 11, 'bold'), bg='#ffffff').pack(anchor=tk.W)
        self.input_combo = ttk.Combobox(from_frame, values=lang_names,
                                       font=('Segoe UI', 11), width=20)
        self.input_combo.pack(fill=tk.X, pady=5)
        self.input_combo.set("English")

        # Swap button
        swap_btn = tk.Button(lang_controls, text="⇄", font=('Segoe UI', 16, 'bold'),
                           command=self.swap_languages,
                           bg='#3b82f6', fg='white', relief='flat',
                           padx=15, pady=5, cursor='hand2')
        swap_btn.pack(side=tk.LEFT, padx=15, pady=20)

        # To language
        to_frame = tk.Frame(lang_controls, bg='#ffffff')
        to_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(15, 0))

        tk.Label(to_frame, text="🌐 Translate to:",
                font=('Segoe UI', 11, 'bold'), bg='#ffffff').pack(anchor=tk.W)
        self.output_combo = ttk.Combobox(to_frame, values=lang_names,
                                        font=('Segoe UI', 11), width=20)
        self.output_combo.pack(fill=tk.X, pady=5)
        self.output_combo.set("Sinhala (සිංහල)")

        self.input_combo.bind('<<ComboboxSelected>>', self.update_languages)
        self.output_combo.bind('<<ComboboxSelected>>', self.update_languages)

        # Main control panel
        control_frame = tk.Frame(main_container, bg='#f8fafc')
        control_frame.pack(fill=tk.X, pady=(0, 20))

        # Voice input section
        voice_frame = tk.LabelFrame(control_frame, text=" 🎤 Voice Input Methods / හඬ ආදාන ක්‍රම ",
                                   font=('Segoe UI', 12, 'bold'),
                                   bg='#ecfdf5', fg='#065f46', padx=20, pady=15)
        voice_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Voice method buttons
        voice_methods = tk.Frame(voice_frame, bg='#ecfdf5')
        voice_methods.pack(fill=tk.X, pady=10)

        # Method 1: Windows Voice Recorder
        self.recorder_btn = tk.Button(voice_methods, text="🎙️ Windows Voice Recorder",
                                     command=self.use_windows_recorder,
                                     font=('Segoe UI', 11, 'bold'),
                                     bg='#10b981', fg='white', relief='flat',
                                     padx=20, pady=12, cursor='hand2')
        self.recorder_btn.pack(fill=tk.X, pady=3)

        # Method 2: Manual Voice Input
        manual_btn = tk.Button(voice_methods, text="🗣️ Manual Voice Input",
                              command=self.manual_voice_input,
                              font=('Segoe UI', 11, 'bold'),
                              bg='#f59e0b', fg='white', relief='flat',
                              padx=20, pady=12, cursor='hand2')
        manual_btn.pack(fill=tk.X, pady=3)

        # Method 3: Voice Commands
        cmd_btn = tk.Button(voice_methods, text="⚡ Quick Voice Commands",
                           command=self.show_voice_commands,
                           font=('Segoe UI', 11, 'bold'),
                           bg='#8b5cf6', fg='white', relief='flat',
                           padx=20, pady=12, cursor='hand2')
        cmd_btn.pack(fill=tk.X, pady=3)

        # Recording status
        self.record_status = tk.Label(voice_frame, text="🔴 Ready to record",
                                     font=('Segoe UI', 10, 'bold'),
                                     bg='#ecfdf5', fg='#059669')
        self.record_status.pack(pady=10)

        # Text input section
        text_frame = tk.LabelFrame(control_frame, text=" 📝 Text Input / පෙළ ආදානය ",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg='#fef3c7', fg='#92400e', padx=20, pady=15)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        text_methods = tk.Frame(text_frame, bg='#fef3c7')
        text_methods.pack(fill=tk.X, pady=10)

        self.text_mode_btn = tk.Button(text_methods, text="📝 Open Text Editor",
                                      command=self.toggle_text_mode,
                                      font=('Segoe UI', 11, 'bold'),
                                      bg='#f59e0b', fg='white', relief='flat',
                                      padx=20, pady=12, cursor='hand2')
        self.text_mode_btn.pack(fill=tk.X, pady=3)

        paste_btn = tk.Button(text_methods, text="📋 Paste & Translate",
                             command=self.paste_and_translate,
                             font=('Segoe UI', 11, 'bold'),
                             bg='#8b5cf6', fg='white', relief='flat',
                             padx=20, pady=12, cursor='hand2')
        paste_btn.pack(fill=tk.X, pady=3)

        clear_btn = tk.Button(text_methods, text="🗑️ Clear All",
                             command=self.clear_all,
                             font=('Segoe UI', 11, 'bold'),
                             bg='#ef4444', fg='white', relief='flat',
                             padx=20, pady=12, cursor='hand2')
        clear_btn.pack(fill=tk.X, pady=3)

        # Text input area (hidden initially)
        self.text_input_frame = tk.LabelFrame(main_container,
                                             text=" ✏️ Text Editor / පෙළ සංස්කාරක ",
                                             font=('Segoe UI', 11, 'bold'),
                                             bg='#ffffff', fg='#1f2937')

        text_container = tk.Frame(self.text_input_frame, bg='#ffffff')
        text_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.text_input = tk.Text(text_container, height=4,
                                 font=('Segoe UI', 12), wrap=tk.WORD,
                                 bg='#f9fafb', relief='flat', bd=1,
                                 padx=10, pady=10)
        self.text_input.pack(fill=tk.BOTH, expand=True)

        text_controls = tk.Frame(self.text_input_frame, bg='#ffffff')
        text_controls.pack(fill=tk.X, padx=15, pady=(0, 15))

        tk.Button(text_controls, text="🌐 Translate",
                 command=self.translate_text_input,
                 font=('Segoe UI', 11, 'bold'),
                 bg='#059669', fg='white', relief='flat',
                 padx=20, pady=10, cursor='hand2').pack(side=tk.LEFT, padx=5)

        tk.Button(text_controls, text="Clear",
                 command=lambda: self.text_input.delete(1.0, tk.END),
                 font=('Segoe UI', 11),
                 bg='#6b7280', fg='white', relief='flat',
                 padx=15, pady=10, cursor='hand2').pack(side=tk.LEFT, padx=5)

        # Results display
        result_frame = tk.LabelFrame(main_container,
                                    text=" 🔄 Translation Results / පරිවර්තන ප්‍රතිඵල ",
                                    font=('Segoe UI', 13, 'bold'),
                                    bg='#ffffff', fg='#1f2937')
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))

        results_container = tk.Frame(result_frame, bg='#ffffff')
        results_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        self.result_display = scrolledtext.ScrolledText(results_container,
                                                       font=('Segoe UI', 11),
                                                       wrap=tk.WORD, height=15,
                                                       bg='#fafafa', relief='flat',
                                                       padx=10, pady=10)
        self.result_display.pack(fill=tk.BOTH, expand=True)

        # Text tags
        self.result_display.tag_config("timestamp", foreground="#9ca3af", font=('Segoe UI', 9))
        self.result_display.tag_config("voice", foreground="#10b981", font=('Segoe UI', 11, 'bold'))
        self.result_display.tag_config("text", foreground="#3b82f6", font=('Segoe UI', 11, 'bold'))
        self.result_display.tag_config("translation", foreground="#dc2626", font=('Segoe UI', 12, 'bold'))
        self.result_display.tag_config("error", foreground="#ef4444")
        self.result_display.tag_config("success", foreground="#059669", font=('Segoe UI', 10, 'bold'))
        self.result_display.tag_config("separator", foreground="#d1d5db")

        # Status bar
        status_frame = tk.Frame(main_container, bg='#374151', height=45)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, text="🟢 Ready / සූදානම්",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg='#374151', fg='#ffffff')
        self.status_label.pack(side=tk.LEFT, padx=20, pady=12)

        # Add welcome message
        self.add_welcome_message()

    def add_welcome_message(self):
        self.result_display.insert(tk.END, "🎉 Welcome to Practical Voice Translator!\n", "success")
        self.result_display.insert(tk.END, "ප්‍රායෝගික හඬ පරිවර්තකයට ආයුබෝවන්!\n\n", "success")
        self.result_display.insert(tk.END, "Available methods / පවතින ක්‍රම:\n", "voice")
        self.result_display.insert(tk.END, "🎙️ Windows Voice Recorder - Record your voice\n", "text")
        self.result_display.insert(tk.END, "🗣️ Manual Voice Input - Type what you said\n", "text")
        self.result_display.insert(tk.END, "⚡ Quick Voice Commands - Common phrases\n", "text")
        self.result_display.insert(tk.END, "📝 Text Editor - Direct typing\n", "text")
        self.result_display.insert(tk.END, "📋 Paste & Translate - Clipboard content\n", "text")
        self.result_display.insert(tk.END, "═" * 70 + "\n\n", "separator")

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
        self.add_message("⇄ Languages swapped / භාෂා මාරු කළා", "success")

    def use_windows_recorder(self):
        """Open Windows Voice Recorder"""
        try:
            self.record_status.config(text="🎙️ Opening Windows Voice Recorder...", fg="#f59e0b")
            self.status_label.config(text="🎙️ Opening voice recorder / හඬ පටිගත කරන්නා විවෘත කරමින්...")

            # Try to open Windows Voice Recorder
            try:
                subprocess.Popen(['ms-voicerecorder:'])
                self.add_message("🎙️ Windows Voice Recorder opened! / Windows හඬ පටිගත කරන්නා විවෘත කළා!", "voice")
                self.add_message("1. Record your voice / ඔයාගේ හඬ පටිගත කරන්න", "text")
                self.add_message("2. Listen to it / ඒක අහන්න", "text")
                self.add_message("3. Type what you said below / ඔයා කිව්වේ මොකක්ද පහතින් ටයිප් කරන්න", "text")

                # Show input dialog after a delay
                self.root.after(3000, self.prompt_recorded_text)

            except:
                # Fallback: open Sound Recorder
                subprocess.Popen(['SoundRecorder.exe'])
                self.add_message("🎙️ Sound Recorder opened! Record your voice and type below.", "voice")
                self.root.after(3000, self.prompt_recorded_text)

        except Exception as e:
            messagebox.showerror("Error", f"Could not open voice recorder: {e}")
            self.manual_voice_input()

    def prompt_recorded_text(self):
        """Prompt user to type what they recorded"""
        self.record_status.config(text="⌨️ Type what you recorded", fg="#3b82f6")

        dialog_text = (
            "🎙️ Voice Recording Complete!\n\n"
            "Now type what you said in the recording:\n"
            "දැන් ඔයා පටිගත කරපු දේ ටයිප් කරන්න:\n\n"
            "What did you say?"
        )

        recorded_text = tk.simpledialog.askstring("Voice Input", dialog_text)

        if recorded_text and recorded_text.strip():
            self.process_voice_input(recorded_text.strip(), "🎙️ Recorded Voice")
            self.record_status.config(text="✅ Voice processed", fg="#059669")
        else:
            self.record_status.config(text="❌ No input received", fg="#ef4444")

    def manual_voice_input(self):
        """Manual voice input"""
        dialog_text = (
            "🗣️ Manual Voice Input\n\n"
            "Speak out loud, then type what you said:\n"
            "හයියෙන් කතා කරලා, ඔයා කිව්වේ මොකක්ද ටයිප් කරන්න:\n\n"
            "Enter your speech:"
        )

        voice_text = tk.simpledialog.askstring("Manual Voice Input", dialog_text)

        if voice_text and voice_text.strip():
            self.process_voice_input(voice_text.strip(), "🗣️ Manual Voice")

    def show_voice_commands(self):
        """Show common voice commands"""
        commands = {
            "English": [
                "Hello, how are you?",
                "What is your name?",
                "Thank you very much",
                "Where is the bathroom?",
                "How much does this cost?",
                "I need help",
                "Can you help me?",
                "What time is it?"
            ],
            "Common Phrases": [
                "Good morning",
                "Good evening",
                "Please help me",
                "I don't understand",
                "Speak slowly please",
                "How do you say this?",
                "Where can I find?",
                "This is delicious"
            ]
        }

        # Create command selection window
        cmd_window = tk.Toplevel(self.root)
        cmd_window.title("Quick Voice Commands")
        cmd_window.geometry("500x400")
        cmd_window.configure(bg='#f8fafc')

        tk.Label(cmd_window, text="⚡ Quick Voice Commands",
                font=('Segoe UI', 16, 'bold'),
                bg='#f8fafc', fg='#1f2937').pack(pady=10)

        tk.Label(cmd_window, text="Click any phrase to translate:",
                font=('Segoe UI', 11),
                bg='#f8fafc', fg='#6b7280').pack(pady=5)

        # Create scrollable frame
        canvas = tk.Canvas(cmd_window, bg='#ffffff')
        scrollbar = ttk.Scrollbar(cmd_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ffffff')

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for category, phrases in commands.items():
            tk.Label(scrollable_frame, text=f"📂 {category}",
                    font=('Segoe UI', 12, 'bold'),
                    bg='#ffffff', fg='#1f2937').pack(anchor=tk.W, padx=10, pady=(10, 5))

            for phrase in phrases:
                btn = tk.Button(scrollable_frame, text=phrase,
                               command=lambda p=phrase: self.select_command(p, cmd_window),
                               font=('Segoe UI', 10),
                               bg='#e5e7eb', fg='#374151',
                               relief='flat', padx=10, pady=5,
                               cursor='hand2')
                btn.pack(fill=tk.X, padx=20, pady=2)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def select_command(self, phrase, window):
        """Select a voice command"""
        window.destroy()
        self.process_voice_input(phrase, "⚡ Quick Command")

    def process_voice_input(self, text, input_type):
        """Process voice input"""
        self.add_message(f"{input_type}: {text}", "voice")
        self.status_label.config(text="🔄 Translating... / පරිවර්තනය කරමින්...")
        threading.Thread(target=self.translate_and_display, args=(text, input_type), daemon=True).start()

    def toggle_text_mode(self):
        """Toggle text input area"""
        if self.text_input_frame.winfo_viewable():
            self.text_input_frame.pack_forget()
            self.text_mode_btn.config(text="📝 Open Text Editor")
        else:
            # Find result frame and pack before it
            for child in self.text_input_frame.master.winfo_children():
                if isinstance(child, tk.LabelFrame) and "Translation Results" in child.cget('text'):
                    self.text_input_frame.pack(fill=tk.X, pady=15, before=child)
                    break
            else:
                self.text_input_frame.pack(fill=tk.X, pady=15)

            self.text_mode_btn.config(text="📝 Hide Text Editor")
            self.text_input.focus()

    def translate_text_input(self):
        """Translate text input"""
        text = self.text_input.get(1.0, tk.END).strip()
        if text:
            self.add_message(f"📝 Text Input: {text}", "text")
            self.text_input.delete(1.0, tk.END)
            threading.Thread(target=self.translate_and_display, args=(text, "📝 Text"), daemon=True).start()

    def paste_and_translate(self):
        """Paste from clipboard and translate"""
        try:
            clipboard_text = self.root.clipboard_get().strip()
            if clipboard_text:
                self.add_message(f"📋 Pasted: {clipboard_text}", "text")
                threading.Thread(target=self.translate_and_display,
                               args=(clipboard_text, "📋 Clipboard"), daemon=True).start()
            else:
                messagebox.showinfo("Empty Clipboard", "Clipboard is empty!")
        except:
            messagebox.showerror("Error", "Could not access clipboard!")

    def translate_and_display(self, text, input_type):
        """Translate and display result"""
        try:
            translated = self.translate_text(text)
            if translated:
                self.root.after(0, lambda: self.add_message(
                    f"🌐 Translation: {translated}", "translation"))
                self.root.after(0, lambda: self.status_label.config(
                    text="✅ Translation complete / පරිවර්තනය සම්පූර්ණයි"))
            else:
                self.root.after(0, lambda: self.add_message("❌ Translation failed", "error"))
        except Exception as e:
            self.root.after(0, lambda: self.add_message(f"❌ Error: {e}", "error"))

    def translate_text(self, text):
        """Translate using Google Translate"""
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

            translated_text = ''
            if result and len(result) > 0 and result[0]:
                for sentence in result[0]:
                    if sentence[0]:
                        translated_text += sentence[0]

            return translated_text
        except Exception as e:
            print(f"Translation error: {e}")
            return None

    def add_message(self, message, tag):
        """Add message to display"""
        timestamp = time.strftime("%H:%M:%S")
        self.result_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.result_display.insert(tk.END, f"{message}\n", tag)
        if tag == "translation":
            self.result_display.insert(tk.END, "─" * 70 + "\n", "separator")
        self.result_display.see(tk.END)

    def clear_all(self):
        """Clear all displays"""
        self.result_display.delete(1.0, tk.END)
        self.add_welcome_message()
        self.status_label.config(text="🗑️ Cleared / මකා දැමුවා")

def main():
    import tkinter.simpledialog
    tk.simpledialog = tkinter.simpledialog

    root = tk.Tk()
    app = PracticalVoiceTranslator(root)

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
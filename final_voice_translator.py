import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import urllib.request
import urllib.parse
import json
import subprocess
import os
import tempfile

class FinalVoiceTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Final Voice Translator - අවසාන හඬ පරිවර්තකය")
        self.root.geometry("1000x750")
        self.root.configure(bg='#f0f4f8')

        self.input_lang = 'en'
        self.output_lang = 'si'

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg='#f0f4f8')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_frame = tk.Frame(main_container, bg='#2563eb', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="🎯 Final Voice Translator",
                              font=('Segoe UI', 20, 'bold'),
                              fg='white', bg='#2563eb')
        title_label.pack(expand=True)

        subtitle_label = tk.Label(header_frame, text="අවසාන හඬ පරිවර්තකය - Multiple Voice Input Methods",
                                 font=('Segoe UI', 10),
                                 fg='#dbeafe', bg='#2563eb')
        subtitle_label.pack()

        # Language selection
        lang_frame = tk.LabelFrame(main_container, text=" 🌍 Language Settings / භාෂා සැකසුම් ",
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='#ffffff', fg='#1f2937', padx=15, pady=10)
        lang_frame.pack(fill=tk.X, pady=(0, 15))

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
        lang_controls.pack(fill=tk.X, pady=5)

        # From language
        from_frame = tk.Frame(lang_controls, bg='#ffffff')
        from_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        tk.Label(from_frame, text="Input:", font=('Segoe UI', 10, 'bold'), bg='#ffffff').pack(anchor=tk.W)
        self.input_combo = ttk.Combobox(from_frame, values=lang_names, font=('Segoe UI', 10), width=18)
        self.input_combo.pack(fill=tk.X, pady=2)
        self.input_combo.set("English")

        # Swap button
        swap_btn = tk.Button(lang_controls, text="⇄", font=('Segoe UI', 14, 'bold'),
                           command=self.swap_languages, bg='#3b82f6', fg='white',
                           relief='flat', padx=12, pady=3, cursor='hand2')
        swap_btn.pack(side=tk.LEFT, padx=10, pady=15)

        # To language
        to_frame = tk.Frame(lang_controls, bg='#ffffff')
        to_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(10, 0))

        tk.Label(to_frame, text="Output:", font=('Segoe UI', 10, 'bold'), bg='#ffffff').pack(anchor=tk.W)
        self.output_combo = ttk.Combobox(to_frame, values=lang_names, font=('Segoe UI', 10), width=18)
        self.output_combo.pack(fill=tk.X, pady=2)
        self.output_combo.set("Sinhala (සිංහල)")

        self.input_combo.bind('<<ComboboxSelected>>', self.update_languages)
        self.output_combo.bind('<<ComboboxSelected>>', self.update_languages)

        # Input methods panel
        methods_frame = tk.Frame(main_container, bg='#f0f4f8')
        methods_frame.pack(fill=tk.X, pady=(0, 15))

        # Voice methods
        voice_frame = tk.LabelFrame(methods_frame, text=" 🎤 Voice Input / හඬ ආදානය ",
                                   font=('Segoe UI', 11, 'bold'),
                                   bg='#e6fffa', fg='#065f46', padx=15, pady=10)
        voice_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        voice_methods = [
            ("🎙️ Record with Phone", self.phone_recording_guide, "#10b981"),
            ("🗣️ Type What You Said", self.manual_voice_input, "#f59e0b"),
            ("⚡ Quick Phrases", self.show_quick_phrases, "#8b5cf6"),
            ("🎯 Voice Commands", self.show_voice_commands, "#ec4899")
        ]

        for i, (text, command, color) in enumerate(voice_methods):
            btn = tk.Button(voice_frame, text=text, command=command,
                           font=('Segoe UI', 10, 'bold'), bg=color, fg='white',
                           relief='flat', padx=15, pady=8, cursor='hand2')
            btn.pack(fill=tk.X, pady=2)

        # Text methods
        text_frame = tk.LabelFrame(methods_frame, text=" 📝 Text Input / පෙළ ආදානය ",
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='#fef7ed', fg='#9a3412', padx=15, pady=10)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        text_methods = [
            ("📝 Text Editor", self.toggle_text_mode, "#ea580c"),
            ("📋 Paste Text", self.paste_and_translate, "#7c3aed"),
            ("🔤 Sample Texts", self.show_sample_texts, "#059669"),
            ("🗑️ Clear All", self.clear_all, "#dc2626")
        ]

        for i, (text, command, color) in enumerate(text_methods):
            btn = tk.Button(text_frame, text=text, command=command,
                           font=('Segoe UI', 10, 'bold'), bg=color, fg='white',
                           relief='flat', padx=15, pady=8, cursor='hand2')
            btn.pack(fill=tk.X, pady=2)

        # Text input area (hidden initially)
        self.text_input_frame = tk.LabelFrame(main_container,
                                             text=" ✏️ Text Editor / පෙළ සංස්කාරක ",
                                             font=('Segoe UI', 10, 'bold'),
                                             bg='#ffffff', fg='#1f2937')

        text_container = tk.Frame(self.text_input_frame, bg='#ffffff')
        text_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.text_input = tk.Text(text_container, height=3, font=('Segoe UI', 11),
                                 wrap=tk.WORD, bg='#f9fafb', relief='flat',
                                 bd=1, padx=8, pady=8)
        self.text_input.pack(fill=tk.BOTH, expand=True)

        text_controls = tk.Frame(self.text_input_frame, bg='#ffffff')
        text_controls.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Button(text_controls, text="🌐 Translate", command=self.translate_text_input,
                 font=('Segoe UI', 10, 'bold'), bg='#059669', fg='white',
                 relief='flat', padx=15, pady=6, cursor='hand2').pack(side=tk.LEFT, padx=3)

        tk.Button(text_controls, text="Clear", command=lambda: self.text_input.delete(1.0, tk.END),
                 font=('Segoe UI', 10), bg='#6b7280', fg='white',
                 relief='flat', padx=12, pady=6, cursor='hand2').pack(side=tk.LEFT, padx=3)

        # Results display
        result_frame = tk.LabelFrame(main_container,
                                    text=" 🔄 Translation Results / පරිවර්තන ප්‍රතිඵල ",
                                    font=('Segoe UI', 12, 'bold'),
                                    bg='#ffffff', fg='#1f2937')
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        self.result_display = scrolledtext.ScrolledText(result_frame,
                                                       font=('Segoe UI', 10),
                                                       wrap=tk.WORD, height=18,
                                                       bg='#fafafa', relief='flat',
                                                       padx=8, pady=8)
        self.result_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Text tags
        self.result_display.tag_config("timestamp", foreground="#9ca3af", font=('Segoe UI', 8))
        self.result_display.tag_config("voice", foreground="#10b981", font=('Segoe UI', 10, 'bold'))
        self.result_display.tag_config("text", foreground="#3b82f6", font=('Segoe UI', 10, 'bold'))
        self.result_display.tag_config("translation", foreground="#dc2626", font=('Segoe UI', 11, 'bold'))
        self.result_display.tag_config("success", foreground="#059669", font=('Segoe UI', 10, 'bold'))
        self.result_display.tag_config("error", foreground="#ef4444")
        self.result_display.tag_config("separator", foreground="#d1d5db")
        self.result_display.tag_config("guide", foreground="#7c3aed", font=('Segoe UI', 9, 'italic'))

        # Status bar
        status_frame = tk.Frame(main_container, bg='#1f2937', height=35)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        status_frame.pack_propagate(False)

        self.status_label = tk.Label(status_frame, text="🟢 Ready / සූදානම්",
                                    font=('Segoe UI', 10, 'bold'),
                                    bg='#1f2937', fg='#ffffff')
        self.status_label.pack(side=tk.LEFT, padx=15, pady=8)

        # Add welcome message
        self.add_welcome_message()

    def add_welcome_message(self):
        self.result_display.insert(tk.END, "🎯 Welcome to Final Voice Translator!\n", "success")
        self.result_display.insert(tk.END, "අවසාන හඬ පරිවර්තකයට ආයුබෝවන්!\n\n", "success")
        self.result_display.insert(tk.END, "Voice Input Methods / හඬ ආදාන ක්‍රම:\n", "voice")
        self.result_display.insert(tk.END, "🎙️ Record with Phone - Use your phone to record\n", "text")
        self.result_display.insert(tk.END, "🗣️ Type What You Said - Manual voice input\n", "text")
        self.result_display.insert(tk.END, "⚡ Quick Phrases - Common expressions\n", "text")
        self.result_display.insert(tk.END, "🎯 Voice Commands - Useful commands\n", "text")
        self.result_display.insert(tk.END, "\nText Input Methods / පෙළ ආදාන ක්‍රම:\n", "text")
        self.result_display.insert(tk.END, "📝 Text Editor - Direct typing\n", "text")
        self.result_display.insert(tk.END, "📋 Paste Text - From clipboard\n", "text")
        self.result_display.insert(tk.END, "🔤 Sample Texts - Example texts\n", "text")
        self.result_display.insert(tk.END, "═" * 60 + "\n\n", "separator")

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
        self.add_message("⇄ Languages swapped / භාෂා අදලාවෙනු කරන ලදි", "success")

    def phone_recording_guide(self):
        """Guide for recording with phone"""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Phone Recording Guide")
        guide_window.geometry("600x500")
        guide_window.configure(bg='#f0f4f8')

        # Header
        tk.Label(guide_window, text="🎙️ Record with Your Phone",
                font=('Segoe UI', 16, 'bold'),
                bg='#f0f4f8', fg='#1f2937').pack(pady=15)

        # Instructions frame
        inst_frame = tk.LabelFrame(guide_window, text="Instructions / උපදෙස්",
                                  font=('Segoe UI', 11, 'bold'),
                                  bg='#ffffff', fg='#1f2937', padx=20, pady=15)
        inst_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        instructions = [
            "1. 📱 Open voice recorder app on your phone",
            "   ඔයාගේ phone එකේ voice recorder app එක open කරන්න",
            "",
            "2. 🎤 Record your voice clearly",
            "   පැහැදිලිව ඔයාගේ හඬ record කරන්න",
            "",
            "3. ▶️ Play back and listen to the recording",
            "   Record කරපු එක play කරලා අහන්න",
            "",
            "4. ⌨️ Type exactly what you said below",
            "   ඔයා කිව්වේ හරියටම මොකක්ද පහතින් type කරන්න",
            "",
            "5. 🌐 Click 'Start Recording Process' to begin",
            "   'Start Recording Process' click කරලා පටන් ගන්න"
        ]

        for instruction in instructions:
            if instruction.strip():
                color = "#3b82f6" if instruction.startswith("   ") else "#1f2937"
                weight = "normal" if instruction.startswith("   ") else "bold"
                tk.Label(inst_frame, text=instruction,
                        font=('Segoe UI', 10, weight),
                        bg='#ffffff', fg=color).pack(anchor=tk.W, pady=2)
            else:
                tk.Label(inst_frame, text="", bg='#ffffff').pack(pady=3)

        # Start button
        start_btn = tk.Button(guide_window, text="🎙️ Start Recording Process",
                             command=lambda: self.start_phone_recording(guide_window),
                             font=('Segoe UI', 12, 'bold'),
                             bg='#10b981', fg='white', relief='flat',
                             padx=20, pady=10, cursor='hand2')
        start_btn.pack(pady=20)

    def start_phone_recording(self, guide_window):
        """Start phone recording process"""
        guide_window.destroy()

        # Show countdown
        countdown_window = tk.Toplevel(self.root)
        countdown_window.title("Recording...")
        countdown_window.geometry("400x200")
        countdown_window.configure(bg='#f0f4f8')

        tk.Label(countdown_window, text="🎙️ Recording Process",
                font=('Segoe UI', 16, 'bold'),
                bg='#f0f4f8', fg='#1f2937').pack(pady=20)

        status_label = tk.Label(countdown_window, text="Get ready to record...",
                               font=('Segoe UI', 12),
                               bg='#f0f4f8', fg='#6b7280')
        status_label.pack(pady=10)

        # Countdown
        for i in range(3, 0, -1):
            status_label.config(text=f"Starting in {i}...")
            countdown_window.update()
            time.sleep(1)

        status_label.config(text="🔴 RECORD NOW!", fg="#ef4444")
        countdown_window.update()
        time.sleep(3)

        status_label.config(text="⏹ Recording finished! Now type what you said.", fg="#10b981")
        countdown_window.update()
        time.sleep(2)

        countdown_window.destroy()

        # Get voice input
        self.manual_voice_input()

    def manual_voice_input(self):
        """Manual voice input"""
        voice_text = tk.simpledialog.askstring(
            "Voice Input",
            "🗣️ What did you say?\n"
            "ඔයා කිව්වේ මොකක්ද?\n\n"
            "Type your speech here:"
        )

        if voice_text and voice_text.strip():
            self.process_voice_input(voice_text.strip(), "🗣️ Voice")

    def show_quick_phrases(self):
        """Show quick phrases"""
        phrases = {
            "Greetings / ආයුබෝවන": [
                "Hello", "Good morning", "Good evening", "How are you?",
                "Nice to meet you", "Goodbye", "See you later", "Thank you"
            ],
            "Travel / ගමන": [
                "Where is the bathroom?", "How much does this cost?",
                "I need help", "Do you speak English?", "Where is the hotel?",
                "Can you help me?", "I'm lost", "Call a taxi"
            ],
            "Food / ආහාර": [
                "I'm hungry", "This is delicious", "The bill please",
                "Water please", "I'm vegetarian", "What do you recommend?",
                "No spicy food", "Can I have the menu?"
            ]
        }

        self.show_phrase_window("⚡ Quick Phrases", phrases)

    def show_voice_commands(self):
        """Show voice commands"""
        commands = {
            "Basic Commands / මූලික විධාන": [
                "What time is it?", "What is your name?", "How old are you?",
                "Where are you from?", "What is this?", "How do you say this?",
                "I don't understand", "Please repeat"
            ],
            "Emergency / හදිසි": [
                "Help me", "Call the police", "I need a doctor",
                "Emergency", "Fire", "Call ambulance", "I'm sick", "Hospital"
            ],
            "Directions / දිශාව": [
                "Where is?", "How do I get to?", "Turn left", "Turn right",
                "Go straight", "Stop here", "Near", "Far"
            ]
        }

        self.show_phrase_window("🎯 Voice Commands", commands)

    def show_phrase_window(self, title, phrases_dict):
        """Show phrase selection window"""
        phrase_window = tk.Toplevel(self.root)
        phrase_window.title(title)
        phrase_window.geometry("500x400")
        phrase_window.configure(bg='#f0f4f8')

        tk.Label(phrase_window, text=title,
                font=('Segoe UI', 14, 'bold'),
                bg='#f0f4f8', fg='#1f2937').pack(pady=10)

        # Create scrollable area
        canvas = tk.Canvas(phrase_window, bg='#ffffff')
        scrollbar = ttk.Scrollbar(phrase_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ffffff')

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for category, phrase_list in phrases_dict.items():
            tk.Label(scrollable_frame, text=f"📂 {category}",
                    font=('Segoe UI', 11, 'bold'),
                    bg='#ffffff', fg='#1f2937').pack(anchor=tk.W, padx=10, pady=(10, 5))

            for phrase in phrase_list:
                btn = tk.Button(scrollable_frame, text=phrase,
                               command=lambda p=phrase: self.select_phrase(p, phrase_window),
                               font=('Segoe UI', 9), bg='#e5e7eb', fg='#374151',
                               relief='flat', padx=8, pady=4, cursor='hand2')
                btn.pack(fill=tk.X, padx=15, pady=1)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)

    def select_phrase(self, phrase, window):
        """Select a phrase"""
        window.destroy()
        self.process_voice_input(phrase, "⚡ Quick Phrase")

    def show_sample_texts(self):
        """Show sample texts"""
        samples = {
            "Business / ව්‍යාපාර": [
                "I would like to schedule a meeting",
                "Please send me the report",
                "The project is completed",
                "We need to discuss the budget"
            ],
            "Education / අධ්‍යාපන": [
                "I need help with my homework",
                "When is the exam?",
                "Can you explain this concept?",
                "The assignment is due tomorrow"
            ],
            "Daily Life / දෛනික ජීවිතය": [
                "What's the weather like?",
                "I'm going to the store",
                "Let's have dinner together",
                "I'll call you later"
            ]
        }

        self.show_phrase_window("🔤 Sample Texts", samples)

    def process_voice_input(self, text, input_type):
        """Process voice input"""
        self.add_message(f"{input_type}: {text}", "voice")
        self.status_label.config(text="🔄 Translating... / පරිවර්තනය කරමින්...")
        threading.Thread(target=self.translate_and_display, args=(text, input_type), daemon=True).start()

    def toggle_text_mode(self):
        """Toggle text input area"""
        if self.text_input_frame.winfo_viewable():
            self.text_input_frame.pack_forget()
        else:
            # Find result frame and pack before it
            for child in self.text_input_frame.master.winfo_children():
                if isinstance(child, tk.LabelFrame) and "Translation Results" in child.cget('text'):
                    self.text_input_frame.pack(fill=tk.X, pady=10, before=child)
                    break
            else:
                self.text_input_frame.pack(fill=tk.X, pady=10)
            self.text_input.focus()

    def translate_text_input(self):
        """Translate text input"""
        text = self.text_input.get(1.0, tk.END).strip()
        if text:
            self.add_message(f"📝 Text: {text}", "text")
            self.text_input.delete(1.0, tk.END)
            threading.Thread(target=self.translate_and_display, args=(text, "📝 Text"), daemon=True).start()

    def paste_and_translate(self):
        """Paste and translate"""
        try:
            clipboard_text = self.root.clipboard_get().strip()
            if clipboard_text:
                self.add_message(f"📋 Pasted: {clipboard_text}", "text")
                threading.Thread(target=self.translate_and_display,
                               args=(clipboard_text, "📋 Clipboard"), daemon=True).start()
            else:
                messagebox.showinfo("Empty", "Clipboard is empty!")
        except:
            messagebox.showerror("Error", "Could not access clipboard!")

    def translate_and_display(self, text, input_type):
        """Translate and display"""
        try:
            translated = self.translate_text(text)
            if translated:
                self.root.after(0, lambda: self.add_message(f"🌐 Translation: {translated}", "translation"))
                self.root.after(0, lambda: self.status_label.config(text="✅ Complete / සම්පූර්ණයි"))
            else:
                self.root.after(0, lambda: self.add_message("❌ Translation failed", "error"))
        except Exception as e:
            self.root.after(0, lambda: self.add_message(f"❌ Error: {e}", "error"))

    def translate_text(self, text):
        """Translate using Google Translate"""
        try:
            base_url = "https://translate.googleapis.com/translate_a/single"
            params = {'client': 'gtx', 'sl': self.input_lang, 'tl': self.output_lang, 'dt': 't', 'q': text}
            url = base_url + '?' + urllib.parse.urlencode(params)
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
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
            self.result_display.insert(tk.END, "─" * 60 + "\n", "separator")
        self.result_display.see(tk.END)

    def clear_all(self):
        """Clear all"""
        self.result_display.delete(1.0, tk.END)
        self.add_welcome_message()
        self.status_label.config(text="🗑️ Cleared / මකා දැමුවා")

def main():
    import tkinter.simpledialog
    tk.simpledialog = tkinter.simpledialog

    root = tk.Tk()
    app = FinalVoiceTranslator(root)

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
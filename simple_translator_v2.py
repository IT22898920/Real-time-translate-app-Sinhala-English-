import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import urllib.request
import urllib.parse
import json
import threading

class SimpleTranslatorV2:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Text Translator - සරල පෙළ පරිවර්තකය")
        self.root.geometry("900x650")

        self.input_lang = 'en'
        self.output_lang = 'si'

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="Text Translator",
                                font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        subtitle_label = ttk.Label(main_frame, text="පෙළ පරිවර්තකය",
                                   font=('Arial', 14))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Language selection
        lang_frame = ttk.LabelFrame(main_frame, text="Language Settings / භාෂා සැකසුම්",
                                    padding="10")
        lang_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        ttk.Label(lang_frame, text="From / සිට:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.input_lang_combo = ttk.Combobox(lang_frame, width=25)
        self.input_lang_combo.grid(row=0, column=1, padx=5)

        ttk.Label(lang_frame, text="To / දක්වා:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.output_lang_combo = ttk.Combobox(lang_frame, width=25)
        self.output_lang_combo.grid(row=0, column=3, padx=5)

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
            ('Portuguese', 'pt'),
            ('Russian (Русский)', 'ru'),
            ('Japanese (日本語)', 'ja'),
            ('Korean (한국어)', 'ko'),
            ('Chinese Simplified (简体中文)', 'zh-CN'),
            ('Arabic (العربية)', 'ar'),
            ('Dutch (Nederlands)', 'nl'),
            ('Swedish (Svenska)', 'sv'),
            ('Polish (Polski)', 'pl'),
            ('Turkish (Türkçe)', 'tr'),
            ('Indonesian', 'id'),
            ('Thai (ไทย)', 'th')
        ]

        self.lang_dict = {name: code for name, code in languages}
        lang_names = [name for name, code in languages]

        self.input_lang_combo['values'] = lang_names
        self.output_lang_combo['values'] = lang_names

        self.input_lang_combo.set("English")
        self.output_lang_combo.set("Sinhala (සිංහල)")

        self.input_lang_combo.bind('<<ComboboxSelected>>', self.update_languages)
        self.output_lang_combo.bind('<<ComboboxSelected>>', self.update_languages)

        # Input and output frames
        frames_container = ttk.Frame(main_frame)
        frames_container.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input frame
        input_frame = ttk.LabelFrame(frames_container, text="Input Text / ඇතුළත් කරන පෙළ",
                                     padding="10")
        input_frame.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.input_text = scrolledtext.ScrolledText(input_frame, width=45, height=18,
                                                    wrap=tk.WORD, font=('Arial', 11))
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Character count for input
        self.input_count_label = ttk.Label(input_frame, text="Characters: 0",
                                           font=('Arial', 9))
        self.input_count_label.grid(row=1, column=0, pady=5, sticky=tk.W)

        # Output frame
        output_frame = ttk.LabelFrame(frames_container, text="Translation / පරිවර්තනය",
                                      padding="10")
        output_frame.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.output_text = scrolledtext.ScrolledText(output_frame, width=45, height=18,
                                                     wrap=tk.WORD, font=('Arial', 11),
                                                     bg='#f0f0f0')
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.output_text.config(state=tk.DISABLED)

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.translate_button = ttk.Button(control_frame, text="🌐 Translate / පරිවර්තනය කරන්න",
                                          command=self.translate_text, width=25)
        self.translate_button.grid(row=0, column=0, padx=5)

        self.clear_button = ttk.Button(control_frame, text="🗑️ Clear All / සියල්ල මකන්න",
                                       command=self.clear_text, width=20)
        self.clear_button.grid(row=0, column=1, padx=5)

        self.swap_button = ttk.Button(control_frame, text="⇄ Swap Languages",
                                      command=self.swap_languages, width=20)
        self.swap_button.grid(row=0, column=2, padx=5)

        self.copy_button = ttk.Button(control_frame, text="📋 Copy Translation",
                                      command=self.copy_translation, width=20)
        self.copy_button.grid(row=0, column=3, padx=5)

        # Real-time translation checkbox
        self.realtime_var = tk.BooleanVar(value=False)
        self.realtime_check = ttk.Checkbutton(control_frame,
                                              text="Enable Real-time Translation / සජීවී පරිවර්තනය සක්‍රීය කරන්න",
                                              variable=self.realtime_var,
                                              command=self.toggle_realtime)
        self.realtime_check.grid(row=1, column=0, columnspan=4, pady=10)

        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=5, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        self.status_label = ttk.Label(status_frame, text="Ready / සූදානම්",
                                     foreground="green", font=('Arial', 10))
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        # Instructions
        instructions = ttk.Label(status_frame,
                               text="Type or paste text and click Translate | පෙළ ටයිප් කර හෝ paste කර Translate click කරන්න",
                               font=('Arial', 9), foreground="gray")
        instructions.grid(row=0, column=1, padx=20)

        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(3, weight=1)
        frames_container.grid_rowconfigure(0, weight=1)
        frames_container.grid_columnconfigure(0, weight=1)
        frames_container.grid_columnconfigure(1, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)
        output_frame.grid_columnconfigure(0, weight=1)

        # Bind events
        self.input_text.bind('<KeyRelease>', self.on_text_change)
        self.input_text.bind('<Control-v>', self.on_paste)

        # Timer for real-time translation
        self.timer = None

    def update_languages(self, event=None):
        input_selection = self.input_lang_combo.get()
        output_selection = self.output_lang_combo.get()

        self.input_lang = self.lang_dict.get(input_selection, 'en')
        self.output_lang = self.lang_dict.get(output_selection, 'si')

    def toggle_realtime(self):
        if self.realtime_var.get():
            self.translate_button.config(state=tk.DISABLED)
            self.status_label.config(text="Real-time mode ON / සජීවී මාදිලිය සක්‍රීයයි",
                                    foreground="blue")
            self.on_text_change()
        else:
            self.translate_button.config(state=tk.NORMAL)
            self.status_label.config(text="Ready / සූදානම්", foreground="green")

    def on_text_change(self, event=None):
        # Update character count
        text = self.input_text.get(1.0, tk.END).strip()
        char_count = len(text)
        self.input_count_label.config(text=f"Characters: {char_count}")

        if self.realtime_var.get():
            # Cancel previous timer if exists
            if self.timer:
                self.root.after_cancel(self.timer)
            # Set new timer to translate after 800ms of no typing
            if text:
                self.timer = self.root.after(800, self.translate_text)

    def on_paste(self, event=None):
        # Handle paste event
        self.root.after(100, self.on_text_change)

    def translate_text(self):
        input_text = self.input_text.get(1.0, tk.END).strip()

        if not input_text:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.config(state=tk.DISABLED)
            return

        # Limit text length for API
        if len(input_text) > 5000:
            messagebox.showwarning("Text Too Long",
                                  "Please enter text less than 5000 characters.\nපෙළ අක්ෂර 5000 ට අඩු විය යුතුය.")
            return

        self.status_label.config(text="Translating... / පරිවර්තනය කරමින්...",
                                foreground="orange")
        self.translate_button.config(state=tk.DISABLED)

        # Run translation in separate thread
        thread = threading.Thread(target=self.perform_translation, args=(input_text,))
        thread.daemon = True
        thread.start()

    def perform_translation(self, text):
        try:
            # Using Google Translate API (free tier)
            base_url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': self.input_lang,
                'tl': self.output_lang,
                'dt': 't',
                'q': text
            }

            url = base_url + '?' + urllib.parse.urlencode(params)

            # Make request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            request = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(request, timeout=10)
            result = json.loads(response.read().decode('utf-8'))

            # Extract translated text
            translated_text = ''
            if result and len(result) > 0 and result[0]:
                for sentence in result[0]:
                    if sentence[0]:
                        translated_text += sentence[0]

            if translated_text:
                # Update UI in main thread
                self.root.after(0, self.update_output, translated_text)
                self.root.after(0, lambda: self.status_label.config(
                    text="Translation complete / පරිවර්තනය සම්පූර්ණයි",
                    foreground="green"))
            else:
                self.root.after(0, lambda: self.status_label.config(
                    text="No translation available / පරිවර්තනයක් නොමැත",
                    foreground="orange"))

        except urllib.error.URLError:
            self.root.after(0, lambda: messagebox.showerror(
                "Connection Error",
                "No internet connection. Please check your network.\nඅන්තර්ජාල සම්බන්ධතාවය පරීක්ෂා කරන්න."))
            self.root.after(0, lambda: self.status_label.config(
                text="Connection error / සම්බන්ධතා දෝෂය",
                foreground="red"))
        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(
                text="Translation error / පරිවර්තන දෝෂය",
                foreground="red"))
        finally:
            self.root.after(0, lambda: self.translate_button.config(
                state=tk.NORMAL if not self.realtime_var.get() else tk.DISABLED))

    def update_output(self, text):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, text)
        self.output_text.config(state=tk.DISABLED)

    def clear_text(self):
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.input_count_label.config(text="Characters: 0")
        self.status_label.config(text="Cleared / මකා දැමුවා", foreground="green")

    def swap_languages(self):
        # Swap language selections
        input_val = self.input_lang_combo.get()
        output_val = self.output_lang_combo.get()
        self.input_lang_combo.set(output_val)
        self.output_lang_combo.set(input_val)
        self.update_languages()

        # Swap text contents
        output_text = self.output_text.get(1.0, tk.END).strip()
        if output_text:
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(1.0, output_text)
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.config(state=tk.DISABLED)
            self.status_label.config(text="Languages swapped / භාෂා මාරු කළා",
                                    foreground="blue")

    def copy_translation(self):
        translated_text = self.output_text.get(1.0, tk.END).strip()
        if translated_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(translated_text)
            self.status_label.config(text="Copied to clipboard / පිටපත් කළා",
                                    foreground="blue")
        else:
            self.status_label.config(text="Nothing to copy / පිටපත් කිරීමට කිසිවක් නැත",
                                    foreground="orange")

def main():
    root = tk.Tk()
    app = SimpleTranslatorV2(root)

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
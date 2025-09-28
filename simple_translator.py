import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from googletrans import Translator, LANGUAGES
import threading

class SimpleTranslator:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Text Translator - සරල පෙළ පරිවර්තකය")
        self.root.geometry("800x600")

        self.translator = Translator()
        self.input_lang = 'en'
        self.output_lang = 'si'

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="Text Translator",
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        subtitle_label = ttk.Label(main_frame, text="පෙළ පරිවර්තකය",
                                   font=('Arial', 12))
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Language selection
        lang_frame = ttk.LabelFrame(main_frame, text="Language Settings / භාෂා සැකසුම්",
                                    padding="10")
        lang_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        ttk.Label(lang_frame, text="From:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.input_lang_combo = ttk.Combobox(lang_frame, width=20)
        self.input_lang_combo.grid(row=0, column=1, padx=5)

        ttk.Label(lang_frame, text="To:").grid(row=0, column=2, padx=5, sticky=tk.W)
        self.output_lang_combo = ttk.Combobox(lang_frame, width=20)
        self.output_lang_combo.grid(row=0, column=3, padx=5)

        # Common languages
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
            'zh-cn': 'Chinese (Simplified)'
        }

        lang_values = [f"{common_languages.get(code, LANGUAGES.get(code, code).title())} ({code})"
                      for code in common_languages.keys()]
        self.input_lang_combo['values'] = lang_values
        self.output_lang_combo['values'] = lang_values

        self.input_lang_combo.set("English (en)")
        self.output_lang_combo.set("Sinhala (සිංහල) (si)")

        self.input_lang_combo.bind('<<ComboboxSelected>>', self.update_languages)
        self.output_lang_combo.bind('<<ComboboxSelected>>', self.update_languages)

        # Input and output frames
        frames_container = ttk.Frame(main_frame)
        frames_container.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input frame
        input_frame = ttk.LabelFrame(frames_container, text="Input Text / ඇතුළත් කරන පෙළ",
                                     padding="10")
        input_frame.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.input_text = scrolledtext.ScrolledText(input_frame, width=40, height=15,
                                                    wrap=tk.WORD, font=('Arial', 11))
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Output frame
        output_frame = ttk.LabelFrame(frames_container, text="Translation / පරිවර්තනය",
                                      padding="10")
        output_frame.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.output_text = scrolledtext.ScrolledText(output_frame, width=40, height=15,
                                                     wrap=tk.WORD, font=('Arial', 11))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.output_text.config(state=tk.DISABLED)

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.translate_button = ttk.Button(control_frame, text="Translate / පරිවර්තනය කරන්න",
                                          command=self.translate_text, width=20)
        self.translate_button.grid(row=0, column=0, padx=5)

        self.realtime_var = tk.BooleanVar(value=False)
        self.realtime_check = ttk.Checkbutton(control_frame, text="Real-time Translation / සජීවී පරිවර්තනය",
                                              variable=self.realtime_var,
                                              command=self.toggle_realtime)
        self.realtime_check.grid(row=0, column=1, padx=5)

        self.clear_button = ttk.Button(control_frame, text="Clear / මකන්න",
                                       command=self.clear_text, width=15)
        self.clear_button.grid(row=0, column=2, padx=5)

        self.swap_button = ttk.Button(control_frame, text="⇄ Swap Languages",
                                      command=self.swap_languages, width=15)
        self.swap_button.grid(row=0, column=3, padx=5)

        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready / සූදානම්",
                                     foreground="green")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5, sticky=tk.W)

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

        # Bind text change event for real-time translation
        self.input_text.bind('<KeyRelease>', self.on_text_change)

    def update_languages(self, event=None):
        input_selection = self.input_lang_combo.get()
        output_selection = self.output_lang_combo.get()

        self.input_lang = input_selection.split('(')[-1].rstrip(')')
        self.output_lang = output_selection.split('(')[-1].rstrip(')')

    def toggle_realtime(self):
        if self.realtime_var.get():
            self.translate_button.config(state=tk.DISABLED)
            self.on_text_change()
        else:
            self.translate_button.config(state=tk.NORMAL)

    def on_text_change(self, event=None):
        if self.realtime_var.get():
            # Cancel previous timer if exists
            if hasattr(self, 'timer'):
                self.root.after_cancel(self.timer)
            # Set new timer to translate after 500ms of no typing
            self.timer = self.root.after(500, self.translate_text)

    def translate_text(self):
        input_text = self.input_text.get(1.0, tk.END).strip()

        if not input_text:
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.config(state=tk.DISABLED)
            return

        self.status_label.config(text="Translating... / පරිවර්තනය කරමින්...",
                                 foreground="blue")

        # Run translation in separate thread to avoid freezing UI
        thread = threading.Thread(target=self.perform_translation, args=(input_text,))
        thread.daemon = True
        thread.start()

    def perform_translation(self, text):
        try:
            translated = self.translator.translate(text, src=self.input_lang,
                                                  dest=self.output_lang)

            # Update UI in main thread
            self.root.after(0, self.update_output, translated.text)
            self.root.after(0, lambda: self.status_label.config(
                text="Translation complete / පරිවර්තනය සම්පූර්ණයි",
                foreground="green"))

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.update_output, error_msg)
            self.root.after(0, lambda: self.status_label.config(
                text="Translation error / පරිවර්තන දෝෂයක්",
                foreground="red"))

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
        self.status_label.config(text="Cleared / මකා දැමුවා", foreground="green")

    def swap_languages(self):
        # Swap language selections
        input_val = self.input_lang_combo.get()
        output_val = self.output_lang_combo.get()
        self.input_lang_combo.set(output_val)
        self.output_lang_combo.set(input_val)
        self.update_languages()

        # Swap text contents
        input_text = self.input_text.get(1.0, tk.END).strip()
        output_text = self.output_text.get(1.0, tk.END).strip()

        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, output_text)

        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(1.0, input_text)
        self.output_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = SimpleTranslator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
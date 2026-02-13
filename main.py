import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from LabOne.CeaserCipher import CeaserCipher


# ─────────────────────────── helpers ───────────────────────────
def make_label_entry(parent, label_text, row, default="", width=60):
    """Create a Label + Entry pair and return the StringVar."""
    ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", padx=6, pady=4)
    var = tk.StringVar(value=default)
    entry = ttk.Entry(parent, textvariable=var, width=width)
    entry.grid(row=row, column=1, sticky="we", padx=6, pady=4)
    return var


def make_text_block(parent, label_text, height=6):
    """Create a Label + ScrolledText and return the text widget."""
    frame = ttk.LabelFrame(parent, text=label_text)
    frame.pack(fill="both", expand=True, padx=8, pady=4)
    txt = scrolledtext.ScrolledText(frame, wrap="word", height=height, font=("Hack", 11))
    txt.pack(fill="both", expand=True, padx=4, pady=4)
    return txt


# ─────────────────────── Caesar tab ────────────────────────────
class CaesarTab(ttk.Frame):
    """Tab for the Caesar cipher."""

    def __init__(self, master):
        super().__init__(master)
        self.cipher = CeaserCipher()
        self._build_ui()

    # ── UI ──────────────────────────────────────────────────────
    def _build_ui(self):
        # --- top panel: key input and direction ----------------
        top = ttk.Frame(self)
        top.pack(fill="x", padx=8, pady=4)
        top.columnconfigure(1, weight=1)

        self.key_var = make_label_entry(top, "Key (shift):", row=0, default="3", width=10)

        self.direction_var = tk.StringVar(value="left")
        ttk.Label(top, text="Direction:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        dir_frame = ttk.Frame(top)
        dir_frame.grid(row=1, column=1, sticky="w", padx=6)
        ttk.Radiobutton(dir_frame, text="Left", variable=self.direction_var, value="left").pack(side="left")
        ttk.Radiobutton(dir_frame, text="Right", variable=self.direction_var, value="right").pack(side="left", padx=12)

        # --- input text field ----------------------------------
        self.input_txt = make_text_block(self, "Input Text")

        # --- action buttons ------------------------------------
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=4)

        ttk.Button(btn_frame, text="[+] Encrypt",      command=self._encrypt).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="[-] Decrypt",      command=self._decrypt).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="[!] Brute-force",  command=self._brute_force).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="[X] Partial Cryptanalysis",  command=self._chi_squared).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="[~] Frequency",    command=self._show_freq).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="[x] Clear",        command=self._clear).pack(side="right", padx=4)

        # --- output field --------------------------------------
        self.output_txt = make_text_block(self, "Result", height=10)

    # ── actions ─────────────────────────────────────────────────
    def _get_key(self):
        try:
            return int(self.key_var.get())
        except ValueError:
            messagebox.showerror("Error", "Key must be an integer")
            return None

    def _get_moved_alphabet(self, key):
        if self.direction_var.get() == "left":
            return self.cipher.moved_alphabet_left(key)
        return self.cipher.moved_alphabet_right(key)

    def _write_output(self, text):
        self.output_txt.delete("1.0", "end")
        self.output_txt.insert("1.0", text)

    def _encrypt(self):
        key = self._get_key()
        if key is None:
            return
        plain = self.input_txt.get("1.0", "end").strip().upper()
        moved = self._get_moved_alphabet(key)
        encrypted = self.cipher.encrypt_text(plain, moved)
        self._write_output(encrypted)

    def _decrypt(self):
        key = self._get_key()
        if key is None:
            return
        cipher_text = self.input_txt.get("1.0", "end").strip().upper()
        moved = self._get_moved_alphabet(key)
        decrypted = self.cipher.decrypt_text(cipher_text, moved)
        self._write_output(decrypted)

    def _brute_force(self):
        cipher_text = self.input_txt.get("1.0", "end").strip().upper()
        if not cipher_text:
            messagebox.showwarning("Empty", "Please enter encrypted text")
            return
        lines = []
        for i in range(26):
            moved = self.cipher.moved_alphabet_left(i)
            decrypted = self.cipher.decrypt_text(cipher_text, moved)
            lines.append(f"Shift {i:>2}: {decrypted}")
        self._write_output("\n".join(lines))

    def _chi_squared(self):
        cipher_text = self.input_txt.get("1.0", "end").strip().upper()
        if not cipher_text:
            messagebox.showwarning("Empty", "Please enter encrypted text")
            return

        alphabet_index = {c: i for i, c in enumerate(self.cipher._alphabet)}
        results = []
        for shift in range(26):
            decrypted = ""
            for ch in cipher_text:
                if ch in alphabet_index:
                    idx = (alphabet_index[ch] - shift) % 26
                    decrypted += self.cipher._alphabet[idx]
                else:
                    decrypted += ch
            freq = self.cipher.count_text_frequencies(decrypted)
            score = self.cipher.chi_squared(freq)
            results.append((shift, score, decrypted))

        results.sort(key=lambda x: x[1])

        lines = ["Top 5 most likely decryptions:\n"]
        for i, (shift, score, text) in enumerate(results[:5], 1):
            lines.append(f"{i}. Shift={shift}, χ²={score:.2f}")
            lines.append(f"   {text[:120]}...\n")

        lines.append("=" * 60)
        lines.append("Best result (full text):\n")
        lines.append(results[0][2])
        self._write_output("\n".join(lines))

    def _show_freq(self):
        text = self.input_txt.get("1.0", "end").strip().upper()
        if not text:
            messagebox.showwarning("Empty", "Please enter text for analysis")
            return
        freq = self.cipher.count_text_frequencies(text)
        # sort by frequency descending
        sorted_freq = sorted(freq.items(), key=lambda x: -x[1])
        lines = ["Frequency analysis:\n"]
        lines.append(f"{'Char':<8} {'Freq, %':<12} {'Bar'}")
        lines.append("-" * 50)
        for ch, pct in sorted_freq:
            bar = "█" * int(pct)
            lines.append(f"  {ch:<6} {pct:>6.2f}%      {bar}")
        self._write_output("\n".join(lines))

    def _clear(self):
        self.input_txt.delete("1.0", "end")
        self.output_txt.delete("1.0", "end")


# ───────────────────── placeholder tab ─────────────────────────
class PlaceholderTab(ttk.Frame):
    """Placeholder for future cipher methods."""

    def __init__(self, master, name="???"):
        super().__init__(master)
        ttk.Label(
            self,
            text=f"[ ] Method '{name}' will be implemented later",
            font=("Noto Sans", 14),
        ).pack(expand=True)


# ───────────────────── main application ────────────────────────
class CryptoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cryptography -- Laboratory")
        self.geometry("900x700")
        self.minsize(700, 500)

        # -- normalize DPI scaling across environments ---------
        self.tk.call("tk", "scaling", 1.33)

        # -- set default fonts for the whole app ---------------
        default_font = ("Noto Sans", 10)
        self.option_add("*Font", default_font)
        self.option_add("*TkDefaultFont", default_font)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".",          font=("Noto Sans", 10))
        style.configure("TLabel",     font=("Noto Sans", 10))
        style.configure("TButton",    font=("Noto Sans", 10))
        style.configure("TNotebook.Tab", font=("Noto Sans", 10, "bold"))
        style.configure("TLabelframe.Label", font=("Noto Sans", 10))
        style.configure("TRadiobutton", font=("Noto Sans", 10))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=6, pady=6)

        # ── tabs ──
        self.notebook.add(CaesarTab(self.notebook),              text="  Caesar  ")
        self.notebook.add(PlaceholderTab(self.notebook, "____"),    text="  ____  ")
        self.notebook.add(PlaceholderTab(self.notebook, "____"), text="  ____  ")

        # status bar
        self.status = ttk.Label(self, text="Ready", relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")


if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()

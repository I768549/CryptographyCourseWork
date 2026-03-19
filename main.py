import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from LabOne.CeaserCipher import CeaserCipher
from LabTwo.NumericalGenerator import NumericalGenerator


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
        ttk.Button(btn_frame, text="[X] Chi-squared",  command=self._chi_squared).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="[~] Frequency",    command=self._show_freq).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="[A] Frequency Crack", command=self._classic_crack).pack(side="left", padx=4)
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

    def _classic_crack(self):
        cipher_text = self.input_txt.get("1.0", "end").strip().upper()
        if not cipher_text:
            messagebox.showwarning("Empty", "Please enter encrypted text")
            return

        shift, decrypted, mapping = self.cipher.classic_frequency_analysis(cipher_text)

        lines = ["=== Classic Frequency Cryptanalysis ===", ""]
        lines.append(f"Most frequent cipher letter -> mapped to 'E'")
        lines.append(f"Detected shift: {shift}")
        lines.append("")
        lines.append("Frequency mapping (cipher vs English reference):")
        lines.append(f"{'#':<4} {'Cipher':<9} {'Freq %':<10} {'English':<9} {'Ref %':<10}")
        lines.append("-" * 46)
        for rank, c_ch, c_fr, e_ch, e_fr in mapping:
            marker = "  <--" if rank == 1 else ""
            lines.append(f"{rank:<4} {c_ch:<9} {c_fr:>5.2f}%    {e_ch:<9} {e_fr:>5.2f}%{marker}")
        lines.append("")
        lines.append("=" * 46)
        lines.append("Decrypted text:")
        lines.append(decrypted)
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


# ──────────────────── Generator tab ────────────────────────────
class GeneratorTab(ttk.Frame):
    """Tab for pseudo-random number / bit generation (Lemer & BBS)."""

    def __init__(self, master):
        super().__init__(master)
        self.gen = NumericalGenerator()
        self._build_ui()

    # ── UI ──────────────────────────────────────────────────────
    def _build_ui(self):
        # --- method selector -----------------------------------
        sel = ttk.LabelFrame(self, text="Method")
        sel.pack(fill="x", padx=8, pady=4)

        self.method_var = tk.StringVar(value="lemer")
        ttk.Radiobutton(sel, text="Lemer (LCG)", variable=self.method_var,
                        value="lemer", command=self._toggle_params).pack(side="left", padx=10, pady=4)
        ttk.Radiobutton(sel, text="BBS", variable=self.method_var,
                        value="bbs", command=self._toggle_params).pack(side="left", padx=10, pady=4)
        ttk.Radiobutton(sel, text="BBS + Binance entropy", variable=self.method_var,
                        value="bbs_binance", command=self._toggle_params).pack(side="left", padx=10, pady=4)

        # --- parameters frame ----------------------------------
        self.params_frame = ttk.LabelFrame(self, text="Parameters")
        self.params_frame.pack(fill="x", padx=8, pady=4)
        self.params_frame.columnconfigure(1, weight=1)

        # Lemer params
        self.lemer_n_var      = make_label_entry(self.params_frame, "Count (n):",      row=0, default="1000", width=20)
        self.lemer_multi_var  = make_label_entry(self.params_frame, "Multiplier (a):",  row=1, default="16807", width=20)
        self.lemer_mod_var    = make_label_entry(self.params_frame, "Modulus (m):",     row=2, default="2147483647", width=20)
        self.lemer_seed_var   = make_label_entry(self.params_frame, "Seed:",            row=3, default="1007", width=20)

        # BBS params (rows 4-7, hidden initially)
        self.bbs_p_var       = make_label_entry(self.params_frame, "p (≡3 mod 4):",   row=4, default="2147483659", width=20)
        self.bbs_q_var       = make_label_entry(self.params_frame, "q (≡3 mod 4):",   row=5, default="2147483743", width=20)
        self.bbs_seed_var    = make_label_entry(self.params_frame, "Seed:",            row=6, default="123456789", width=20)
        self.bbs_bits_var    = make_label_entry(self.params_frame, "Bits to generate:",row=7, default="1024", width=20)

        # output format
        fmt = ttk.Frame(self.params_frame)
        fmt.grid(row=8, column=0, columnspan=2, sticky="w", padx=6, pady=4)
        ttk.Label(fmt, text="Show as:").pack(side="left")
        self.fmt_var = tk.StringVar(value="bits")
        ttk.Radiobutton(fmt, text="Bitstream", variable=self.fmt_var, value="bits").pack(side="left", padx=8)
        ttk.Radiobutton(fmt, text="Numbers",   variable=self.fmt_var, value="nums").pack(side="left", padx=8)

        self._toggle_params()  # show/hide relevant rows

        # --- buttons -------------------------------------------
        btn = ttk.Frame(self)
        btn.pack(fill="x", padx=8, pady=4)
        ttk.Button(btn, text="▶  Generate", command=self._generate).pack(side="left", padx=4)
        ttk.Button(btn, text="💾  Save to file", command=self._save).pack(side="left", padx=4)
        ttk.Button(btn, text="✕  Clear",    command=self._clear).pack(side="right", padx=4)

        # --- output --------------------------------------------
        self.output_txt = make_text_block(self, "Output", height=14)

    # ── show / hide params based on method ─────────────────────
    def _toggle_params(self):
        method = self.method_var.get()
        lemer_rows = {0, 1, 2, 3}
        bbs_rows   = {4, 5, 6, 7}

        for widget in self.params_frame.winfo_children():
            info = widget.grid_info()
            if not info:
                continue
            r = int(info["row"])
            if method == "lemer":
                widget.grid() if r in lemer_rows or r == 8 else widget.grid_remove()
            else:
                widget.grid() if r in bbs_rows or r == 8 else widget.grid_remove()

    # ── generation logic ───────────────────────────────────────
    def _generate(self):
        method = self.method_var.get()
        try:
            if method == "lemer":
                result = self._run_lemer()
            elif method == "bbs":
                result = self._run_bbs()
            else:
                result = self._run_bbs_binance()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.output_txt.delete("1.0", "end")
        self.output_txt.insert("1.0", result)

    def _run_lemer(self):
        n     = int(self.lemer_n_var.get())
        multi = int(self.lemer_multi_var.get())
        mod   = int(self.lemer_mod_var.get())
        seed  = int(self.lemer_seed_var.get())
        nums  = self.gen.LemerGenerator(n, multi, mod, seed)

        if self.fmt_var.get() == "bits":
            bits = NumericalGenerator.numbers_to_bitsream(nums)
            return f"Lemer bitstream ({len(bits)} bits):\n\n{bits}"
        return f"Lemer sequence ({len(nums)} numbers):\n\n" + "\n".join(str(x) for x in nums)

    def _run_bbs(self):
        p    = int(self.bbs_p_var.get())
        q    = int(self.bbs_q_var.get())
        seed = int(self.bbs_seed_var.get())
        nbits = int(self.bbs_bits_var.get())
        bits = self.gen.BBS(p, q, seed, nbits)
        if bits is None:
            raise ValueError("BBS returned nothing — check p, q, seed constraints.")

        if self.fmt_var.get() == "nums":
            nums = NumericalGenerator.bitsream_to_numbers(bits, 32)
            return f"BBS → numbers ({len(nums)} values):\n\n" + "\n".join(str(x) for x in nums)
        return f"BBS bitstream ({len(bits)} bits):\n\n{bits}"

    def _run_bbs_binance(self):
        p     = int(self.bbs_p_var.get())
        q     = int(self.bbs_q_var.get())
        nbits = int(self.bbs_bits_var.get())
        n_val = p * q

        # one Lemer value for entropy
        lemer_val = self.gen.LemerGenerator(1, 16807, 2147483647, 99991)[0]
        import math
        raw_entropy = NumericalGenerator.get_entropy_from_binance(lemer_val)
        s = (raw_entropy % (n_val - 2)) + 2
        while math.gcd(s, n_val) != 1:
            s = (s + 1) % n_val

        bits = self.gen.BBS(p, q, s, nbits)
        if bits is None:
            raise ValueError("BBS returned nothing — check p, q constraints.")

        header = f"BBS + Binance entropy (seed={s})\n"
        if self.fmt_var.get() == "nums":
            nums = NumericalGenerator.bitsream_to_numbers(bits, 32)
            return header + f"{len(nums)} numbers:\n\n" + "\n".join(str(x) for x in nums)
        return header + f"{len(bits)} bits:\n\n{bits}"

    # ── save / clear ───────────────────────────────────────────
    def _save(self):
        content = self.output_txt.get("1.0", "end").strip()
        if not content:
            messagebox.showwarning("Empty", "Nothing to save — generate first.")
            return
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if path:
            with open(path, "w") as f:
                f.write(content)
            messagebox.showinfo("Saved", f"Written to {path}")

    def _clear(self):
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
        self.notebook.add(GeneratorTab(self.notebook),             text="  PRNG  ")
        self.notebook.add(PlaceholderTab(self.notebook, "____"), text="  ____  ")

        # status bar
        self.status = ttk.Label(self, text="Ready", relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")


if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()

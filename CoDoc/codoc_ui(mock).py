import tkinter as tk
from tkinter import messagebox, scrolledtext
from tkinter import ttk
from updated_app import run_analysis
import threading

def code_checkup():
    code = code_text.get("1.0", tk.END).strip()
    if not code:
        messagebox.showwarning("Input Needed", "Please paste or type your code before analyzing.")
        return

    selected_lang = lang_selector.get().lower()
    checkup_btn.config(state="disabled")
    surgery_btn.config(state="disabled")
    messagebox.showinfo("Analyzing", f"Analyzing {selected_lang} code... Please wait.")

    def perform_analysis():
        try:
            result = run_analysis(code)

            diag_text.config(state="normal")
            diag_text.delete("1.0", tk.END)
            diag_text.insert(tk.END, result['native_analysis'].get('table', 'No metrics available'))
            diag_text.config(state="disabled")

            pres_text.config(state="normal")
            pres_text.delete("1.0", tk.END)
            pres_text.insert(tk.END, result['ai_insights'])
            pres_text.config(state="disabled")

            messagebox.showinfo("Analysis Complete", f"Checkup for {selected_lang.capitalize()} code complete!")

        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))
        finally:
            checkup_btn.config(state="normal")
            surgery_btn.config(state="normal")

    threading.Thread(target=perform_analysis).start()



def code_surgery():
    messagebox.showinfo("Code Surgery", "Refactor suggestions are shown on the right panel under 'Prescription'.")


def code_surgery():
    messagebox.showinfo("Code Surgery", "Performing code surgery...")

root = tk.Tk()
root.title("CODOC")
root.configure(bg="#6D5ACF")
root.geometry("1000x600")
root.minsize(800, 500)

# --- Fonts and Colors ---
FONT_HEADER = ("Orbitron", 24, "bold")
FONT_LABEL = ("Orbitron", 16, "bold")
FONT_TEXT = ("Courier New", 12)

COLOR_BG_MAIN = "#CBC3E3"
COLOR_FRAME = "#E5DEFF"
COLOR_TEXT_BG = "#4A3D8B"
COLOR_TEXT_FG = "white"
COLOR_BTN = "#B9A9E3"
COLOR_SIDE = "#F1EDFF"
COLOR_TITLE_BG = "#6D5ACF"
COLOR_PRESCRIPTION_BG = "#DAD3FF"

# === Main Frame ===
frame = tk.Frame(root, bg=COLOR_FRAME, bd=4, relief=tk.RIDGE)
frame.pack(padx=15, pady=15, fill='both', expand=True)

# Title
title = tk.Label(frame, text="CODOC", font=FONT_HEADER, bg=COLOR_TITLE_BG, fg="white", pady=10)
title.pack(fill="x")

# === Layout Frame ===
main_layout = tk.Frame(frame, bg=COLOR_FRAME)
main_layout.pack(fill="both", expand=True)

main_layout.columnconfigure(0, weight=3)
main_layout.columnconfigure(1, weight=1)
main_layout.rowconfigure(0, weight=1)

# === Code Area ===
code_area = tk.Frame(main_layout, bg=COLOR_FRAME)
code_area.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

control_bar = tk.Frame(code_area, bg=COLOR_FRAME)
control_bar.pack(pady=(0, 10), padx=10, anchor="w")

lang_selector = ttk.Combobox(control_bar, values=["Python", "JavaScript", "Java", "C++"], state="readonly", width=14, font=("Helvetica", 10))
lang_selector.set("Python")
lang_selector.pack(side="left", padx=(0, 10))

checkup_btn = tk.Button(control_bar, text="💜 Code Checkup", command=code_checkup, bg=COLOR_BTN, font=("Helvetica", 10, "bold"))
checkup_btn.pack(side="left")

code_text = scrolledtext.ScrolledText(code_area, bg=COLOR_TEXT_BG, fg=COLOR_TEXT_FG, insertbackground="white", font=FONT_TEXT, bd=4, relief="sunken",  wrap=tk.WORD)
code_text.insert(tk.END, "def Add():\n    pass")
code_text.pack(padx=10, pady=10, fill="both", expand=True)

# === Side Panel ===
side_panel = tk.Frame(main_layout, bg=COLOR_SIDE)
side_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)

side_panel.columnconfigure(0, weight=1)
side_panel.rowconfigure(1, weight=1)
side_panel.rowconfigure(3, weight=1)

# Diagnosis Label
diag_label = tk.Label(side_panel, text="Diagnosis:", font=FONT_LABEL, bg=COLOR_SIDE, anchor="w")
diag_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))

# Diagnosis Text (now a Text widget for better layout)
diag_text = tk.Text(side_panel, wrap="word", height=5, bg=COLOR_PRESCRIPTION_BG, fg="black", font=("Helvetica", 10))
diag_text.insert(tk.END, "")
diag_text.config(state="disabled")
diag_text.grid(row=1, column=0, sticky="nsew", padx=15)

# Prescription Label
pres_label = tk.Label(side_panel, text="Prescription:", font=FONT_LABEL, bg=COLOR_SIDE, anchor="w")
pres_label.grid(row=2, column=0, sticky="ew", padx=15, pady=(15, 5))

# Prescription Text (also a Text widget)
pres_text = tk.Text(side_panel, wrap="word", height=5, bg=COLOR_PRESCRIPTION_BG, fg="black", font=("Helvetica", 10))
pres_text.insert(tk.END, "")
pres_text.config(state="disabled")
pres_text.grid(row=3, column=0, sticky="nsew", padx=15)

# Surgery Button
surgery_btn = tk.Button(side_panel, text="🩹 Code Surgery", command=code_surgery, bg="#A18CF5", font=("Helvetica", 10, "bold"))
surgery_btn.grid(row=4, column=0, pady=20, padx=15, sticky="ew")

root.mainloop()

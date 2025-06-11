import tkinter as tk
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

# Store results
results = {}

def center_window(window, width=600, height=400):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def save_score():
    name = name_entry.get().strip()
    score = score_entry.get().strip()
    error_label.config(text="", fg="red")

    if not name:
        error_label.config(text="Name cannot be empty.")
        return
    if name.isdigit():
        error_label.config(text="Name cannot be a number.")
        return
    if name in results:
        error_label.config(text=f"Name '{name}' already exists.")
        return

    try:
        score_value = int(score)
        if score_value < 0:
            error_label.config(text="Score cannot be negative.")
            return
    except ValueError:
        error_label.config(text="Score must be a number.")
        return

    results[name] = score_value
    error_label.config(text=f"Saved: {name} - {score_value}", fg="green")
    name_entry.delete(0, tk.END)
    score_entry.delete(0, tk.END)

def show_scores():
    popup = tk.Toplevel(root)
    popup.title("Saved Scores")
    center_window(popup, 300, 300)

    if results:
        text = "\n".join([f"{name}: {score}" for name, score in results.items()])
    else:
        text = "No scores saved yet."

    tk.Label(popup, text=text, justify="left", padx=10, pady=10).pack()

# --- Main Window ---
root = tk.Tk()
root.title("Tournament Scoring System")
center_window(root)

tk.Label(root, text="Participant Name:").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Score:").pack()
score_entry = tk.Entry(root)
score_entry.pack()

error_label = tk.Label(root, text="", fg="red")
error_label.pack(pady=5)

tk.Button(root, text="Submit", command=save_score).pack(pady=5)
tk.Button(root, text="Show Saved Scores", command=show_scores).pack(pady=5)

root.mainloop()
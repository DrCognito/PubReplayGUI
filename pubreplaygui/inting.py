import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from pubreplaygui import LOG

window = tk.Tk()

def directory_picker(output):
    directory = filedialog.askdirectory(mustexist=True)
    if output is not None:
        output.delete(0, tk.END)
        output.insert(0, directory)


def validate_dir():
    pass


def start_gui():
    # Location and browser opener
    loc_picker = ttk.Frame()
    entry = ttk.Entry(master=loc_picker, width=50)
    entry.insert(0, "Dota2 Replay Folder")
    entry.pack(side=tk.LEFT, expand=True)
    
    entry_update = lambda: directory_picker(entry)
    browse_button = ttk.Button(
        master=loc_picker,
        text="Browse",
        command=entry_update
    )
    browse_button.pack(side=tk.RIGHT)
    loc_picker.pack()

    doer_frame = ttk.Frame()
    process_button = ttk.Button(
        master=doer_frame,
        text="Process replays",
    )
    process_button.pack(side=tk.LEFT, expand=True)
    res_button = ttk.Button(
        master=doer_frame,
        text="Show output",
    )
    res_button.pack(side=tk.RIGHT, expand=True)
    doer_frame.pack()


    window.mainloop()
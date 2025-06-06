import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from pathlib import Path
import os as os
from pubreplaygui import LOG
from pubreplaygui.replay import process_replay_path
from tkloguru import LoguruWidget, setup_logger
import subprocess


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.loc_picker = ttk.Frame()
        self.entry = ttk.Entry(master=self.loc_picker, width=100)
        self.entry.pack(side=tk.LEFT, expand=True)

        self.browse_button = ttk.Button(
            master=self.loc_picker,
            text="Browse",
            command=self.directory_picker
        )
        self.browse_button.pack(side=tk.RIGHT)
        self.loc_picker.pack()

        self.doer_frame = ttk.Frame()
        self.process_button = ttk.Button(
            master=self.doer_frame,
            text="Process replays",
            command=self.process_replays
        )
        self.process_button.pack(side=tk.LEFT, expand=True, fill='x')
        show_output = lambda: os.startfile(self.output_path)
        self.res_button = ttk.Button(
            master=self.doer_frame,
            text="Show output",
            command=show_output
        )
        self.res_button.pack(side=tk.RIGHT, expand=True, fill='x')
        self.rep_button = ttk.Button(
            master=self.doer_frame,
            text="Show replays",
        )
        self.rep_button.pack(side=tk.RIGHT, expand=True, fill='x')
        self.doer_frame.pack()
        
        # Logging frame
        # Intercept logging is off by default
        self.log_widget = LoguruWidget(self.parent, show_scrollbar=True, color_mode='level', max_lines=1000)
        self.log_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        setup_logger(self.log_widget)
        
        self.output_path: Path | None = None
        self._replay_path: Path | str = ''
        self._save_config: function | None = None
        self._config = None

    @property
    def replay_path(self) -> Path | str:
        return self._replay_path

    @replay_path.setter
    def replay_path(self, rpath: Path | str):
        if type(rpath) is str:
            rpath = Path(rpath)
        valid = MainApplication.validate_directory(rpath)
        if valid:
             # Save a valid path to the config.ini
            if self._config is not None:
                self._config['PATHS']['replays'] = str(rpath)
                self._save_config()

            show_replays = lambda: os.startfile(rpath)
            self.rep_button.config(command= show_replays)
            self.rep_button.config(state=tk.NORMAL)
        else:
            self.entry.config({"background": "red"})
            self.rep_button.config(command=None)
            self.rep_button.config(state=tk.DISABLED)
    
    def directory_picker(self):
        directory = filedialog.askdirectory(mustexist=True)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, directory)
        self.replay_path = directory

        return

    @staticmethod
    def validate_directory(directory: str | Path) -> bool:
        if type(directory) == str:
            dir_path = Path(directory)
        else:
            dir_path = directory
        if not dir_path.exists():
            LOG.error(f"Directory {dir_path} does not exist.")
            return False
        if not os.access(dir_path, os.R_OK):
            LOG.error(f"Directory {dir_path} does is not readable.")
            return False
        if not os.access(dir_path, os.W_OK):
            LOG.error(f"Directory {dir_path} does is not writable.")
            return False
        LOG.debug(f"Directory {dir_path} is valid.")
        return True
    
    def process_replays(self, reprocess=True):
        replay_dir = Path(self.entry.get())
        process_replay_path(replay_dir, self.output_path, reprocess)
        
        return
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
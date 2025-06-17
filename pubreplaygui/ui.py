import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from pathlib import Path
import os as os
from pubreplaygui import LOG
from pubreplaygui.replay import get_replay_files, process_replay, thread_replays
from tkloguru import LoguruWidget, setup_logger
from queue import Queue, Empty
from concurrent.futures import Future

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.loc_picker = ttk.Frame()
        self.entry = ttk.Entry(master=self.loc_picker, width=100)
        self.entry.pack(side=tk.LEFT, expand=True)
        self.entry.bind('<FocusOut>', self._update_entry)
        self.entry.bind('<Return>', self._update_entry)

        self.browse_button = ttk.Button(
            master=self.loc_picker,
            text="Browse",
            command=self.directory_picker
        )
        self.browse_button.pack(side=tk.RIGHT)
        self.loc_picker.pack(pady=5, padx=5)

        self.doer_frame = ttk.Frame()
        self.overwrite_check = ttk.Checkbutton(
            master=self.doer_frame,
            text="Overwrite existing",
            onvalue=True, offvalue=False,
            command=self.update_overwrite
        )
        self.overwrite = tk.BooleanVar(value=True)
        self.overwrite_check.config(variable=self.overwrite)
        self.overwrite_check.pack(side=tk.LEFT, expand=True, fill='x')
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
        self.doer_frame.pack(pady=5, padx=5)
        
        # Logging frame
        # Intercept logging is off by default
        self.log_widget = LoguruWidget(self.parent, show_scrollbar=True, color_mode='level', max_lines=1000)
        self.log_widget.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        # Do this manually to not remove current handler
        # setup_logger(self.log_widget)
        LOG.add(self.log_widget.sink, backtrace=True, diagnose=True, level="INFO")
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(orient=tk.HORIZONTAL, length=100,)
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.output_path: Path | None = None
        self._replay_path: Path | str = ''
        self._save_config: function | None = None
        self._config = None
        # Replay processing queue
        self.replay_queue = Queue()
        # Register the replay queue check
        self.parent.after(200, self.check_queue)

    def update_overwrite(self):
        if "OPTIONS" not in self._config:
            self._config["OPTIONS"] = {}
        self._config["OPTIONS"]["overwrite_output"] = str(self.overwrite.get())
        self._save_config()
        return

    @property
    def replay_path(self) -> Path | str:
        return self._replay_path

    @replay_path.setter
    def replay_path(self, rpath: Path | str):
        if type(rpath) is str:
            rpath = Path(rpath)
        self._replay_path = rpath
        valid = MainApplication.validate_directory(rpath)
        if valid:
             # Save a valid path to the config.ini
            if self._config is not None:
                self._config['PATHS']['replays'] = str(rpath)
                self._save_config()

            show_replays = lambda: os.startfile(rpath)
            self.rep_button.config(command=show_replays)
            self.rep_button.config(state=tk.NORMAL)
            self.process_button.config(state=tk.NORMAL)
        else:
            self.entry.config({"background": "red"})
            self.rep_button.config(command=None)
            self.rep_button.config(state=tk.DISABLED)
            self.process_button.config(state=tk.DISABLED)
    
    def directory_picker(self):
        directory = filedialog.askdirectory(mustexist=True)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, directory)
        self.replay_path = directory

        return
    
    def _update_entry(self, event):
        self.replay_path = self.entry.get()

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
    
    # def process_replays(self, reprocess=True):
    #     replay_dir = Path(self.entry.get())
    #     process_replay_path(replay_dir, self.output_path, reprocess, self.progress_bar)
        
    #     return
    def check_queue(self):
        running = Queue()
        while self.replay_queue.qsize():
            try:
                replay:str
                task: Future
                replay, task = self.replay_queue.get_nowait()
                if not task.done():
                    running.put((replay, task))
                    continue
                # Expect dict[name:task]
                LOG.info(f"Processed {replay}")
                LOG.debug(f"Process for {replay} completed with:")
                LOG.debug(task.result().stdout)
                self.progress_bar.step()
            except Empty:
                LOG.debug("All ")
                pass
        # Re-add running
        self.replay_queue = running
        # Re-register our check
        self.parent.after(20, self.check_queue)


    def process_replays(self):
        reprocess = not self.overwrite.get()
        thread_replays(
            self.replay_path, self.output_path,
            reprocess, self.progress_bar, self.replay_queue)
        LOG.debug(f"Submitted all replays. Reprocess is {reprocess}")

        return
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
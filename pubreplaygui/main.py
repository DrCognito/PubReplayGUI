from pathlib import Path
from pubreplaygui import LOG, PARSER_LOC, CONFIG_LOC
from pubreplaygui.config import get_create_config, save_config
from pubreplaygui.ui import MainApplication
from pubreplaygui.replay import process_replay_path
import tkinter as tk
import tkinter.ttk as ttk

if __name__ == "__main__":
    # Setup the gui
    root = tk.Tk()
    main_ui = MainApplication(root)
    main_ui.pack(side="top", fill="both", expand=True)
    # Save config lambda
    config = get_create_config()
    LOG.debug("Loaded config file.")
    main_ui.entry.insert(0, config['PATHS']['replays'])
    # Output
    main_ui.output_path = Path(config["PATHS"]['output']).resolve()
    main_ui._config = config
    main_ui._save_config = lambda : save_config(CONFIG_LOC, config)
    # Set the directory to our saved directory
    LOG.debug("Starting UI")
    root.mainloop()
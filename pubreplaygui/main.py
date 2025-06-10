from pathlib import Path
from pubreplaygui import LOG, PARSER_LOC, CONFIG_LOC
from pubreplaygui.config import get_create_config, save_config
from pubreplaygui.ui import MainApplication
from pubreplaygui.replay import process_replay_path
import tkinter as tk
import tkinter.ttk as ttk


def environment_check():
    valid = True
    if not CONFIG_LOC.exists():
        LOG.error("Config.ini is missing.")
        valid = False
    if not PARSER_LOC.exists():
        LOG.error(f"Parser binary is missing at {PARSER_LOC}")
        valid = False
    if not Path("./output").exists():
        LOG.error("Output folder is missing.")
        valid = False
    if valid:
        LOG.info("Environment check complete without error.")
    else:
        LOG.error("Environment check failed!")

if __name__ == "__main__":
    # Setup the gui
    root = tk.Tk()
    main_ui = MainApplication(root)
    main_ui.pack(side="top", fill="both", expand=True)
    # Save config lambda
    config = get_create_config()
    LOG.debug("Loaded config file.")
    # Set the directory to our saved directory
    main_ui.entry.insert(0, config['PATHS']['replays'])
    main_ui.replay_path = config['PATHS']['replays']
    # Output
    main_ui.output_path = Path(config["PATHS"]['output']).resolve()
    main_ui._config = config
    main_ui._save_config = lambda : save_config(CONFIG_LOC, config)
    # Env check
    environment_check()
    # Start the UI
    LOG.debug("Starting UI")
    root.title("PubReplay GUI")
    root.mainloop()
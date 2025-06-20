from configparser import ConfigParser
from pathlib import Path
from pubreplaygui import LOG, CONFIG_LOC


def make_config(conf_path: Path) -> ConfigParser:
    config = ConfigParser()
    config["PATHS"] = {
        "replays": "Select directory.",
        "output": "output",
    }
    config["OPTIONS"] = {
        "overwrite_output": 1
    }

    save_config(conf_path, config)

    return config


required_headings = ["PATHS", "OPTIONS"]
def get_create_config(conf_path: Path = CONFIG_LOC) -> ConfigParser:
    config = ConfigParser()
    if conf_path.exists():
        try:
            config.read(conf_path)
            LOG.debug({section: dict(config[section]) for section in config.sections()})
        except:
            LOG.opt(exception=True).error(f"Failed to read config at {conf_path}")
            raise
        # Make sure we have all the available sections
        if all(map(lambda x: x in config, required_headings)):
            return config
        else:
            LOG.warning(f"config.ini was invalid and has been reset.")
    else:
        LOG.info(f"No existing config file found, creating a new one.")
    return make_config(conf_path)


def save_config(conf_path: Path, config: ConfigParser):
    LOG.info(f"Wrote config to {conf_path}")
    with open(conf_path, "w") as file:
        config.write(file)
        

if __name__ == "__main__":
    config = get_create_config(CONFIG_LOC)
    print({section: dict(config[section]) for section in config.sections()})
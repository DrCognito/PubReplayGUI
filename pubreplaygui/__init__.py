from loguru import logger as LOG
from pathlib import Path

LOG.remove()
LOG.add("app.log", rotation="5 MB", level='DEBUG', retention=0)

CONFIG_LOC = Path("config.ini")
PARSER_LOC = Path("./bin/PubParser.exe")
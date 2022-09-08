import importlib.metadata
from pathlib import Path

from appdirs import AppDirs

__version__ = importlib.metadata.version("ylva")
APP_IDENTIFIER = "net.nausicaea.ylva"
APP_AUTHOR = "nausicaea"
YML_SUFFIX = ".yml"
YML_SUFFIXES = (YML_SUFFIX, ".yaml")
APPDIRS = AppDirs(APP_IDENTIFIER, APP_AUTHOR)
CONFIG_DIR = Path(APPDIRS.user_config_dir)
DEFAULT_CONFIG_FILE = CONFIG_DIR.joinpath(f"config{YML_SUFFIX}")

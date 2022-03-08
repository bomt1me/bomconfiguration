import re


FILENAME = "bom"
FILESUFFIX = "conf.json"
OVERRIDE = "override"
KEY_DELIMITER = "."
QUOTE_CHAR = '"'
BASE_FILENAME = f"{FILENAME}.{FILESUFFIX}"
FILENAME_TEMPLATE = f"{FILENAME}." + "{specifier}" f".{FILESUFFIX}"
ENV_VAR_RE = re.compile(r"^\$\{?(([\w]+)([\:]?[\-\?])?([\w]+)?)\}?$")

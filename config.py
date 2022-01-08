from datetime import datetime
from numpy import nan
from pandas import NaT as nat

DEBUG = False
BASE_FILE_FORMAT = "%Y%m%d-%H%M-"  # means "yyyyMMdd-HHmm-", example: "20210909-0750-"
BASE_FORMAT_DATE = "%Y%m%d"
BASE_FORMAT_TIME = "%H%M"
DATETIME_PREFIX = datetime.now().strftime(BASE_FILE_FORMAT)
SEED = 42
LINKS_RE = "https?:\S+|http?:\S+"
TIMESTAMP_START = datetime(1899, 12, 30)
STRFTIME = {
    "d": 2,
    "m": 2,
    "Y": 4,
    "H": 2,
    "M": 2,
}

EMPTY_VALUES = set([nan, None, "", nat])

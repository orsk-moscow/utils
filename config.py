import locale
from datetime import datetime

from numpy import nan
from pandas import NaT as nat

LOCALE = 'ru_RU.UTF-8'
locale.setlocale(locale.LC_TIME, LOCALE)
DEBUG = False
BASE_FILE_FORMAT = (
    "%Y%m%d-%H%M-"  # means "yyyyMMdd-HHmm-", example: "20210909-0750-"
)
BASE_FORMAT_DATE = "%Y%m%d"
BASE_FORMAT_TIME = "%H%M"
FORMAT_DATE_FOR_READING = "%d %B %Y (%A)"
FORMAT_TIME_FOR_READING = "%Hч %Mмин"
FORMAT_DATETIME_FOR_READING = f"{FORMAT_DATE_FOR_READING} {FORMAT_TIME_FOR_READING}"

now = datetime.now()
DATETIME_PREFIX = now.strftime(BASE_FILE_FORMAT)
DATE = now.strftime(BASE_FORMAT_DATE)
TIME = now.strftime(BASE_FORMAT_TIME)
DATE_FOR_READING = now.strftime(FORMAT_DATE_FOR_READING)
TIME_FOR_READING = now.strftime(FORMAT_TIME_FOR_READING)

SEED = 42
LINKS_RE = "https?:\S+|http?:\S+"
RE_TOKENS = r"\w+|[^\w\s]+"
TIMESTAMP_START = datetime(1899, 12, 30)
STRFTIME = {
    "d": 2,
    "m": 2,
    "Y": 4,
    "H": 2,
    "M": 2,
}

EMPTY_VALUES = set([nan, None, "", nat])
TIMEOUT = 3.027
DISK = (
    "Yandex.Disk.localized"  # Variants: "Downloads" or "Yandex.Disk.localized"
)
DIR_DATA = "-DATA"
DIR_DEBUG = "-DEBUG"
DIR_LOGS = "-LOGS"
SEP = '\t'

# OPTIONS FOR PANDAS .CSV AND .TSV IO OPERATIONS
KWARGS_CSV_INPUT = {
    "sep": SEP,
    "encoding": "utf-8-sig",
    "lineterminator": '\n',
    'dtype': 'str',
}
KWARGS_CSV_OUTPUT = {
    "sep": SEP,
    "encoding": "utf-8-sig",
    "index": False,
}

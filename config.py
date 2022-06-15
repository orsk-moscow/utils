import getpass
import locale
import os
import re
from datetime import datetime
from hashlib import md5

from numpy import nan
from pandas import NaT as nat

LOCALE = "ru_RU.UTF-8"
locale.setlocale(locale.LC_TIME, LOCALE)

# NOTE general options
DEBUG = False
SEED = 42
EMPTY_VALUES = set([nan, None, "", nat])
# actively used in google spreadsheets
TIMESTAMP_START = datetime(1899, 12, 30)

# NOTE strftime strings
# means "yyyyMMdd-HHmm-", example: "20210909-0750-":
BASE_FILE_FORMAT = "%Y%m%d-%H%M-"
BASE_FORMAT_DATE = "%Y%m%d"
BASE_FORMAT_TIME = "%H%M"
FORMAT_DATE_FOR_READING = "%d %B %Y (%A)"
FORMAT_TIME_FOR_READING = "%Hч %Mмин"
FORMAT_DATETIME_FOR_READING = (
    f"{FORMAT_DATE_FOR_READING} {FORMAT_TIME_FOR_READING}"
)
STRFTIME = {"d": 2, "m": 2, "Y": 4, "H": 2, "M": 2}
WEEK_DAYS_RU = {
    "понед",
    "вторн",
    "среда",
    "четве",
    "пятни",
    "суббо",
    "воскр",
}
MONTHS_RU = {
    "янв",
    "фев",
    "мар",
    "апр",
    "май",
    "июн",
    "июл",
    "авг",
    "сен",
    "окт",
    "ноя",
    "дек",
}
MONTHS_EN = {
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
}
WEEK_DAYS_EN = {
    "monda",
    "tuesd",
    "wedne",
    "thurs",
    "frida",
    "satur",
    "sunda",
}
STRFTIME_LOCAL = {
    "A": {
        "num": 5,
        "values": WEEK_DAYS_RU if LOCALE == "ru_RU.UTF-8" else WEEK_DAYS_EN,
    },
    "B": {
        "num": 3,
        "values": MONTHS_RU if LOCALE == "ru_RU.UTF-8" else MONTHS_EN,
    },
}

# NOTE datetime strings
now = datetime.now()
DATETIME_PREFIX = now.strftime(BASE_FILE_FORMAT)
DATE = now.strftime(BASE_FORMAT_DATE)
TIME = now.strftime(BASE_FORMAT_TIME)
DATE_FOR_READING = now.strftime(FORMAT_DATE_FOR_READING)
TIME_FOR_READING = now.strftime(FORMAT_TIME_FOR_READING)

# NOTE logging options
NAME_NODE = os.uname().nodename
NAME_OS = os.uname().sysname
NAME_ARCH = os.uname().machine
NAME_OS_VERSION = os.uname().release
NAME_PYTHON = os.sys.version
NAME_LOGIN = os.getlogin()
NAME_USER = getpass.getuser()
IDHASH = md5(bytes(f"{now}+{NAME_USER}", encoding="utf8")).hexdigest()
LOG_FORMAT = (
    f"{IDHASH} %(asctime)s %(levelname)s %(name)s %(funcName)s: %(message)s"
)

# NOTE usefull regular expressions patterns
RE_LINKS = r"https?:\S+|http?:\S+"
RE_TOKENS = r"\w+|[^\w\s]+"
RE_NEWLINES = r"[^\n]+"

# NOTE text processing info
SEP = "\t"
TAB = "".join(4 * " ")
END_OF_LINE = ".\n"  # r".\n"
NEWLINE_SUMBOL = "|"
PRE_PATTERNS = [
    # delete rubbish separators. change to 4 whitesapces for code blocks:
    (re.compile(SEP), TAB),
    # delete rubbish spaces at the end of line:
    (re.compile("[\t ]+\n"), "\n"),
    # delete rubbish newlines:
    (re.compile("\n\n+"), "\n\n"),
]
NOISE_PATTERNS = [
    (re.compile(f"{SEP}"), ". "),  # delete rubbish separators
    (re.compile('"'), " ",),
    (re.compile(r"\s+\n"), "\n"),  # delete empty lines and new lines
    (r"(?:\.+)\n+", END_OF_LINE),
]
google_meet = "Контактная.+\nСсылка на видеовстречу.+\nВы также можете позвонить по телефону.+\nДополнительные номера телефонов.+\n"
POST_PATTERNS = [  # (паттерн, замена, тэг1, личное?)
    (re.compile(google_meet), "", "рабочая встреча", -1),
]

# NOTE network
TIMEOUT = 3.027

# NOTE options for .csv AND .tsv io operations, firtsly, pandas
SEP = "\t"
KWARGS_CSV_INPUT = {
    "sep": SEP,
    "encoding": "utf-8-sig",
    "lineterminator": "\n",
    "dtype": "str",
}
KWARGS_CSV_OUTPUT = {
    "sep": SEP,
    "encoding": "utf-8-sig",
    "index": False,
}

# NOTE yadisk filesystem properties
# Variants: "Downloads" or "Yandex.Disk.localized"
DISK = "Yandex.Disk.localized"
DIR_DATA = "-DATA"
DIR_DEBUG = "-DEBUG"
DIR_LOGS = "-LOGS"

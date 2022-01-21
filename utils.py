import logging
from collections import defaultdict
from datetime import datetime, timedelta
import os
from typing import Dict, List, Literal, Optional, Tuple, TypedDict, Union

import yaml
from path import Path

from .config import BASE_FILE_FORMAT, DEBUG, STRFTIME

logger = logging.getLogger(__name__)


def validate_path(path_obj: Path, endswith: str):
    log.info(
        f"проверка существования объекта '{path_obj}' с типом файла '{endswith}'"
    )
    if not path_obj.exists():
        log.error(f"""filename '{path_obj}' does not exists""")
    elif not path_obj.isfile():
        log.error(f"""filename '{path_obj}' is not a file""")
    elif not path_obj.endswith(endswith):
        log.error(f"""filename '{path_obj}' is not a '*.{endswith}' file""")
    else:
        log.info("проверка существования объекта ОК")
        return path_obj
    exit()


def make_logging_config(
    debug=DEBUG, in_file=True, open_for_debug: bool = False
):
    if in_file:
        logdir = Path(".debug" if debug else ".logs")
        logdir.mkdir_p()
        logfile = Path.joinpath(
            logdir,
            f"""{datetime.today().strftime(BASE_FILE_FORMAT)}{"-DEBUG"if debug else ""}.log""",
        )
    if debug:
        log.basicConfig(
            level=log.DEBUG,
            format="%(asctime)s %(levelname)s %(name)s %(funcName)s: %(message)s",
            filename=logfile if in_file else None,
            force=True,  # python 3.8+ required
        )
        log.debug("this is test run")
    else:
        log.basicConfig(
            level=log.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(funcName)s: %(message)s",
            filename=logfile if in_file else None,
            force=True,  # python 3.8+ required
        )
        log.info("this is production run")
    if in_file and open_for_debug and debug:
        logfile.touch()
        os.system(f"open {logfile}")
    return


def check_ts_mask(candidate, timestamp):
    cnt = 0
    itrtr = 0
    while cnt < len(timestamp):
        if itrtr >= len(candidate):
            return False
        if timestamp[cnt] == "%":
            pass
        elif timestamp[cnt] in STRFTIME.keys():
            num_digits = STRFTIME[timestamp[cnt]] + itrtr
            while itrtr < num_digits:
                if candidate[itrtr] not in set("1234567890"):
                    return False
                itrtr += 1
        else:
            if timestamp[cnt] != candidate[itrtr]:
                return False
            itrtr += 1
            pass
        cnt += 1
        continue
    try:
        return datetime.strptime(
            candidate[:num_digits], timestamp
        )  # ValueError: unconverted data remains: :29.761Z - отсекаем хвост по кол-ву нужных цифр
    except ValueError:
        pass
    return False


def get_ts_candidat_len(timestamp):
    cnt = 0
    ts_len = 0
    while cnt < len(timestamp):
        if timestamp[cnt] == "%":
            if cnt + 1 >= len(timestamp):
                raise ValueError(
                    f"Wrong timestamp format '{timestamp}': can not correctly parse symbol at index {cnt}"
                )
            cnt += 1
            sign_len = STRFTIME.get(timestamp[cnt])
            if not sign_len:
                raise ValueError(f"Unknown modifier '{timestamp[cnt]}'")
            ts_len += sign_len
        else:
            ts_len += 1
        cnt += 1
    return ts_len


def parse_timestamp(text, timestamp, index=None):

    ts_len = get_ts_candidat_len(timestamp)
    size = len(text)
    cnt, current, res = 0, -1, dict()
    if size == 0:
        return res

    while cnt < size:
        if ts_len and cnt + ts_len > size:
            break
        ts = check_ts_mask(text[cnt : cnt + ts_len], timestamp)
        if not ts:
            cnt += 1
            continue
        if current != -1:
            key_candidat = datetime.strptime(
                text[current : current + ts_len], timestamp,
            )
            if index:
                while True:
                    if key_candidat in index:
                        key_candidat += timedelta(seconds=1)
                    else:
                        index |= set([key_candidat])
                        break
            else:
                index = set([key_candidat])
            res[key_candidat] = text[current + ts_len : cnt]
        current = cnt
        cnt += 1
        cnt += ts_len

    if current == -1:
        return res

    key_candidat = datetime.strptime(
        text[current : current + ts_len], timestamp
    )
    if index:
        while True:
            if key_candidat in index:
                key_candidat += timedelta(seconds=1)
            else:
                index |= set([key_candidat])
                break
    res[key_candidat] = text[current + ts_len :]
    return res


def dict_union_with_ts_as_key(*dicts):
    result_dict = dict()
    for dict_ in dicts:
        for old_key in dict_:
            new_key = old_key
            while True:
                if new_key in result_dict.keys():
                    new_key += timedelta(seconds=1)
                else:
                    break
            result_dict[new_key] = dict_[old_key]
    return result_dict


def mirror_dict(dctnr: dict) -> dict:
    res = defaultdict(list)
    for (k, v) in dctnr.items():
        res[v].append(k)
    return res


class column_dtypes_attributes(TypedDict):
    dtype: str


class dtype_columns_attributes(TypedDict):
    string: Optional[List[str]]
    number: Optional[List[str]]
    date: Optional[List[str]]
    time: Optional[List[str]]


def get_sheet_info(
    abspath: Path,
) -> Tuple[
    Dict[str, column_dtypes_attributes],
    dtype_columns_attributes,
    Dict[str, str],
]:
    validate_path(abspath, endswith=".yaml")
    with open(abspath) as f:
        dict_dtypes = yaml.safe_load(f)
    column_dtypes = dict([(k, dict_dtypes[k]["dtype"]) for k in dict_dtypes])
    default_values = dict(
        [
            (k, dict_dtypes[k]["default"])
            for k in dict_dtypes
            if dict_dtypes[k].get("default")
        ]
    )
    dtype_columns = mirror_dict(column_dtypes)
    return (column_dtypes, dtype_columns, default_values)


def prettify_input(
    user_input: str,
    stay_whitespaces: bool = True,
    case: Optional[Literal["upper", "lower"]] = None,
) -> str:
    tokens = user_input.strip().split()
    string = (" " if stay_whitespaces else "").join(tokens)
    if not case:
        pass
    elif case == "upper":
        string = string.upper()
    elif case == "lower":
        string = string.lower()
    return string

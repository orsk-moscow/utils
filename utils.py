from path import Path
import logging
from datetime import datetime, timedelta
from path import Path
import numpy as np
from .config import BASE_FILE_FORMAT, DEBUG, STRFTIME
from typing import Any
from collections import defaultdict


def validate_path(path_obj: Path, endswith):
    if not path_obj.exists():
        logging.error(f"""filename '{path_obj}' does not exists""")
    elif not path_obj.isfile():
        logging.error(f"""filename '{path_obj}' is not a file""")
    elif not path_obj.endswith(endswith):
        logging.error(f"""filename '{path_obj}' is not a '*.{endswith}' file""")
    else:
        return path_obj
    exit()


def make_logging_config(debug=DEBUG, in_file=True):
    if in_file:
        logdir = Path(".debug" if debug else ".logs")
        logdir.mkdir_p()
        logfile = Path.joinpath(
            logdir,
            f"""{datetime.today().strftime(BASE_FILE_FORMAT)}{"-DEBUG"if debug else ""}.log""",
        )
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s %(levelname)s %(name)s %(funcName)s: %(message)s",
            filename=logfile if in_file else None,
            force=True,  # python 3.8+ required
        )
        logging.debug("this is test run")
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s %(funcName)s: %(message)s",
            filename=logfile if in_file else None,
            force=True,  # python 3.8+ required
        )
        logging.info("this is production run")
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
        return datetime.strptime(candidate, timestamp)
    except:
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

    key_candidat = datetime.strptime(text[current : current + ts_len], timestamp)
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

#! /usr/bin/env python3
import logging
from pathlib import Path

from utils import make_logging_config

log = logging.getLogger(Path(__file__).name)

DEBUG = True
DIR_WHITELIST = [
    'Downloads',
    'Desktop',
]
DIR_DEST = 'Pictures'
YADISK = 'Yandex.Disk.localized'
YAFOLDER = 'Downloads'
MEDIA = {
    'png',
    'jpg',
    'jpeg',
    'png',
    'avi',
    'mov',
    'mp4',
    'mpeg4',
    'hevc',
}

if __name__ == '__main__':
    make_logging_config(debug=DEBUG)
    current = Path(__file__)
    home = current.home()
    dest = home.joinpath(DIR_DEST)
    yandex = home.joinpath(YADISK).joinpath(YAFOLDER)
    media = set([f".{str(e).lower().replace('.','')}" for e in MEDIA])

    for e in DIR_WHITELIST:
        dir = home.joinpath(e)
        if not dir.exists():
            continue
        for e in dir.iterdir():
            if e.name.startswith("."):
                continue
            if e.is_file() and e.suffix.lower() in media:
                dest_ = dest.joinpath(e.name)
                e.replace(dest_)
                log.info(
                    f"Файл '{e}' перемещен по пути '{dest_}'")

    for e in home.iterdir():
        if e.name.startswith("."):
            continue
        if e.name.startswith("file."):
            log.info(f"файл '{e}' пропущен: служебный")
            continue
        if e.is_file():
            t = e.suffix
            t = t.lower()
            dest_ = dest.joinpath(
                e.name) if t in media else yandex.joinpath(e.name)
            e.replace(dest_)
            log.info(
                f"Файл '{e}' перемещен по пути '{dest_}'")

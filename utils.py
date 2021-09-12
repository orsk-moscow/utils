from path import Path
import logging
from datetime import datetime
from path import Path
from .config import BASE_FILE_FORMAT, DEBUG


def validate_path(path_obj, endswith):
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

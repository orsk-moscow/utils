import logging
from datetime import datetime, timedelta
from typing import Union, Mapping

import gspread
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from path import Path
from pandas import DataFrame

from .config import TIMESTAMP_START
from utils.utils import validate_path, make_logging_config, mirror_dict

GOOGLE_API_SCOPE = ["https://www.googleapis.com/auth/drive"]
ENCODING = "utf-8-sig"
RENDER_OPTION = "UNFORMATTED_VALUE"


class google_table:
    def __init__(
        self,
        table: str,
        sheet: Union[str, int],
        secret_json: Path,
        column_dtypes: Mapping[str, type],
    ) -> None:
        self.table = table
        validate_path(Path(secret_json).abspath(), endswith=".json")
        self.secret_json = secret_json
        self.scopes = GOOGLE_API_SCOPE
        self.sheet_name = None if type(sheet) == int else sheet
        self.sheet_num = None if type(sheet) == str else sheet
        self.column_dtypes = column_dtypes
        self.dtype_columns = mirror_dict(column_dtypes)
        pass

    def _login(self) -> gspread.Client:
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            self.secret_json, scopes=self.scopes,
        )
        self.client = gspread.authorize(self.creds)
        return self.client

    def get_sheet(self) -> gspread.Worksheet:
        opened = self.client.open(self.table)
        self.sheet = (
            opened.worksheet(self.sheet_name)
            if self.sheet_name
            else opened.get_worksheet(self.sheet_num)
        ).get(value_render_option=RENDER_OPTION)
        return self.sheet

    @staticmethod
    def calc_datetime(days_since_1899: Union[float, str]) -> datetime:
        if type(days_since_1899) == str:
            if days_since_1899 == "":
                return np.datetime64("nat")
            else:
                message = "parameter `days_since_1899` should be `float`, not `str`"
                logging.error(message)
                raise ValueError(message)
        return TIMESTAMP_START + timedelta(days_since_1899)

    @staticmethod
    def get_gspread_date(timestamp: datetime) -> float:
        days_since_1899 = (timestamp - TIMESTAMP_START) / timedelta(days=1)
        return days_since_1899

    def download(self) -> DataFrame:
        result = DataFrame()
        self._login()
        self.get_sheet()
        dctnr = dict([tpl for tpl in self.sheet if len(tpl) == len(self.column_dtypes)])
        result = DataFrame.from_dict(dctnr, orient="index").reset_index()
        result.columns = list(self.column_dtypes.keys())
        if self.dtype_columns.get(datetime):
            for col in self.dtype_columns.get(datetime):
                result[col] = result[col].apply(self.calc_date)
        return result

    def to_cloud(self, dataframe: DataFrame) -> bool:
        download_success = True
        return True if download_success else False


def test() -> None:
    make_logging_config(debug=True)
    column_dtypes = {
        "Транзакция": int,
        "Дата": datetime,
        "Примечание": str,
        "Идентификатор операции": str,
        "Входящий баланс": "formula",
        "Исходящий баланс": "formula",
        "№ п.п": int,
    }
    google_table(
        "План-1Q22", "1Q22", "secret-gspreadsheets.json", column_dtypes
    ).download()
    pass


if __name__ == "__main__":
    test()  # /Users/popov-iv/opt/anaconda3/bin/python3 -m utils.gtables

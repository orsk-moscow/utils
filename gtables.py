import logging
from datetime import datetime, timedelta
from string import ascii_uppercase
from typing import Mapping, Union

import gspread
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from pandas import DataFrame, to_datetime
from path import Path

from utils.config import TIMESTAMP_START, EMPTY_VALUES
from utils.utils import make_logging_config, mirror_dict, validate_path

GOOGLE_API_SCOPE = ["https://www.googleapis.com/auth/drive"]
ENCODING = "utf-8-sig"
RENDER_OPTION = "FORMULA"  # "UNFORMATTED_VALUE"
FILLNA = ""


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
        self._login()
        self.get_sheet()
        pass

    def _login(self) -> gspread.Client:
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(
            self.secret_json, scopes=self.scopes,
        )
        self.client = gspread.authorize(self.creds)
        return self.client

    def get_sheet(self) -> gspread.Worksheet:
        opened = self.client.open(self.table)
        self.sheet_io = (
            opened.worksheet(self.sheet_name)
            if self.sheet_name
            else opened.get_worksheet(self.sheet_num)
        )
        self.sheet = self.sheet_io.get(value_render_option=RENDER_OPTION)
        return self.sheet

    @staticmethod
    def calc_datetime(days_since_1899: Union[float, str, int]) -> datetime:
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
        if type(timestamp).__name__ == "datetime":
            days_since_1899 = (timestamp - TIMESTAMP_START) / timedelta(days=1)
        elif type(timestamp).__name__ == "date":
            days_since_1899 = (timestamp - TIMESTAMP_START.date()) / timedelta(days=1)
        elif type(timestamp).__name__ == "Timestamp":
            days_since_1899 = (timestamp.to_pydatetime() - TIMESTAMP_START) / timedelta(
                days=1
            )
        else:
            days_since_1899 = (timestamp - TIMESTAMP_START) / timedelta(days=1)
        return days_since_1899

    @staticmethod
    def convert_values(
        value: Union[str, int, float, datetime], goal_type: str = "int"
    ) -> Union[str, int, float, datetime]:
        if goal_type == "int":
            return int(value)
        if goal_type == "number":
            return float(value)
        if goal_type == "date" and (
            type(value) == int or type(value) == float or value == ""
        ):
            return google_table.calc_datetime(value)
        if goal_type == "date":
            return to_datetime(value)
        return value

    def download(self) -> DataFrame:
        self.df_from_cloud = DataFrame(self.sheet[1:], columns=self.sheet[0])
        for col in self.df_from_cloud.columns:
            if not self.column_dtypes.get(col):
                message = f"В названии партии данных есть столбец '{col}', для которого не указан тип"
                logging.error(message)
                raise KeyError(message)
            self.df_from_cloud[col] = self.df_from_cloud[col].apply(
                lambda v: google_table.convert_values(v, self.column_dtypes.get(col))
            )
        return self.df_from_cloud

    def insert_into_same_sheet(
        self,
        dataframe: DataFrame,  # TODO should I copy 'dataframe' before?
        startswith: int = 1,
        endswith: int = -1,
        header: bool = True,
    ) -> bool:
        for col in dataframe.columns:
            is_datetime = False
            while True:
                sample = (
                    dataframe[col].sample(1).iloc[0]
                )  # todo потенциально слабое место, долгая итерация в случае большого числа пустых значений, нужно переделать
                if sample in EMPTY_VALUES:
                    continue
                is_datetime = (
                    True
                    if (
                        ("date" in type(sample).__name__.lower())
                        or ("time" in type(sample).__name__.lower())
                    )
                    else False
                )
                break
            if not is_datetime:
                continue
            dataframe[col] = dataframe[col].apply(
                lambda dt: google_table.get_gspread_date(dt)
            )
        dataframe.fillna(FILLNA, inplace=True)
        try:
            self.sheet_io.update(
                ([dataframe.columns.values.tolist()] if header else [])
                + dataframe.values.tolist(),
                raw=False,
            )
            download_success = True
            logging.info(
                f"загрузка таблицы в google tables '{self.table}/{self.sheet_name}' прошла успешно"
            )
        except Exception as e:
            e = str(e).replace("'", '"')
            logging.error(
                f"при загрузке таблицы в google tables '{self.table}/{self.sheet_name}' возникла ошибка '{e}'"
            )
            download_success = False
        finally:
            pass
        return download_success


def test() -> None:
    make_logging_config(debug=True)
    column_dtypes = {
        "Транзакция": "number",
        "Дата": "date",
        "Примечание": "string",
        "Идентификатор операции": "string",
        "Входящий баланс": "string",
        "Исходящий баланс": "string",
        "№ п.п": "string",
    }
    google_table(
        "План-1Q22", "1Q22", "secret-gspreadsheets.json", column_dtypes
    ).download()
    pass


if __name__ == "__main__":
    test()  # /Users/popov-iv/opt/anaconda3/bin/python3 -m utils.gtables

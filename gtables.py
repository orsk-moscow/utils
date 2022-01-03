import logging
from datetime import datetime, timedelta
from string import ascii_uppercase
from typing import Mapping, Union

import gspread
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from pandas import DataFrame, to_datetime
from path import Path

from utils.config import TIMESTAMP_START
from utils.utils import make_logging_config, mirror_dict, validate_path

GOOGLE_API_SCOPE = ["https://www.googleapis.com/auth/drive"]
ENCODING = "utf-8-sig"
RENDER_OPTION = "FORMULA"  # "UNFORMATTED_VALUE"


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
        days_since_1899 = (timestamp - TIMESTAMP_START) / timedelta(days=1)
        return days_since_1899

    @staticmethod
    def convert_values(
        value: Union[str, int, float, datetime], goal_type: str = "int"
    ) -> Union[str, int, float, datetime]:
        if goal_type == "int":
            return int(value)
        if goal_type == "float":
            return float(value)
        if goal_type == "datetime" and (
            type(value) == int or type(value) == float or value == ""
        ):
            return google_table.calc_datetime(value)
        if goal_type == "datetime":
            return to_datetime(value)
        return value

    def download(self) -> DataFrame:
        self._login()
        self.get_sheet()
        self.df_from_cloud = DataFrame(self.sheet[1:], columns=self.sheet[0])
        for col in self.df_from_cloud.columns:
            if not self.column_dtypes.get(col):
                raise KeyError(
                    f"В названии партии данных есть столбец '{col}', для которого не указан тип"
                )
            self.df_from_cloud[col] = self.df_from_cloud[col].apply(
                lambda v: google_table.convert_values(v, self.column_dtypes.get(col))
            )
        return self.df_from_cloud

    def insert_into_same_sheet(
        self,
        dataframe: DataFrame,  # TODO should I copy 'dataframe' before?
        startswith: int = 1,
        endswith: int = -1,
    ) -> bool:
        datetime_columns = self.dtype_columns.get("datetime")
        if not datetime_columns:
            pass
        else:
            for col in datetime_columns:
                dataframe[col] = dataframe[col].apply(
                    lambda dt: google_table.get_gspread_date(dt)
                )
        data = list(dataframe.columns)
        data.extend(dataframe.values.tolist())
        batch = [
            {
                "range": f"A{startswith}:{ascii_uppercase[dataframe.shape[1]]}{endswith if endswith!=-1 else len(dataframe)+1}",
                "values": data,
            }
        ]  # NOTE old values in this 'range' will be updated
        self.sheet_io.batch_update(batch, value_input_option="USER_ENTERED")
        download_success = True
        return True if download_success else False


def test() -> None:
    make_logging_config(debug=True)
    column_dtypes = {
        "Транзакция": "float",
        "Дата": "date",
        "Примечание": "str",
        "Идентификатор операции": "str",
        "Входящий баланс": "formula",
        "Исходящий баланс": "formula",
        "№ п.п": "formula",
    }
    google_table(
        "План-1Q22", "1Q22", "secret-gspreadsheets.json", column_dtypes
    ).download()
    pass


if __name__ == "__main__":
    test()  # /Users/popov-iv/opt/anaconda3/bin/python3 -m utils.gtables

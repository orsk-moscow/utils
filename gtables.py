import logging
from datetime import datetime, timedelta
from string import ascii_uppercase
from typing import Mapping, Union

import gspread
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from pandas import DataFrame, to_datetime
from pathlib import Path

from utils.config import TIMESTAMP_START
from utils.utils import make_logging_config, mirror_dict, validate_path

log = logging.getLogger(__name__)

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
        validate_path(secret_json.absolute(), endswith=".json")
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

    def clear(self) -> None:
        self.sheet_io.clear()
        pass

    @staticmethod
    def calc_datetime(days_since_1899: Union[float, str, int]) -> datetime:
        if type(days_since_1899) == str:
            if days_since_1899 == "":
                return np.datetime64("nat")
            else:
                message = (
                    "parameter `days_since_1899` should be `float`, not `str`"
                )
                log.error(message)
                raise ValueError(message)
        return TIMESTAMP_START + timedelta(days_since_1899)

    @staticmethod
    def get_gspread_date(timestamp: datetime) -> float:
        if type(timestamp).__name__ == "datetime":
            days_since_1899 = (timestamp - TIMESTAMP_START) / timedelta(days=1)
        elif type(timestamp).__name__ == "date":
            days_since_1899 = (timestamp - TIMESTAMP_START.date()) / timedelta(
                days=1
            )
        elif type(timestamp).__name__ == "Timestamp":
            days_since_1899 = (
                timestamp.to_pydatetime() - TIMESTAMP_START
            ) / timedelta(days=1)
        elif type(timestamp).__name__ == "time":
            days_since_1899 = (
                datetime.combine(TIMESTAMP_START, timestamp) - TIMESTAMP_START
            ) / timedelta(days=1)
        else:
            days_since_1899 = (timestamp - TIMESTAMP_START) / timedelta(days=1)
        return days_since_1899

    @staticmethod
    def convert_values(
        value: Union[str, int, float, datetime], goal_type: str = "int"
    ) -> Union[str, int, float, datetime]:
        if goal_type == "int":
            return int(value) if value != "" else np.nan
        if goal_type == "number":
            if type(value).__name__ == "str":
                value = value.replace(",", ".")
            return float(value) if value != "" else np.nan
        if (goal_type == "date") and (
            type(value) == int or type(value) == float or value == ""
        ):
            return google_table.calc_datetime(value)
        if goal_type == "date":
            return to_datetime(value)
        if (goal_type == "time") and (
            type(value) == int or type(value) == float or value == ""
        ):
            res = google_table.calc_datetime(value)
            return res.time()
        if goal_type == "time":
            if type(value).__name__ == "time":
                return value
            else:
                return to_datetime(value).to_pydatetime().time()
        if goal_type == "bool" and (type(value) == int or type(value) == float):
            return bool(value)
        return value

    def download(self, header_line=0) -> DataFrame:
        self.df_from_cloud = DataFrame(
            self.sheet[header_line+1:], columns=self.sheet[header_line])
        for col in self.df_from_cloud.columns:
            if not self.column_dtypes.get(col):
                message = f"?? ???????????????? ???????????? ???????????? ???????? ?????????????? '{col}', ?????? ???????????????? ???? ???????????? ??????"
                log.error(message)
                raise KeyError(message)
            self.df_from_cloud[col] = self.df_from_cloud[col].apply(
                lambda v: google_table.convert_values(
                    v, self.column_dtypes.get(col)
                )
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
            series = dataframe[col]
            mask = series.notna()
            notna = series[mask]
            if len(notna) == 0:
                continue
            sample = notna.sample(1).iloc[0]
            is_datetime = (
                True
                if (
                    ("date" in type(sample).__name__.lower())
                    or ("time" in type(sample).__name__.lower())
                )
                else False
            )
            if not is_datetime:
                continue
            dataframe[col] = dataframe[col].apply(
                lambda dt: google_table.get_gspread_date(dt)
            )
        dataframe.fillna(FILLNA, inplace=True)
        # NOTE ???????????? ?????????? ?????????????????? ???????????????? ?? cloud
        try:
            self.sheet_io.update(
                f"A{startswith}:{ascii_uppercase[dataframe.shape[1]]}{dataframe.shape[0]+startswith if endswith==-1 else endswith}",
                ([dataframe.columns.values.tolist()] if header else [])
                + dataframe.values.tolist(),
                raw=False,
            )
            download_success = True
            log.info(
                f"???????????????? ?????????????? ?? google tables '{self.table}/{self.sheet_name}' ???????????? ??????????????"
            )
        except Exception as e:
            e = str(e).replace("'", '"')
            log.error(
                f"?????? ???????????????? ?????????????? ?? google tables '{self.table}/{self.sheet_name}' ???????????????? ???????????? '{e}'"
            )
            download_success = False
        finally:
            pass
        return download_success


def test() -> None:
    make_logging_config(debug=True)
    column_dtypes = {
        "????????????????????": "number",
        "????????": "date",
        "????????????????????": "string",
        "?????????????????????????? ????????????????": "string",
        "???????????????? ????????????": "string",
        "?????????????????? ????????????": "string",
        "??? ??.??": "string",
    }
    google_table(
        "????????-1Q22", "1Q22", "secret-gspreadsheets.json", column_dtypes
    ).download()
    pass


if __name__ == "__main__":
    test()  # /Users/popov-iv/opt/anaconda3/bin/python3 -m utils.gtables

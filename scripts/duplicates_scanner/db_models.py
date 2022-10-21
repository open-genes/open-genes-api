from functools import reduce

import pandas as pd
from db import dao
from pandas import DataFrame


class DbColumn:
    def __init__(self, table: str, column: str, case_sensetive: bool) -> None:
        self.table = table
        self.column = column
        self.id_column = "id"
        self.case_sensetive = case_sensetive
        self.duplicates = DataFrame()
        self.trailing_spaces = DataFrame()
        self.relations = DataFrame()
        self._connection = dao.BaseDAO().cnx
        self._data_df = self._read_data()

    def _read_data(self) -> DataFrame:
        """Read data from Database from provided table with provided columns"""
        columns = ", ".join([self.id_column, self.column])
        sql = f"SELECT {columns} FROM {self.table}"
        df = pd.read_sql(sql, con=self._connection)
        df = df.dropna()
        return df

    def _read_related_tables(self) -> DataFrame:
        """Read information schema to get all related table names"""
        sql = "select TABLE_NAME from INFORMATION_SCHEMA.COLUMNS where COLUMN_NAME like %(column_name)s order by TABLE_NAME"
        df = pd.read_sql(sql, con=self._connection, params={"column_name": f"{self.table}_id"})
        return df

    def find_duplicates(self) -> None:
        """Find all duplicates from column"""
        data_df = self._data_df.copy()

        if pd.api.types.is_string_dtype(data_df[self.column]):
            data_df[self.column] = data_df[self.column].str.strip()

        if not self.case_sensetive:
            data_df[self.column] = data_df[self.column].str.upper()

        self.duplicates = data_df[data_df.duplicated(subset=[self.column], keep=False)]

    def find_trailing_spaces(self) -> None:
        """Find values in column that have spaces at the beginning and the end"""
        data_df = self._data_df.copy()

        if pd.api.types.is_string_dtype(data_df[self.column]):
            data_df[f"{self.column}_trimmed"] = data_df[self.column].str.strip()
        else:
            raise ValueError("Column must be string type")

        trailing_spaces_df = data_df[data_df[self.column] != data_df[f"{self.column}_trimmed"]]
        self.trailing_spaces = trailing_spaces_df[[self.id_column, self.column]]

    def find_relations(self) -> None:
        """Find relations in other tables"""
        duplicates_ids = tuple(self.duplicates[self.id_column].tolist())
        related_tables_df = self._read_related_tables()
        tables_to_scan = related_tables_df["TABLE_NAME"]
        scan_column = f"{self.table}_id"

        relations_dfs = []
        for table in tables_to_scan:
            columns = ", ".join([self.id_column, scan_column])
            sql = f"SELECT {columns} FROM {table} WHERE {scan_column} IN {duplicates_ids}"
            df = pd.read_sql(sql, con=self._connection)
            df = df.groupby(scan_column).agg(list).reset_index()
            df = df.rename(columns={self.id_column: f'{table}.{self.id_column}'})
            relations_dfs.append(df)

        relations_df = reduce(
            lambda left, right: pd.merge(left, right, on=scan_column, how="outer"), relations_dfs
        )
        relations_df = relations_df.dropna(axis=1, how='all')
        first_column = relations_df.pop(scan_column)
        relations_df.insert(0, scan_column, first_column)
        self.relations = relations_df

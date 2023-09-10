import json
import logging
import os
import sys
import time
from collections import namedtuple
from typing import List
import numpy as np
import pandas as pd
from mysql.connector import MySQLConnection, cursor
from pandas import DataFrame

LOGGER = logging.getLogger("expression_change_human_mrna_upload")
LOGGER.setLevel(logging.INFO)
HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setLevel(logging.INFO)
FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S"
)
HANDLER.setFormatter(FORMAT)
LOG_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output.log')
FILE_HANDLER = logging.FileHandler(LOG_FILEPATH)
FILE_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER.setFormatter(FORMAT)
LOGGER.addHandler(HANDLER)
LOGGER.addHandler(FILE_HANDLER)

ORGANISM_SEX_NULL_VALUE = "not specified"
PREFIX = "_name"
DbTable = namedtuple(
    "DbTable",
    ["name", "columns", "dataset_column", "mapping", "has_created_date"],
    defaults=[False],
)
TABLES_TO_READ = (
    DbTable(
        "gene",
        ("id", "symbol"),
        "gene_symbol",
        {"gene_symbol": "gene_id"},
    ),
    DbTable(
        "age_related_change_type",
        ("id", "name_en"),
        "change_type",
        {"change_type": "age_related_change_type_id"},
        True,
    ),
    DbTable("sample", ("id", "name_en"), "sample", {"sample": "sample_id"}, True),
    DbTable(
        "model_organism", ("id", "name_en"), "organism", {"organism": "model_organism_id"}, True
    ),
    DbTable(
        "time_unit",
        ("id", "name_en"),
        "age_units",
        {"age_units": "age_unit_id"},
    ),
    DbTable(
        "expression_evaluation",
        ("id", "name_en"),
        "change_evaluation_by",
        {"change_evaluation_by": "expression_evaluation_by_id"},
    ),
    DbTable(
        "measurement_method",
        ("id", "name_en"),
        "measurement_method",
        {"measurement_method": "measurement_method_id"},
    ),
    DbTable(
        "statistical_method",
        ("id", "name_en"),
        "statistical_method",
        {"statistical_method": "statistical_method_id"},
    ),
    DbTable(
        "organism_sex",
        ("id", "name_en"),
        "sex",
        {},
    ),
)

def get_df_from_db(connection: MySQLConnection, table: str, columns: List) -> DataFrame:
    """Read data from Database from provided table with provided columns"""
    columns = ", ".join(columns)
    sql = f"SELECT {columns} FROM {table}"
    df = pd.read_sql(sql, con=connection)
    df = df.dropna()
    return df

def get_df_from_csv(file_name: str) -> DataFrame:
    """Read csv file by provided file name"""
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(cur_dir, file_name), quotechar='"', header=0, decimal=",")
    df.columns = df.columns.str.strip()

    for column in df.columns:
        if pd.api.types.is_string_dtype(df[column]):
            df[column] = df[column].str.strip()

    return df

def upload_data(cursor: cursor, df: DataFrame, table_name: str):
    try:
        df = df.replace({np.nan: None})
        df = df.dropna(subset=["gene_id"])
        column_names = ", ".join(df.columns)
        column_vars = ", ".join((f"%({col})s" for col in df.columns))
        data_to_load = df.to_dict("records")
        cursor.executemany(f"INSERT IGNORE INTO {table_name}({column_names}) VALUES ({column_vars})", data_to_load)
    except Exception as e:
        LOGGER.error("Error while uploading data to %s: %s", table_name, str(e))


def delete_existing_records(cursor: cursor, df: DataFrame, table_name: str):
    try:
        for index, row in df.iterrows():
            doi = row["doi"]
            gene_symbol = row["gene_symbol"]
            cursor.execute(f"DELETE FROM {table_name} WHERE doi = %s AND gene_symbol = %s" , (doi, gene_symbol))
    except Exception as e:
        LOGGER.error("Error while deleting existing records from %s: %s", table_name, str(e))


def main():
    LOGGER.info("========== Upload script started ==========")
    dataset_df = get_df_from_csv("08-09-2023-update-items-human-mrna.csv")

    for table in TABLES_TO_READ:
        id_values_df = get_df_from_db(cnx, table.name, table.columns)
        dataset_df = replace_id_values(
            dataset_df,
            id_values_df,
            origin_column=table.dataset_column,
            col_mapping=table.mapping,
        )
        data_to_upload = get_new_data(dataset_df, table)

        if not data_to_upload.empty:
            add_new_data_to_db(cur, data_to_upload, table)
            dataset_df = dataset_df.drop(columns=[table.dataset_column])
            dataset_df = dataset_df.rename(columns={f"{table.dataset_column}{PREFIX}": table.dataset_column})
            id_values_df = get_df_from_db(cnx, table.name, table.columns)
            dataset_df = replace_id_values(
                dataset_df,
                id_values_df,
                origin_column=table.dataset_column,
                col_mapping=table.mapping,
            )

    delete_existing_records(cur, dataset_df, "age_related_change")
    upload_data(cur, dataset_df, "age_related_change")
    cur.close()
    LOGGER.info("========== Upload script finished ==========\n")


if __name__ == "__main__":
    main()

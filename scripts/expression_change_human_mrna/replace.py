import logging
import os
import sys
import time
from collections import namedtuple
from typing import List

import numpy as np
import pandas as pd
from db import dao
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor
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

def upload_data(cursor: MySQLCursor, df: DataFrame, table_name: str):
    try:
        df = df.replace({np.nan: None})
        df = df.dropna(subset=["gene_id"])
        column_names = ", ".join(df.columns)
        column_vars = ", ".join((f"%({col})s" for col in df.columns))
        data_to_load = df.to_dict("records")
        cursor.executemany(f"INSERT IGNORE INTO {table_name}({column_names}) VALUES ({column_vars})", data_to_load)
    except Exception as e:
        LOGGER.error("Error while uploading data to %s: %s", table_name, str(e))

def delete_existing_records(cursor: MySQLCursor, df: DataFrame, table_name: str):
    try:
        for index, row in df.iterrows():
            reference = row["reference"]
            gene_symbol = row["gene_symbol"]

            # Get the corresponding gene_id from the "gene" table
            cursor.execute("SELECT id FROM gene WHERE symbol = %s", (gene_symbol,))
            result = cursor.fetchone()
            if result is not None:
                gene_id = result["id"]

                # Delete the record using gene_id and reference
                cursor.execute(f"DELETE FROM {table_name} WHERE reference = %s AND gene_id = %s", (reference, gene_id))
            else:
                LOGGER.warning("No matching gene_id found for gene_symbol='%s'", gene_symbol)
    except Exception as e:
        LOGGER.error("Error while deleting existing records from %s: %s", table_name, str(e))


def add_new_data_to_db(cursor: MySQLCursor, df: DataFrame, table: namedtuple):
    """Uploads new values in Database

    New values - dataset column values that don't have id association in Database
    """
    LOGGER.info("Upload in table %s started", table.name)
    new_data_df = df[[f"{table.dataset_column}{PREFIX}"]]
    new_data_df = new_data_df.drop_duplicates()
    new_data_df = new_data_df.rename(columns={f"{table.dataset_column}{PREFIX}": "name_en"})

    if table.has_created_date:
        new_data_df["updated_at"] = time.time()

    count_rows = new_data_df.shape[0]
    column_names = ', '.join(new_data_df.columns)
    column_vars = ', '.join(map(lambda x: f'%({x})s', new_data_df.columns))
    LOGGER.info("Number of rows to be uploaded: %s in table: %s", count_rows, table.name)
    sql_query = f"INSERT INTO {table.name} ({column_names}) VALUES ({column_vars})"
    cursor.executemany(sql_query, new_data_df.to_dict("records"))
    row_count = cursor.rowcount if not new_data_df.empty else 0
    LOGGER.info("Number of rows uploaded: %s in table: %s", row_count, table.name)
    LOGGER.info("Upload in table %s finished", table.name)

def get_new_data(df: DataFrame, table: namedtuple) -> DataFrame:
    """Returns data that is present in the dataset but not present in the database"""

    if table.mapping:
        df = df.rename(columns={table.mapping[table.dataset_column]: table.dataset_column})

    new_data_df = df[df[table.dataset_column].isnull()]
    new_data_df = new_data_df[new_data_df[f"{table.dataset_column}{PREFIX}"].notnull()]
    return new_data_df

def replace_id_values(
    df_origin: DataFrame, df_with_ids: DataFrame, origin_column: str, col_mapping: dict
) -> DataFrame:
    """Replace values from the dataset with corresponding id value from the Database"""
    mapping = {}
    id_col, name_col = list(df_with_ids.columns)
    mapping = {
        row[name_col].upper().strip(): row[id_col]
        for _, row in df_with_ids.to_dict("index").items()
    }

    if origin_column == "sex":
        df_origin[origin_column] = df_origin[origin_column].replace("Woman", "female")
        df_origin[origin_column] = df_origin[origin_column].fillna(ORGANISM_SEX_NULL_VALUE)

    df_replaced = df_origin.rename(columns={origin_column: f"{origin_column}{PREFIX}"})
    df_replaced[origin_column] = (
        df_replaced[f"{origin_column}{PREFIX}"].str.upper().str.strip().map(mapping)
    )
    log_values_without_id(df_replaced, origin_column)
    df_replaced = df_replaced.rename(columns=col_mapping)
    return df_replaced

def log_values_without_id(df: DataFrame, id_column: str):
    """Log values from the dataset which don't have id association in the Database"""
    value_column = f"{id_column}{PREFIX}"
    gene_column = "gene_symbol" if "gene_symbol" in df.columns else f"gene_symbol{PREFIX}"
    columns = [value_column, gene_column, "reference"]

    empty_id_df = df[df[id_column].isnull() & df[value_column].notnull()]
    not_matched_df = empty_id_df[columns].drop_duplicates()

    for _, not_matched in not_matched_df.iterrows():
        LOGGER.info(
            "Not found %s='%s' for %s='%s', %s='%s'",
            id_column,
            not_matched[value_column],
            "gene_symbol",
            not_matched[gene_column],
            "reference",
            not_matched["reference"],
        )

def main():
    LOGGER.info("========== Upload script started ==========")
    dataset_df = get_df_from_csv("08-09-2023-update-items-human-mrna.csv")

    with dao.BaseDAO().cnx as cnx:
        cnx.autocommit = True
        cur = cnx.cursor(dictionary=True)
        gene_df = get_df_from_db(cnx, "gene", ["id", "symbol"])
        gene_df = gene_df.dropna(subset=["symbol"])

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

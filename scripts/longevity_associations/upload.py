import json
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

# Create a custom logger
LOGGER = logging.getLogger("longevity_associations_upload")
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

LONGEVITY_ID = 1
INCREASED_LIFESPAN_ID = 8
GENOMIC_DATA_TYPE_ID = 1
ORGANISM_SEX_NULL_VALUE = "not specified"
PREFIX = "_name"

DbTable = namedtuple("DbTable", ["name", "columns", "dataset_column", "mapping"])
TABLES_TO_READ = (
    DbTable(
        "age_related_change_type",
        ("id", "name_en"),
        "age_related_change_type",
        {"age_related_change_type": "age_related_change_type_id"},
    ),
    DbTable(
        "data_types",
        ("id", "name_en"),
        "data_type",
        {},
    ),
    DbTable(
        "ethnicity",
        ("id", "name_en"),
        "ethnicity",
        {"ethnicity": "ethnicity_id"},
    ),
    DbTable(
        "gene",
        ("id", "symbol"),
        "gene_symbol",
        {"gene_symbol": "gene_id"},
    ),
    DbTable(
        "longevity_effect",
        ("id", "name_en"),
        "longevity_effect",
        {"longevity_effect": "longevity_effect_id"},
    ),
    DbTable(
        "polymorphism",
        ("id", "name_en"),
        "polymorphism_id",
        {},
    ),
    DbTable(
        "polymorphism_type",
        ("id", "name_en"),
        "polymorphism_type",
        {"polymorphism_type": "polymorphism_type_id"},
    ),
    DbTable(
        "position",
        ("id", "name_en"),
        "position",
        {"position": "position_id"},
    ),
    DbTable(
        "study_type",
        ("id", "name_en"),
        "study_type",
        {"study_type": "study_type_id"},
    ),
    DbTable(
        "organism_sex",
        ("id", "name_en"),
        "sex_of_organism",
        {},
    ),
)


def delete_experiments(cursor: MySQLCursor, table_name: str):
    """Delete rows from provided table

    Condition: WHERE (longevity_effect_id = %s or longevity_effect_id = %s) and data_type = %s
    """
    LOGGER.info("Deleting from table %s started", table_name)
    sql_query = (
        f"DELETE from {table_name} "
        "WHERE (longevity_effect_id = %s or longevity_effect_id = %s) and data_type = %s"
    )
    params = (LONGEVITY_ID, INCREASED_LIFESPAN_ID, GENOMIC_DATA_TYPE_ID)
    LOGGER.info("Delete query: '%s' with params: '%s'", sql_query, params)
    cursor.execute(sql_query, params)
    LOGGER.info("Number of rows deleted: %s in table: %s", cursor.rowcount, table_name)
    LOGGER.info("Deleting from table %s finished", table_name)


def upload_experiments(cursor: MySQLCursor, df: DataFrame, table_name: str):
    """Uploads data from DataFrame in provided table

    All empty values for gene_id column are dropped before isertion
    """
    LOGGER.info("Upload in table %s started", table_name)
    df = df.replace({np.nan: None})
    df = df.dropna(subset=["gene_id"])
    LOGGER.info("Dropped rows with empty gene_id")
    column_names = ", ".join(df.columns)
    column_vars = ", ".join((f"%({col})s" for col in df.columns))
    data_to_load = df.to_dict("records")
    LOGGER.info("Number of rows to be uploaded: %s in table: %s", len(data_to_load), table_name)
    sql_query = f"INSERT IGNORE INTO {table_name}({column_names}) VALUES ({column_vars})"
    cursor.executemany(sql_query, data_to_load)
    LOGGER.info("Number of rows uploaded: %s in table: %s", cursor.rowcount, table_name)
    LOGGER.info("Upload in table %s finished", table_name)


def add_new_data_to_db(cursor: MySQLCursor, df: DataFrame, table: namedtuple):
    """Uploads new values in Database

    New values - dataset column values that don't have id association in Database
    """
    LOGGER.info("Upload in table %s started", table.name)

    if table.mapping:
        df.rename(columns={table.mapping[table.dataset_column]: table.dataset_column}, inplace=True)

    new_data_df = df[df[table.dataset_column].isnull()]
    new_data_df = new_data_df[new_data_df[f"{table.dataset_column}{PREFIX}"].notnull()]
    new_data_df = new_data_df[[f"{table.dataset_column}{PREFIX}"]]
    new_data_df = new_data_df.drop_duplicates()
    new_data_df = new_data_df.rename(columns={f"{table.dataset_column}{PREFIX}": "name_en"})

    if table.name == "polymorphism":
        new_data_df["name_ru"] = new_data_df["name_en"]
        created_at = time.time()
        new_data_df["created_at"] = created_at
        new_data_df["updated_at"] = new_data_df["created_at"]

    count_rows = new_data_df.shape[0]
    column_names = ', '.join(new_data_df.columns)
    column_vars = ', '.join(map(lambda x: f'%({x})s', new_data_df.columns))
    LOGGER.info("Number of rows to be uploaded: %s in table: %s", count_rows, table.name)
    sql_query = f"INSERT INTO {table.name} ({column_names}) VALUES ({column_vars})"
    cursor.executemany(sql_query, new_data_df.to_dict("records"))
    row_count = cursor.rowcount if not new_data_df.empty else 0
    LOGGER.info("Number of rows uploaded: %s in table: %s", row_count, table.name)
    LOGGER.info("Upload in table %s finished", table.name)


def apply_structure(df: DataFrame, structure: dict) -> DataFrame:
    """Cast all DataFrame values to corresponding data types"""
    columns = map(lambda x: x["columnName"], structure["columns"])
    dtypes = {col["columnName"]: col["columnType"] for col in structure["columns"]}
    df = df[columns]
    try:
        df = df.astype(dtypes)
    except ValueError as err:
        LOGGER.error("Row will be skipped during upload, error message: %s", err)
    return df


def replace_id_values(
    df_origin: DataFrame, df_with_ids: DataFrame, origin_column: str, col_mapping: dict
) -> DataFrame:
    """Replace values from dataset with corresponding id value from Database"""
    mapping = {}
    id_col, name_col = list(df_with_ids.columns)
    mapping = {row[name_col]: row[id_col] for _, row in df_with_ids.to_dict("index").items()}

    if origin_column == "sex_of_organism":
        df_origin[origin_column] = df_origin[origin_column].fillna(ORGANISM_SEX_NULL_VALUE)

    df_replaced = df_origin.rename(columns={origin_column: f"{origin_column}{PREFIX}"})
    df_replaced[origin_column] = df_replaced[f"{origin_column}{PREFIX}"].map(mapping)
    log_values_without_id(df_replaced, origin_column)
    df_replaced = df_replaced.rename(columns=col_mapping)
    return df_replaced


def log_values_without_id(df: DataFrame, id_column: str):
    """Log values from dataset which don't have id association in Database"""
    value_column = f"{id_column}{PREFIX}"
    gene_column = "gene_symbol" if "gene_symbol" in df.columns else f"gene_symbol{PREFIX}"
    columns = [value_column, gene_column, "reference"]

    if id_column in ["polymorphism_id", "ethnicity", "position"]:
        return

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


def get_df_from_db(connection: MySQLConnection, table: str, columns: List) -> DataFrame:
    """Read data from Database from provided table with provided columns"""
    columns = ", ".join(columns)
    sql = f"SELECT {columns} FROM {table}"
    df = pd.read_sql(sql, con=connection)
    return df


def get_df_from_csv(file_name: str) -> DataFrame:
    """Read csv file by provided file name"""
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(cur_dir, file_name), quotechar='"', header=0)
    df.columns = df.columns.str.strip()

    for column in df.columns:
        if pd.api.types.is_string_dtype(df[column]):
            df[column] = df[column].str.strip()

    return df


def read_structure_json(file_name: str) -> dict:
    """Read json file by provided file name"""
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(cur_dir, file_name)) as json_file:
        structure = json.load(json_file)
    return structure


def main():
    LOGGER.info("========== Upload script started ==========")
    longevity_associations_df = get_df_from_csv("longevity-associations.csv")
    structure = read_structure_json("gene_to_longevity_effect_structure.json")

    with dao.BaseDAO().cnx as cnx:
        cnx.autocommit = True
        cur = cnx.cursor(dictionary=True)
        delete_experiments(cur, structure["tableName"])

        for table in TABLES_TO_READ:
            id_values_df = get_df_from_db(cnx, table.name, table.columns)
            longevity_associations_df = replace_id_values(
                longevity_associations_df,
                id_values_df,
                origin_column=table.dataset_column,
                col_mapping=table.mapping,
            )

            if table.name in ["polymorphism", "ethnicity", "position"]:
                add_new_data_to_db(cur, longevity_associations_df, table)
                longevity_associations_df = longevity_associations_df.drop(
                    columns=[table.dataset_column]
                )
                longevity_associations_df = longevity_associations_df.rename(
                    columns={f"{table.dataset_column}{PREFIX}": table.dataset_column}
                )
                id_values_df = get_df_from_db(cnx, table.name, table.columns)
                longevity_associations_df = replace_id_values(
                    longevity_associations_df,
                    id_values_df,
                    origin_column=table.dataset_column,
                    col_mapping=table.mapping,
                )

        longevity_associations_df = apply_structure(longevity_associations_df, structure)
        upload_experiments(cur, longevity_associations_df, structure["tableName"])
        cur.close()

    LOGGER.info("========== Upload script finished ==========\n")


if __name__ == "__main__":
    main()

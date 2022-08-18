import logging
import os
import sys
from dataclasses import dataclass

import pandas as pd
from db import dao
from mysql import connector


@dataclass
class GeneToConfidenceLevel:
    table = "gene_to_confidence_level"
    columns = ("gene_id", "confidence_level_id")


@dataclass
class Gene:
    table = "gene"
    columns = ("symbol", "confidence_level_id")
    default_confidence_level_id = 5  # lowest


@dataclass
class ConfidenceLevel:
    table = "confidence_level"
    columns = ("id", "name_en", "name_ru")
    levels = (
        (1, "highest", "самый высокий"),
        (2, "high", "высокий"),
        (3, "moderate", "умеренный"),
        (4, "low", "низкий"),
        (5, "lowest", "самый низкий"),
    )


# Create a custom logger
LOGGER = logging.getLogger("confidence_level_upload")
LOGGER.setLevel(logging.INFO)
HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setLevel(logging.INFO)
FORMAT = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
HANDLER.setFormatter(FORMAT)
LOGGER.addHandler(HANDLER)


def upload_confidence_level(cursor):
    LOGGER.info("upload in table %s started", ConfidenceLevel.table)
    columns_params = ','.join(ConfidenceLevel.columns)
    sql_query = f"REPLACE INTO {ConfidenceLevel.table} ({columns_params}) VALUES (%s, %s, %s)"

    try:
        cursor.executemany(sql_query, ConfidenceLevel.levels)
    except connector.Error as error:
        if error.errno == connector.errorcode.ER_ROW_IS_REFERENCED_2:
            LOGGER.warning(
                "TABLE %s is not empty. Error message: %s", ConfidenceLevel.table, error.msg
            )
        else:
            raise
    finally:
        LOGGER.info("upload in table %s finished", ConfidenceLevel.table)


def upload_gene(cursor):
    LOGGER.info("upload in table %s started", Gene.table)

    cur_dir = os.path.dirname(os.path.abspath(__file__))
    confidence_level_df = pd.read_table(
        os.path.join(cur_dir, 'confidence_level.tsv'), names=Gene.columns, header=0
    )
    levels_mapping = {i[1]: i[0] for i in ConfidenceLevel.levels}
    confidence_level_df = confidence_level_df.replace({"confidence_level_id": levels_mapping})
    data_to_load = confidence_level_df.to_dict("records")
    sql_query = (
        f"UPDATE {Gene.table} "
        "SET confidence_level_id = %(confidence_level_id)s WHERE symbol = %(symbol)s"
    )
    cursor.executemany(sql_query, data_to_load)

    sql_query = (
        f"UPDATE {Gene.table} "
        "SET confidence_level_id = %(default)s WHERE confidence_level_id is null"
    )
    cursor.execute(sql_query, {"default": Gene.default_confidence_level_id})

    LOGGER.info("upload in table %s finished", Gene.table)


def upload_gene_to_confidence_level(cursor):
    LOGGER.info("upload in table %s started", GeneToConfidenceLevel.table)

    sql = f"SELECT id, confidence_level_id FROM {Gene.table}"
    cursor.execute(sql)

    data_to_load = cursor.fetchall()
    sql = f"TRUNCATE TABLE {GeneToConfidenceLevel.table}"
    cursor.execute(sql)

    columns_params = ','.join(GeneToConfidenceLevel.columns)
    sql_query = (
        f"REPLACE INTO {GeneToConfidenceLevel.table} ({columns_params}) "
        "VALUES (%(id)s, %(confidence_level_id)s)"
    )
    cursor.executemany(sql_query, data_to_load)

    LOGGER.info("upload in table %s finished", GeneToConfidenceLevel.table)


def main():
    LOGGER.info("upload script started")

    with dao.BaseDAO().cnx as cnx:
        cnx.autocommit = True
        cur = cnx.cursor(dictionary=True)
        upload_confidence_level(cur)
        upload_gene(cur)
        upload_gene_to_confidence_level(cur)

    LOGGER.info("upload script finished")


if __name__ == "__main__":
    main()

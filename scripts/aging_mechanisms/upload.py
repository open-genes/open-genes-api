import ast
import logging
import os
import sys

import pandas as pd
import requests

from api.db import dao

# Create a custom logger
LOGGER = logging.getLogger("aging_mechanisms_upload")
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

BASE_URL_QUICK_GO = "https://www.ebi.ac.uk/QuickGO/services/ontology/go"


def insert_into_aging_mechanism(cursor, name_en, name_ru):
    query = (
        "INSERT aging_mechanism (name_en, name_ru) "
        "SELECT %(name_en)s, %(name_ru)s WHERE NOT EXISTS "
        "(SELECT name_en FROM aging_mechanism WHERE aging_mechanism.name_en = %(name_en)s)"
    )
    cursor.execute(query, {"name_en": name_en, "name_ru": name_ru})

    if cursor.rowcount:
        LOGGER.info(
            "Uploaded in table 'aging_mechanism' row: name_en=%s, name_ru=%s", name_en, name_ru
        )


def insert_into_gene_ontology(cursor, results, go_term_name):
    for result in results:
        if result['name'] in go_term_name and not result['isObsolete']:
            query = (
                "INSERT gene_ontology (ontology_identifier, category, name_en) "
                "SELECT %(ontology_identifier)s, %(category)s, %(name_en)s WHERE NOT EXISTS "
                "(SELECT ontology_identifier, category, name_en "
                "FROM gene_ontology "
                "WHERE gene_ontology.ontology_identifier = %(ontology_identifier)s)"
            )
            cursor.execute(
                query,
                {
                    "ontology_identifier": result['id'],
                    "category": result['aspect'],
                    "name_en": result['name'],
                },
            )
            
            if cursor.rowcount:
                LOGGER.info(
                    "Uploaded in table 'gene_ontology' row: "
                    "ontology_identifier=%s, category=%s, name_en=%s",
                    result['id'],
                    result['aspect'],
                    result['name'],
                )



def insert_into_aging_mechanism_to_gene_ontology(cursor, go_id, aging_mechanism_id):
    query = (
        "INSERT aging_mechanism_to_gene_ontology (gene_ontology_id, aging_mechanism_id) "
        "SELECT %(go_id)s, %(aging_mechanism_id)s WHERE NOT EXISTS "
        "(SELECT gene_ontology_id, aging_mechanism_id "
        "FROM aging_mechanism_to_gene_ontology am_to_go "
        "WHERE am_to_go.gene_ontology_id = %(go_id)s "
        "AND am_to_go.aging_mechanism_id = %(aging_mechanism_id)s)"
    )
    cursor.execute(query, {"go_id": go_id, "aging_mechanism_id": aging_mechanism_id})

    if cursor.rowcount:
        LOGGER.info(
            "Uploaded in table 'aging_mechanism_to_gene_ontology' "
            "row: gene_ontology_id=%s, aging_mechanism_id=%s", 
            go_id, 
            aging_mechanism_id
        )


def get_aging_mechanism_id(cursor, name_en):
    query = "SELECT id FROM aging_mechanism WHERE aging_mechanism.name_en = %s"
    cursor.execute(query, [name_en])
    return cursor.fetchone()["id"]


def get_gene_ontology_id(cursor, go_name_en):
    query = "SELECT id FROM gene_ontology WHERE gene_ontology.name_en = %s LIMIT 1"
    cursor.execute(query, [go_name_en])
    return cursor.fetchone()


def parse_quickgo(go_term_name):
    response = requests.get(
        f'{BASE_URL_QUICK_GO}/search',
        headers={"Accept": "application/json"},
        params={"query": go_term_name, "limit": 5, "page": 1},
        timeout=60,
    ).json()
    return response.get("results", [])


def main():
    LOGGER.info("========== Upload script started ==========")
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    go_and_mechanisms = pd.read_table(os.path.join(cur_dir, 'go_and_mechanisms.tsv'))
    go_and_mechanisms.columns = go_and_mechanisms.columns.str.strip()

    for column in go_and_mechanisms.columns:
        if pd.api.types.is_string_dtype(go_and_mechanisms[column]):
            go_and_mechanisms[column] = go_and_mechanisms[column].str.strip()

    for _, row in go_and_mechanisms.iterrows():

        with dao.BaseDAO().cnx as cnx:
            cnx.autocommit = True
            cur = cnx.cursor(dictionary=True)
            insert_into_aging_mechanism(cur, row['name_en'], row['name_ru'])
            aging_mechanism_id = get_aging_mechanism_id(cur, row['name_en'])

            for go_term_name in ast.literal_eval(row['go_terms']):
                gene_ontology_id = get_gene_ontology_id(cur, go_term_name)

                if gene_ontology_id is None:
                    parsed_data = parse_quickgo(go_term_name)
                    insert_into_gene_ontology(cur, parsed_data, go_term_name)
                    gene_ontology_id = get_gene_ontology_id(cur, go_term_name)

                if gene_ontology_id is not None:
                    insert_into_aging_mechanism_to_gene_ontology(
                        cur, gene_ontology_id["id"], aging_mechanism_id
                    )

    LOGGER.info("========== Upload script finished ==========\n")


if __name__ == "__main__":
    main()

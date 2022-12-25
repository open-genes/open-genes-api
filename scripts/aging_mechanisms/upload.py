import os
import ast
import requests
import pandas as pd
from api.db import dao

cur_dir = os.path.dirname(os.path.abspath(__file__))
go_and_mechanisms = pd.read_table(os.path.join(cur_dir, 'go_and_mechanisms.tsv'))

# Every row in tsv dataset is an individual aging mechanism
for _, row in go_and_mechanisms.iterrows():
    cnx = dao.BaseDAO().cnx
    cur = cnx.cursor(dictionary=True)
    # Check if aging mechanism already exists in DB
    check = f"SELECT * FROM aging_mechanism WHERE name_en = \'{row['name_en']}\' OR name_ru = \'{row['name_ru']}\'"
    cur.execute(check)
    result = cur.fetchall()
    aging_mechanism_id = cur.lastrowid
    # Create if not:
    if not result:
        query = f"INSERT INTO aging_mechanism (name_en, name_ru) VALUES (\'{row['name_en']}\', \'{row['name_ru']}\')"
        cur.execute(query)
        aging_mechanism_id = cur.lastrowid
        cnx.commit()
        cnx.close()
        print('Created new aging mechanism: ', row['name_en'], row['name_ru'])
    else:
        aging_mechanism_id = result[0]['id']
        cnx.close

    # For every aging mechanism make a query to API
    # Try changing the limit if there are few results
    for go_term_name in ast.literal_eval(row['go_terms']):
        url = f'https://www.ebi.ac.uk/QuickGO/services/ontology/go/search?query={go_term_name}&limit=100&page=1'
        response = requests.get(url, headers={"Accept": "application/json"}).json()
        for result in response['results']:
            if result['name'] in go_term_name and not result['isObsolete']:
                cnx = dao.BaseDAO().cnx
                cur = cnx.cursor(dictionary=True)
                query = f"""
                SELECT id
                FROM gene_ontology
                WHERE ontology_identifier = \'{result['id']}\'
                """
                cur.execute(query)
                db_result = cur.fetchall()
                if not db_result:
                    query = f"""
                    INSERT INTO gene_ontology (ontology_identifier, category, name_en)
                    VALUES (\'{result['id']}\', \'{result['aspect']}\', \'{result['name']}\')
                    """
                    cur.execute(query)
                    go_id = cur.lastrowid
                    cnx.commit()
                    cnx.close()
                    print('Added GO term: ', result['id'], result['name'])
                else:
                    go_id = db_result[0]['id']
                    cnx.close()
                cnx = dao.BaseDAO().cnx
                cur = cnx.cursor(dictionary=True)
                check_for_exists = f"""
                SELECT *
                FROM aging_mechanism_to_gene_ontology
                WHERE gene_ontology_id = \'{go_id}\' AND aging_mechanism_id = \'{aging_mechanism_id}\'
                """
                cur.execute(check_for_exists)
                result = cur.fetchall()
                if not result:
                    query = f"""
                    INSERT INTO aging_mechanism_to_gene_ontology (gene_ontology_id, aging_mechanism_id)
                    VALUES (\'{go_id}\', \'{row['name_en']}\')
                    """
                    cur.execute(query)
                    cnx.commit()
                    cnx.close()
                    print(f"Bound: {go_id} to {row['name_en']}")
            else:
                print(f"Didn't find any GO term to bind to {aging_mechanism_id}")
print('DONE')
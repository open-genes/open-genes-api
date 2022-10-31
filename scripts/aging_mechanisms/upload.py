import ast
import os

import pandas as pd
import requests

from api.db import dao

cur_dir = os.path.dirname(os.path.abspath(__file__))
go_and_mechanisms = pd.read_table(os.path.join(cur_dir, 'go_and_mechanisms.tsv'))

for _, row in go_and_mechanisms.iterrows():
    cnx = dao.BaseDAO().cnx
    cur = cnx.cursor(dictionary=True)
    query = f"""
    INSERT aging_mechanism (name_en, name_ru)
    SELECT \'{row['name_en']}\', \'{row['name_ru']}\'
    WHERE NOT EXISTS
    (   SELECT name_en, name_ru
        FROM aging_mechanism
        WHERE aging_mechanism.name_en = \'{row['name_en']}\'
        AND aging_mechanism.name_ru = \'{row['name_ru']}\'
    )
    """
    cur.execute(query)
    aging_mechanism_id = cur.lastrowid
    cnx.commit()
    cnx.close()
    if cur.rowcount:
        print('ADD AGING MECHANISM: ', row['name_en'], row['name_ru'])
        for go_term_name in ast.literal_eval(row['go_terms']):
            url = f'https://www.ebi.ac.uk/QuickGO/services/ontology/go/search?query={go_term_name}&limit=5&page=1'
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
                        print('ADD GO: ', result['id'], result['name'])
                    else:
                        go_id = db_result[0]['id']
                        cnx.close()
                    cnx = dao.BaseDAO().cnx
                    cur = cnx.cursor(dictionary=True)
                    query = f"""
                    INSERT INTO aging_mechanism_to_gene_ontology (gene_ontology_id, aging_mechanism_id)
                    VALUES (\'{go_id}\', \'{aging_mechanism_id}\')
                    """
                    cur.execute(query)
                    cnx.commit()
                    cnx.close()
                    print(f"BIND: {result['name']}, {row['name_en']}")
print('DONE')

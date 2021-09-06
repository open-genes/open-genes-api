import os
import sys
import time
import logging

import requests
import pandas as pd
from deep_translator import GoogleTranslator

from opengenes.db import dao


TRANSLATOR = GoogleTranslator(source='en', target='ru')

cur_dir = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=logging.WARNING,
    handlers=[
        logging.StreamHandler(sys.stdout.flush()),
        logging.FileHandler(
            os.path.join(cur_dir, 'uniprot_fetcher.log')
        )
    ],
)


proteins_info = []
counter = 0
for gene_object in dao.GeneDAO().get_list():
    response_raw = requests.get(
        'https://www.ebi.ac.uk/proteins/api/proteins',
        params={
            'exact_gene': gene_object['symbol'],
            'organism': 'human',
            'isoform': 0,
            'reviewed': True,
        },
        headers={'Accept': 'application/json'}
        )
    
    if response_raw.status_code != 200:
        logging.warning('-'*100)
        logging.warning(f"GENE SYMBOL: {gene_object['symbol']}")
        logging.warning(f"RESPONSE: {response_raw.json()}")
        continue

    response_json = response_raw.json()
    if len(response_json) < 1:
        continue
    
    reference_protein = response_json[0]

    protein = {
        'gene_ncbi_id': gene_object['ncbi_id'],
        'gene_symbol': gene_object['symbol'],
        'uniprot_summary_en': [],
        'uniprot_summary_ru': [],
    }

    for comment in reference_protein['comments']:
        if comment['type'] == 'FUNCTION':
            for text in comment['text']:
                text_value = text['value']
                protein['uniprot_summary_en'].append(text_value)
                if len(text_value) < 5000:
                    translated = TRANSLATOR.translate(text_value)
                else:
                    translated = ''
                    for sentence in text_value.split('.'):
                        translated += ' ' + TRANSLATOR.translate(sentence)
                    translated = translated[1:]  # For the first sentence space.
                protein['uniprot_summary_ru'].append(translated)
    proteins_info.append(protein)
    counter += 1
    print(f'COUNT: {counter} ', f" GENE: {gene_object['symbol']}")
pd.DataFrame(proteins_info).to_csv('test.tsv', sep='\t', index=False)
print(f'DONE. TOTAL COUNT: {counter}')
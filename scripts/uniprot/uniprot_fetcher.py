import os
import sys
import logging

import requests
from deep_translator import GoogleTranslator

from opengenes.entities import entities
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


counter = 0
for gene_object in dao.GeneDAO().get_list(request="SELECT ncbi_id, symbol, uniprot, uniprot_summary_ru FROM `gene`"):
    if gene_object['uniprot'] and gene_object['uniprot_summary_ru']:
        continue
        
    try:
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
            logging.warning('-' * 100)
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
            'uniprot_summary_en': '',
            'uniprot_summary_ru': '',
        }
    
        for comment in reference_protein['comments']:
            if comment['type'] == 'FUNCTION':
                for text in comment['text']:
                    text_value = text['value']
                    protein['uniprot_summary_en'] += text_value + '. '
                    if len(text_value) < 5000:
                        translated = TRANSLATOR.translate(text_value)
                    else:
                        translated = ''
                        for sentence in text_value.split('.'):
                            translated += ' ' + TRANSLATOR.translate(sentence)
                        translated = translated[1:]  # For the first sentence space.
                    protein['uniprot_summary_ru'] += translated + ' '
        dao.GeneDAO().update(
            gene=entities.Gene(
                ncbi_id=gene_object['ncbi_id'],
                uniprot_summary_en=protein['uniprot_summary_en'],
                uniprot_summary_ru=protein['uniprot_summary_ru'],
                uniprot=reference_protein['id'],
            )
        )
        counter += 1
        print(f'COUNT: {counter} ', f" GENE: {gene_object['symbol']}")
    except Exception as e:
        print (f'COUNT: {counter} ', f" GENE: {gene_object['symbol']} ERROR: {type(e)} {str(e)}")
print(f'DONE. TOTAL COUNT: {counter}')

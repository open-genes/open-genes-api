from opengenes.db import dao
import os
import csv
import requests
from opengenes.entities.entities import Gene
import time

def parser():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    calory_restrictions = open(os.path.join(cur_dir, 'Calory_restriction_datasets-2.csv'))
    reader = csv.DictReader(calory_restrictions)
    for row in reader:
        if not dao.GeneDAO().get_by_symbol(gene=row['Gene']):
            gene = requests.get('https://mygene.info/v3/query'
                                '?fields=symbol%2Cname%2Centrezgene%2Calias%2Csummary'
                                '&species=human&q={}'.format(row['Gene']))
            if len(gene.json()['hits']) > 0:
                gene_answer = gene.json()['hits'][0]
                gene = Gene(
                    isHidden=1,
                    ncbi_summary_en=gene_answer['summary'],
                    symbol=gene_answer['symbol'],
                    aliases=','.join(gene_answer['alias']),
                    name=gene_answer['name'],
                    ncbi_id=gene_answer['entrezgene'],
                    created_at=time.time(),
                    updated_at=time.time(),
                )
                dao.GeneDAO().add(gene=gene)

parser()
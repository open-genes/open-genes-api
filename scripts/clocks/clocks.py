import os

import pandas as pd

from opengenes.entities import entities
from opengenes.db import dao


def checker():
    """Check and update DB genes using Horvath clocks genes info."""
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    clocks = pd.read_csv(os.path.join(cur_dir, 'clocks.csv'))
    updated_counter = 0
    added_counter = 0
    for _, row in clocks.iterrows():
        gene_id = row['Gene_ID']
        methylation_horvath = 1 if row['Marginal Age Relationship'] == 'positive' else 0
        if dao.GeneDAO().get(gene_id) is not None:
            dao.GeneDAO().update(
                gene=entities.Gene(
                    ncbi_id=gene_id,
                    methylation_horvath=methylation_horvath,
                )
            )
            updated_counter += 1
            print(f'UPDATED: ncbi_id={gene_id}')
        else:
            dao.GeneDAO().add(gene=entities.Gene(
                isHidden=1,
                symbol=row['Symbol'],
                ncbi_id=gene_id,
                methylation_horvath=methylation_horvath,
                source='horvath',
            ))
            added_counter += 1
            print(f'ADDED: ncbi_id={gene_id}')
    print(f'UPDATED: {updated_counter}')
    print(f'ADDED: {added_counter}')
    print(f'TOTAL: {updated_counter + added_counter}')


checker()

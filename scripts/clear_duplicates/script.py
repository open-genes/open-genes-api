from db import dao


def clean_duplicates():
    database = dao.GeneDAO()
    duplicates = database.get_duplicates_genes()
    tables = [
        'age_related_change',
        'calorie_restriction_experiment',
        'gene_expression_in_sample',
        'gene_intervention_to_vital_process',
        'gene_to_additional_evidence',
        'gene_to_comment_cause',
        'gene_to_disease',
        'gene_to_functional_cluster',
        'gene_to_longevity_effect',
        'gene_to_ontology',
        'gene_to_ortholog',
        'gene_to_progeria',
        'gene_to_protein_class',
        'gene_to_source',
        'lifespan_experiment',
        'protein_to_gene',
    ]
    database.change_table(
        tables=tables,
        duplicates=duplicates,
    )
    genes_to_delete = []
    for item in duplicates:
        genes_to_delete.extend(item['GENES'].split(',')[1::])
    database.delete_duplicates(genes_to_delete)


clean_duplicates()

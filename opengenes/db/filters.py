FILTERS = {
    'diseases': ' `disease`.`id` IN ({}) ',
    'disease_categories': ' `disease`.`parent_icd_code` IN ({}) ',
    'functional_clusters': ' `functional_cluster`.`id` IN ({}) ',
    'expression_change': ' `gene`.`expressionChange` IN ({}) ',
}

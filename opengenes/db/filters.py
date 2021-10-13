FILTERS = {
    'diseases': ' `disease`.`id` IN ({}) ',
    'disease_categories': ' `parent_icd_code`.`id` IN ({}) ',
    'functional_clusters': ' `functionalClusters`.`id` IN ({}) ',
    'expression_change': ' `gene`.`expressionChange` IN ({}) ',
}

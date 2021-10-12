FILTERS = {
    'diseases': 'AND `disease`.`id` IN ({})',
    'disease_categories': 'AND `parent_icd_code`.`id` IN ({})',
    'functional_clusters': 'AND `functionalClusters`.`id` IN ({})'
}

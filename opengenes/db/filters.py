FILTERS = {
    'expression_change': ' `gene`.`expressionChange` IN ({}) ',
}

FILTERS_JOIN = {
    'functional_clusters': ' (SELECT `gene_to_functional_cluster`.`gene_id` FROM `gene_to_functional_cluster` '
            'WHERE `functional_cluster_id` IN ({}) GROUP BY `gene_id` HAVING count(`functional_cluster_id`) = {}) '
            '`age_related_processes` on `age_related_processes`.`gene_id`=`gene`.`id`',

    'diseases': ' (SELECT `gene_to_disease`.`gene_id` FROM `gene_to_disease` '
            'WHERE `disease_id` IN ({}) GROUP BY `gene_id` HAVING count(`disease_id`) = {}) '
            '`gene_diseases` on `gene_diseases`.`gene_id`=`gene`.`id`',

    'disease_categories': ' (SELECT `gene_to_disease`.`gene_id` FROM `gene_to_disease` '
            'LEFT JOIN `disease` on `gene_to_disease`.`disease_id`=`disease`.`id` '
            'LEFT JOIN `disease` disease_category on `disease`.`icd_code_visible`=`disease_category`.`icd_code` '
            'WHERE `disease_category`.`id` IN ({}) GROUP BY `gene_id` HAVING count(`disease_category`.`id`) = {})'
            ' `gene_disease_categories` on `gene_disease_categories`.`gene_id`=`gene`.`id`',
}
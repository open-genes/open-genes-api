FILTERS = {
    'expression_change': ' `gene`.`expressionChange` IN ({}) ',
}

FILTERS_JOIN = {
    'functional_clusters': ' (SELECT `gene_to_functional_cluster`.`gene_id` FROM `gene_to_functional_cluster` '
            'WHERE `functional_cluster_id` IN ({}) GROUP BY `gene_id` HAVING count(`functional_cluster_id`) = {}) '
            '`age_related_processes` on `age_related_processes`.`gene_id`=`gene`.`id`',

    'comment_cause': ' (SELECT `gene_to_comment_cause`.`gene_id` FROM `gene_to_comment_cause` '
            'WHERE `comment_cause_id` IN ({}) GROUP BY `gene_id` HAVING count(`comment_cause_id`) = {}) '
            '`selection_criteria` on `selection_criteria`.`gene_id`=`gene`.`id`',

    'diseases': ' (SELECT `gene_to_disease`.`gene_id` FROM `gene_to_disease` '
            'WHERE `disease_id` IN ({}) GROUP BY `gene_id` HAVING count(`disease_id`) = {}) '
            '`gene_diseases` on `gene_diseases`.`gene_id`=`gene`.`id`',

    'disease_categories': ' (SELECT `gene_to_disease`.`gene_id` FROM `gene_to_disease` '
            'LEFT JOIN `disease` on `gene_to_disease`.`disease_id`=`disease`.`id` '
            'LEFT JOIN `disease` disease_category on `disease`.`icd_code_visible`=`disease_category`.`icd_code` '
            'WHERE `disease_category`.`id` IN ({}) GROUP BY `gene_id` HAVING count(`disease_category`.`id`) = {})'
            ' `gene_disease_categories` on `gene_disease_categories`.`gene_id`=`gene`.`id`',

    'aging_mechanisms': ' (SELECT `gene_to_ontology`.`gene_id` FROM `gene_to_ontology` '
            'LEFT JOIN `gene_ontology_to_aging_mechanism_visible` on '
                '`gene_ontology_to_aging_mechanism_visible`.`gene_ontology_id`=`gene_to_ontology`.`gene_ontology_id` '
            'LEFT JOIN `aging_mechanism` on '
                '`gene_ontology_to_aging_mechanism_visible`.`aging_mechanism_id`=`aging_mechanism`.`id` '
            'WHERE `aging_mechanism`.`id` IN ({}) GROUP BY `gene_id` HAVING count(`aging_mechanism`.`id`) = {})'
            ' `filter_aging_mechanisms` on `filter_aging_mechanisms`.`gene_id`=`gene`.`id`',
}

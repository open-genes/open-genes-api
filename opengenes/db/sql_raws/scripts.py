GENES_QUERY = '''
SELECT JSON_OBJECT(
'options',JSON_OBJECT('pagination',JSON_OBJECT('page',@PAGE@,'pageSize',@PAGESIZE@,'pagesTotal',CEILING(MAX(jsout.fRows)/@PAGESIZE@)),'objTotal',MAX(jsout.fRows))
,'items',JSON_ARRAYAGG(jsout.jsonobj)) respJS FROM (
SELECT preout.jsonobj, fRows FROM (
SELECT count(*) OVER() fRows,
JSON_OBJECT(
'id',gene.id,
'homologueTaxon',IFNULL(taxon.name_en,''),
'symbol',IFNULL(gene.symbol,''),
'name',IFNULL(gene.name,''),
'ncbiId',gene.ncbi_id,
'uniprot',IFNULL(gene.uniprot,''),
'expressionChange',gene.expressionChange,
'timestamp',gene.updated_at,
'ensembl',gene.ensembl,
'methylationCorrelation',IFNULL(gene.methylation_horvath,''),
'aliases',CAST(CONCAT_WS('"','[',REPLACE(gene.aliases,' ','","'),']') AS JSON),
'origin',JSON_OBJECT(
 'id',phylum.id,
 'phylum',IFNULL(phylum.name_phylo,''),
 'age',IFNULL(phylum.name_mya,''),
 'order',phylum.order
 ),
'familyOrigin',JSON_OBJECT(
 'id',family_phylum.id,
 'phylum',IFNULL(family_phylum.name_phylo,''),
 'age',IFNULL(family_phylum.name_mya,''),
 'order',family_phylum.order
 ),
'commentCause',JSON_REMOVE(JSON_OBJECTAGG(IFNULL(comment_cause.id,'null'),comment_cause.name_en), '$.null'),
'functionalClusters',CAST(CONCAT('[',GROUP_CONCAT(distinct JSON_OBJECT('id',IFNULL(functional_cluster.id,0),'name',IFNULL(functional_cluster.name_en,'')) separator ","),']') AS JSON), ## этот вариант требует больше памяти, но обеспечивает совместимость со старым фронтом
##'functionalClusters',JSON_REMOVE(JSON_ARRAYAGG(JSON_OBJECT('id',IFNULL(functional_cluster.id,'null'),'name',IFNULL(functional_cluster.name_en,''))), '$.null'), ## этот вариант требует больше памяти, но обеспечивает совместимость со старым фронтом
##'functionalClusters',JSON_OBJECTAGG('id',IFNULL(functional_cluster.id,''),'name',IFNULL(functional_cluster.name_en,'')), ## этот вариант требует больше памяти, но обеспечивает совместимость со старым фронтом
'diseases',JSON_REMOVE(JSON_OBJECTAGG(IFNULL(disease.id,'null'),JSON_OBJECT('icdCode',IFNULL(disease.icd_code ,''),'name',IFNULL(disease.name_en,''),'icdName',IFNULL(disease.icd_name_en,''))), '$.null'),
'diseaseCategories',JSON_REMOVE(JSON_OBJECTAGG(IFNULL(disease_category.id,'null'),JSON_OBJECT('icdCode',IFNULL(disease_category.icd_code,''),'icdCategoryName',IFNULL(disease_category.icd_name_en,''))), '$.null')
) as jsonobj
FROM gene
LEFT JOIN phylum family_phylum ON gene.family_phylum_id = family_phylum.id
LEFT JOIN phylum ON gene.phylum_id = phylum.id
LEFT JOIN taxon ON gene.taxon_id = taxon.id
LEFT JOIN gene_to_functional_cluster ON gene_to_functional_cluster.gene_id = gene.id
LEFT JOIN functional_cluster ON gene_to_functional_cluster.functional_cluster_id = functional_cluster.id
LEFT JOIN gene_to_comment_cause ON gene_to_comment_cause.gene_id = gene.id
LEFT JOIN comment_cause ON gene_to_comment_cause.comment_cause_id = comment_cause.id
LEFT JOIN gene_to_disease ON gene_to_disease.gene_id = gene.id
LEFT JOIN disease ON gene_to_disease.disease_id = disease.id
LEFT JOIN disease disease_category ON disease.icd_code_visible = disease_category.icd_code
WHERE gene.isHidden != 1 @FILTERS@
GROUP BY gene.id
ORDER BY family_phylum.order DESC
) preout
@LIMIT@
) jsout;
'''

CALORIE_EXPERIMENT_QUERY = '''
SELECT JSON_OBJECT(
    'id', cre.id,
    'gene', g.symbol,
    'p_val', cre.p_val,
    'result', cre.result,
    'measurement_method', mm.name_en,
    'measurement_type', mt.name_en,
    'restriction_percent', cre.restriction_percent,
    'restriction_time', cre.restriction_time,
    'restriction_time_unit', ttu.name_en,
    'age', cre.age,
    'age_time_unit', ttu2.name_en,
    'model_organims', mo.name_en,
    'strain', ol.name_en,
    'organism_sex', os.name_en,
    'tissue', s.name_en,
    'experiment_number', cre.experiment_number,
    'expression_change_log_fc', cre.expression_change_log_fc,
    'expression_change_percent', cre.expression_change_percent,
    'doi', cre.doi,
    'isoform', i.name_en
)
FROM
    calorie_restriction_experiment AS cre
    JOIN gene g on g.id = cre.gene_id
    JOIN measurement_method mm on cre.measurement_method_id = mm.id
    JOIN measurement_type mt on mt.id = cre.measurement_type_id
    JOIN treatment_time_unit ttu on cre.restriction_time_unit_id = ttu.id
    JOIN treatment_time_unit ttu2 on cre.age_time_unit_id = ttu2.id
    JOIN model_organism mo on cre.model_organism_id = mo.id
    JOIN organism_line ol on cre.strain_id = ol.id
    JOIN organism_sex os on cre.organism_sex_id = os.id
    JOIN sample s on cre.tissue_id = s.id
    LEFT JOIN isoform i on cre.isoform_id = i.id
'''

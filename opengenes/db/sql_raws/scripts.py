GENES_QUERY = '''
SELECT JSON_ARRAYAGG(jsout.jsonobj) AS output FROM (
SELECT
JSON_OBJECT(
'id',`gene`.`id`,
'homologueTaxon',IFNULL(`taxon`.`name_en`,''),
'symbol',IFNULL(`gene`.`symbol`,''),
'name',IFNULL(`gene`.`name`,''),
'ncbiId',`gene`.`ncbi_id`,
'uniprot',IFNULL(`gene`.`uniprot`,''),
'expressionChange',`gene`.`expressionChange`,
'timestamp',`gene`.`updated_at`,
'ensembl',`gene`.`ensembl`,
'methylationCorrelation',IFNULL(`gene`.`methylation_horvath`,''),
'aliases',CAST(CONCAT_WS('"','[',REPLACE(`gene`.`aliases`,' ','","'),']') AS JSON),
'origin',JSON_OBJECT(
	'id',`phylum`.`id`,
	'phylum',IFNULL(`phylum`.`name_phylo`,''),
	'age',IFNULL(`phylum`.`name_mya`,''),
	'order',`phylum`.`order`
	),
'familyOrigin',JSON_OBJECT(
	'id',`family_phylum`.`id`,
	'phylum',IFNULL(`family_phylum`.`name_phylo`,''),
	'age',IFNULL(`family_phylum`.`name_mya`,''),
	'order',`family_phylum`.`order`
	),
'commentCause',JSON_REMOVE(JSON_OBJECTAGG(IFNULL(comment_cause.id,'null__'),comment_cause.name_en), '$.null__'),
'functionalClusters',CAST(CONCAT('[',GROUP_CONCAT(distinct JSON_OBJECT('id',IFNULL(functional_cluster.id,0),'name',IFNULL(functional_cluster.name_en,'')) separator ","),']') AS JSON), ## этот вариант требует больше памяти, но обеспечивает совместимость со старым фронтом
##'functionalClusters',JSON_REMOVE(JSON_ARRAYAGG(JSON_OBJECT('id',IFNULL(functional_cluster.id,'null__'),'name',IFNULL(functional_cluster.name_en,''))), '$.null__'), ## этот вариант требует больше памяти, но обеспечивает совместимость со старым фронтом
##'functionalClusters',JSON_OBJECTAGG('id',IFNULL(functional_cluster.id,''),'name',IFNULL(functional_cluster.name_en,'')), ## этот вариант требует больше памяти, но обеспечивает совместимость со старым фронтом
'diseases',JSON_REMOVE(JSON_OBJECTAGG(IFNULL(disease.id,'null__'),JSON_OBJECT('icdCode',IFNULL(disease.icd_code ,''),'name',IFNULL(disease.name_en,''),'icdName',IFNULL(disease.icd_name_en,''))), '$.null__'),
'diseaseCategories',JSON_REMOVE(JSON_OBJECTAGG(IFNULL(disease_category.id,'null__'),JSON_OBJECT('icdCode',IFNULL(disease_category.icd_code,''),'icdCategoryName',IFNULL(disease_category.icd_name_en,''))), '$.null__')
) as jsonobj
FROM `gene`
LEFT JOIN `phylum` `family_phylum` ON gene.family_phylum_id = family_phylum.id
LEFT JOIN `phylum` ON gene.phylum_id = phylum.id
LEFT JOIN `taxon` ON gene.taxon_id = taxon.id
LEFT JOIN `gene_to_functional_cluster` ON gene_to_functional_cluster.gene_id = gene.id
LEFT JOIN `functional_cluster` ON gene_to_functional_cluster.functional_cluster_id = functional_cluster.id
LEFT JOIN `gene_to_comment_cause` ON gene_to_comment_cause.gene_id = gene.id
LEFT JOIN `comment_cause` ON gene_to_comment_cause.comment_cause_id = comment_cause.id
LEFT JOIN `gene_to_disease` ON gene_to_disease.gene_id = gene.id
LEFT JOIN `disease` ON gene_to_disease.disease_id = disease.id
LEFT JOIN `disease` `disease_category` ON disease.icd_code_visible = disease_category.icd_code
WHERE `gene`.`isHidden` != 1  ##and  `gene`.`id`  IN (1642)
GROUP BY `gene`.`id`
ORDER BY `family_phylum`.`order` DESC
) jsout
'''
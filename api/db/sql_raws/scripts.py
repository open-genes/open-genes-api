GENES_QUERY = '''
SELECT JSON_OBJECT(
'options',JSON_OBJECT('pagination',JSON_OBJECT('page',@PAGE@,'pageSize',@PAGESIZE@,'pagesTotal',CEILING(MAX(jsout.fRows)/@PAGESIZE@)),'objTotal',MAX(jsout.fRows))
,'items',JSON_ARRAYAGG(jsout.jsonobj)) respJS FROM (
SELECT preout.jsonobj, fRows FROM (
SELECT count(*) OVER() fRows,
JSON_OBJECT(
'id',gene.id,
'homologueTaxon',COALESCE(NULLIF(taxon.name_@LANG@, ''), NULLIF(taxon.name_en, ''), ''),
'symbol',IFNULL(gene.symbol,''),
'name',IFNULL(gene.name,''),
'ncbiId',gene.ncbi_id,
'uniprot',IFNULL(gene.uniprot,''),
'expressionChange',gene.expressionChange,
'timestamp',JSON_OBJECT(
 'created',IFNULL(gene.created_at,''),
 'changed',IFNULL(gene.updated_at,'')
 ),
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
'commentCause',JSON_REMOVE(JSON_OBJECTAGG(IFNULL(comment_cause.id,'null'),COALESCE(NULLIF(comment_cause.name_@LANG@, ''), NULLIF(comment_cause.name_en, ''), '')), '$.null'),
'functionalClusters',CAST(CONCAT('[',GROUP_CONCAT(distinct JSON_OBJECT('id',IFNULL(functional_cluster.id,0),'name',COALESCE(NULLIF(functional_cluster.name_@LANG@, ''), NULLIF(functional_cluster.name_en, ''), '')) separator ","),']') AS JSON), ## этот вариант требует больше памяти, но обеспечивает совместимость со старым фронтом
##'functionalClusters',JSON_REMOVE(JSON_ARRAYAGG(JSON_OBJECT('id',IFNULL(functional_cluster.id,'null'),'name',IFNULL(functional_cluster.name_en,''))), '$.null'), ## этот вариант требует больше памяти, но обеспечивает совместимость со старым фронтом
##'functionalClusters',JSON_OBJECTAGG('id',IFNULL(functional_cluster.id,''),'name',IFNULL(functional_cluster.name_en,'')), ## этот вариант требует больше памяти, но обеспечивает совместимость со старым фронтом
'diseases',JSON_REMOVE(JSON_OBJECTAGG(IFNULL(disease.id,'null'),JSON_OBJECT('icdCode',IFNULL(disease.icd_code ,''),'name',COALESCE(NULLIF(disease.name_@LANG@, ''), NULLIF(disease.name_en, ''), ''),'icdName',COALESCE(NULLIF(disease.icd_name_@LANG@, ''), NULLIF(disease.icd_name_en, ''), ''))), '$.null'),
'diseaseCategories',JSON_REMOVE(JSON_OBJECTAGG(IFNULL(disease_category.id,'null'),JSON_OBJECT('icdCode',IFNULL(disease_category.icd_code,''),'icdCategoryName',COALESCE(NULLIF(disease_category.icd_name_@LANG@, ''), NULLIF(disease.icd_name_en, ''), ''))), '$.null'),
'agingMechanisms',aging_mechanisms) as jsonobj
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
LEFT JOIN disease disease_category ON disease.icd_code_visible = disease_category.icd_code AND disease_category.icd_name_en != ""
LEFT JOIN (SELECT gene.id,
                CAST(CONCAT('[',GROUP_CONCAT(distinct JSON_OBJECT('id',IFNULL(aging_mechanism.id,0),'name',COALESCE(NULLIF(aging_mechanism.name_@LANG@, ''), NULLIF(aging_mechanism.name_en, ''), '1')) separator ","),']') AS JSON) as aging_mechanisms
                FROM gene
                LEFT JOIN `gene_to_ontology` ON gene_to_ontology.gene_id = gene.id
                LEFT JOIN `gene_ontology_to_aging_mechanism_visible`
                        ON gene_to_ontology.gene_ontology_id = gene_ontology_to_aging_mechanism_visible.gene_ontology_id
                INNER JOIN `aging_mechanism` 
                ON gene_ontology_to_aging_mechanism_visible.aging_mechanism_id = aging_mechanism.id AND aging_mechanism.name_en != ""
                group by gene.id) joined_aging_mechanisms ON gene.id=joined_aging_mechanisms.id
@FILTERS_JOIN@
WHERE gene.isHidden != 1 @FILTERS@
GROUP BY gene.id
ORDER BY family_phylum.order DESC
) preout
@LIMIT@
) jsout;
'''
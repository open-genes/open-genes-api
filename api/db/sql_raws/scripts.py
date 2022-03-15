CALORIE_EXPERIMENT_QUERY = '''
SELECT JSON_OBJECT(
'options',JSON_OBJECT('pagination',JSON_OBJECT('page',@PAGE@,'pageSize',@PAGESIZE@,'pagesTotal',CEILING(MAX(jsout.fRows)/@PAGESIZE@)),'objTotal',MAX(jsout.fRows))
,'items',JSON_ARRAYAGG(jsout.jsonobj)) respJS FROM (
SELECT preout.jsonobj, fRows FROM (
SELECT count(*) OVER() fRows,
JSON_OBJECT(
'id',gene.id,
'symbol',IFNULL(gene.symbol,''),
'name',IFNULL(gene.name,''),
'ncbiId',gene.ncbi_id,
'uniprot',IFNULL(gene.uniprot,''),
'ensembl',gene.ensembl,
'calorieRestrictionExperiments', CAST(CONCAT('[',GROUP_CONCAT(distinct JSON_OBJECT(
    'id', cre.id,
    'lexpressionChangeLogFc', cre.expression_change_log_fc,
    'pValue', cre.p_val,
    'crResult', cre.result,
    'measurementMethod', mm.name_@LANG@,
    'measurementType', mt.name_@LANG@,
    'restrictionPercent', cre.restriction_percent,
    'duration', cre.restriction_time,
    'durationUnit', tu2.name_@LANG@,
    'age', cre.age,
    'ageUnit', tu.name_@LANG@,
    'organism', mo.name_@LANG@,
    'line', ol.name_@LANG@,
    'sex', os.name_@LANG@,
    'tissue', s.name_@LANG@,
    'experimentGroupsQuantity', cre.experiment_number,
    'doi', cre.doi,
    'expressionChangePercent', CAST(cre.expression_change_percent AS FLOAT ),
    'isoform', i.name_@LANG@
    ) separator ","),']') AS JSON)) as jsonobj
FROM gene
    JOIN calorie_restriction_experiment cre on gene.id = cre.gene_id
    JOIN time_unit tu on cre.age_time_unit_id = tu.id
    JOIN time_unit tu2 on cre.restriction_time_unit_id = tu2.id
    JOIN measurement_method mm on cre.measurement_method_id = mm.id
    JOIN measurement_type mt on cre.measurement_type_id = mt.id
    JOIN organism_line ol on cre.strain_id = ol.id
    JOIN organism_sex os on cre.organism_sex_id = os.id
    JOIN model_organism mo on cre.model_organism_id = mo.id
    JOIN sample s on cre.tissue_id = s.id
    LEFT JOIN isoform i on cre.isoform_id = i.id
    GROUP BY gene.id
) preout
@LIMIT@
) jsout;
'''

GENE_QUERY = '''
select JSON_OBJECT(
               'id', gene.id,
               'origin', (select JSON_OBJECT(
                                         'id', p.id,
                                         'phylum', IFNULL(p.name_phylo, ''),
                                         'age', IFNULL(p.name_mya, ''),
                                         'order', p.order
                                     )
                          from phylum p
                          where p.id = gene.phylum_id),
               'familyOrigin', (select JSON_OBJECT(
                                               'id', fp.id,
                                               'phylum', IFNULL(fp.name_phylo, ''),
                                               'age', IFNULL(fp.name_mya, ''),
                                               'order', fp.order
                                           )
                                from phylum fp
                                where fp.id = gene.family_phylum_id),
               'homologueTaxon', (select COALESCE(NULLIF(t.name_en, ''), NULLIF(t.name_en, ''), '') from taxon t where t.id = gene.taxon_id),
               'symbol', IFNULL(gene.symbol, ''),
               'name', IFNULL(gene.name, ''),
               'aliases', CAST(CONCAT_WS('"', '[', REPLACE(gene.aliases, ' ', '","'), ']') AS JSON),
               'diseases', (select JSON_OBJECTAGG(
                                           IFNULL(d.id, 'null'),
                                           JSON_OBJECT(
                                                   'icdCode', IFNULL(d.icd_code, ''),
                                                   'name', COALESCE(NULLIF(d.name_en, ''), NULLIF(d.name_en, ''), ''),
                                                   'icdName', COALESCE(NULLIF(d.icd_name_en, ''), NULLIF(d.icd_name_en, ''), ''),
                                                   'isRare', 'null'
                                               ))
                            from disease d
                            where d.id in (select gtd.disease_id from gene_to_disease gtd where gtd.gene_id = gene.id)),
               'diseaseCategories', (select JSON_OBJECTAGG(IFNULL(disease_category.id, 'null'), JSON_OBJECT(
                'icdCode', IFNULL(disease_category.icd_code, ''),
                'icdCategoryName', COALESCE(NULLIF(disease_category.icd_name_en, ''), NULLIF(disease_category.icd_name_en, ''), ''))
                                                )
                                     FROM disease disease_category
                                     WHERE disease_category.icd_code in (select d.icd_code_visible
                                                                         from disease d
                                                                         where d.id in (select gtd.disease_id from gene_to_disease gtd where gtd.gene_id = gene.id)
                                                                           AND d.icd_name_en != "")
               ),
               'ncbiId', gene.ncbi_id,
               'uniprot', IFNULL(gene.uniprot, ''),
               'commentCause', (select JSON_OBJECTAGG(IFNULL(cc.id, 'null'), COALESCE(NULLIF(cc.name_en, ''), NULLIF(cc.name_en, ''), ''))
                                FROM comment_cause cc
                                WHERE cc.id IN (SELECT gtcc.comment_cause_id FROM gene_to_comment_cause gtcc WHERE gtcc.gene_id = gene.id)),
               'functionalClusters', (select JSON_ARRAYAGG(
                                                     JSON_OBJECT('id', IFNULL(fc.id, 0), 'name', COALESCE(NULLIF(fc.name_en, ''), NULLIF(fc.name_en, '')))
                                                 )
                                      FROM functional_cluster fc
                                      WHERE fc.id IN (select gtfc.functional_cluster_id from gene_to_functional_cluster gtfc where gtfc.gene_id = gene.id)
               ),
               'proteinClasses', (select JSON_ARRAYAGG(
                                                 JSON_OBJECT('id', IFNULL(pc.id, 0), 'name', COALESCE(NULLIF(pc.name_en, ''), NULLIF(pc.name_en, '')))
                                             )
                                  FROM protein_class pc
                                  WHERE pc.id IN (select gtpc.protein_class_id from gene_to_protein_class gtpc where gtpc.gene_id = gene.id)
               ),
               'expressionChange', gene.expressionChange,
               'timestamp', JSON_OBJECT('created', IFNULL(gene.created_at, ''), 'changed', IFNULL(gene.updated_at, '')),
               'methylationCorrelation', IFNULL(gene.methylation_horvath, ''),
               'ensembl', gene.ensembl,
               'agingMechanisms', (SELECT JSON_ARRAYAGG(
                                                  JSON_OBJECT('id', IFNULL(am.id, 0), 'name', COALESCE(NULLIF(am.name_en, ''), NULLIF(am.name_en, '')))
                                              )
                                   FROM aging_mechanism am
                                   WHERE am.id IN (SELECT ggg.aging_mechanism_id
                                                   FROM gene_ontology_to_aging_mechanism_visible ggg
                                                   WHERE ggg.gene_ontology_id IN (
                                                       SELECT gto.gene_ontology_id
                                                       FROM gene_to_ontology gto
                                                       WHERE gto.gene_id = gene.id))
                                     AND am.name_en != ''
               )
           )
FROM gene
WHERE gene.symbol = '{gene_symbol}';
'''

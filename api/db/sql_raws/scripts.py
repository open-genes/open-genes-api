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
    'experimentGroupQuantity', cre.experiment_number,
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


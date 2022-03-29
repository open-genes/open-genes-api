from pydantic import BaseModel




class CalorieRestrictionExperiment(BaseModel):
    lexpressionChangeLogFc: float
    pValue: str
    crResult: str
    measurementMethod: str
    measurementType: str
    restrictionPercent: int
    duration: int
    durationUnit: str
    age: str
    ageUnit: str
    organism: str
    line: str
    sex: str
    tissue: str
    experimentGroupQuantity: str
    doi: str
    expressionChangePercent: float
    isoform: str|None

    _name = 'calorie_restriction_experiment'
    _select = {
        'id': "calorie_restriction_experiment.id",
        'pValue': "p_val",
        'crResult': "COALESCE(calorie_restriction_experiment.name_@LANG@,calorie_restriction_experiment.name_en)",
        'measurementMethod': "measurement_method.name_@LANG@",
        'measurementType': "measurement_type.name_@LANG@",
        'restrictionPercent': "restriction_percent",
        'duration': "restriction_time",
        'durationUnit': "time_unit.name_@LANG@",
        'age': "age",
        'ageUnit': "time_unit_age.name_@LANG@",
        'organism': "model_organism.name_@LANG@",
        'line': "organism_line.name_@LANG@",
        'sex': "organism_sex.name_@LANG@",
        'tissue': "sample.name_@LANG@",
        'experimentGroupQuantity': "experiment_number",
        'doi': "doi",
        'expressionChangePercent': "expression_change_percent",
        'isoform': "isoform.name_@LANG@",
    }
    _from = """
    FROM gene
    JOIN calorie_restriction_experiment on gene.id = calorie_restriction_experiment.gene_id
    JOIN time_unit_age on calorie_restriction_experiment.age_time_unit_id = time_unit_age.id
    JOIN time_unit on calorie_restriction_experiment.restriction_time_unit_id = time_unit.id
    JOIN measurement_method on calorie_restriction_experiment.measurement_method_id = measurement_method.id
    JOIN measurement_type measurement_type on calorie_restriction_experiment.measurement_type_id = measurement_type.id
    JOIN organism_line on calorie_restriction_experiment.strain_id = organism_line.id
    JOIN organism_sex on calorie_restriction_experiment.organism_sex_id = organism_sex.id
    JOIN model_organism on calorie_restriction_experiment.model_organism_id = model_organism.id
    JOIN sample on calorie_restriction_experiment.tissue_id = sample.id
    LEFT JOIN isoform on calorie_restriction_experiment.isoform_id = isoform.id
    GROUP BY gene.id
    """

from pydantic import BaseModel
from models import *

class GeneralLifespanExperiment(BaseModel):
    id:int
    modelOrganism:str|None
    organismLine:str|None
    sex:str|None
    temperatureFrom:float|None
    temperatureTo:float|None
    diet:str|None
    expressionChangeTissue:str|None
    lifespanTimeUnit:str|None
    interventionResultForLifespan:str|None
    expressionMeasurementType:str|None
    controlCohortSize:int|None
    experimentCohortSize:int|None
    expressionChangePercent:float|None
    lifespanMinControl:float|None
    lifespanMeanControl:float|None
    lifespanMedianControl:float|None
    lifespanMaxControl:float|None
    lifespanMinExperiment:float|None
    lifespanMeanExperiment:float|None
    lifespanMedianExperiment:float|None
    lifespanMaxExperiment:float|None
    lifespanMinChangePercent:float|None
    lifespanMeanChangePercent:float|None
    lifespanMedianChangePercent:float|None
    lifespanMaxChangePercent:float|None
    lMinChangeStatSignificance:str|None
    lMeanChangeStatSignificance:str|None
    lMedianChangeStatSignificance:str|None
    lMaxChangeStatSignificance:str|None
    doi:str|None
    pmid:str|None
    comment:str|None
    populationDensity:str|None

class LifespanExperiment(BaseModel):
    id: int
    interventionMethod:str|None
    interventionWay:str|None
    tissueSpecific:str|None
    tissueSpecificPromoter:str|None
    treatmentStart:str|None
    treatmentEnd:str|None
    inductionByDrugWithdrawal:str|None
    treatmentDescription:str|None
    startTimeUnit:str|None
    endTimeUnit:str|None
    genotype:str|None
    drugDeliveryWay:str|None
    drug:str|None
    startStageOfDevelopment:str|None
    endStageOfDevelopment:str|None
    treatmentPeriod:str|None
    _select= {
        'id':'lifespan_experiment.id',
        'interventionMethod':'gene_intervention_method.name_@LANG@',
        'interventionWay':'gene_intervention_way.name_@LANG@',
        "tissueSpecific": "lifespan_experiment.tissue_specificity",
        "tissueSpecificPromoter": "lifespan_experiment.tissue_specific_promoter",
        "treatmentStart": 'lifespan_experiment.treatment_start',
        "treatmentEnd": 'lifespan_experiment.treatment_end',
        "inductionByDrugWithdrawal": "lifespan_experiment.mutation_induction",
        "treatmentDescription": "lifespan_experiment.description_of_therapy_@LANG@",
        "startTimeUnit": 'start_time_unit.name_@LANG@',
        "endTimeUnit": 'end_time_unit.name_@LANG@',
        "genotype": "genotype.name_@LANG@",
        "drugDeliveryWay": 'active_substance_delivery_way.name_@LANG@',
        "drug": 'active_substance.name_@LANG@',
        "startStageOfDevelopment": 'ts.name_@LANG@',
        "endStageOfDevelopment": 'te.name_@LANG@',
        "treatmentPeriod": 'experiment_treatment_period.name_@LANG@',
    }

class Tissue(BaseModel):
    id:int
    name:str|None
    _select= {
        'id':'sample.id',
        'name':'sample.name_@LANG@',
    }

class ControlAndExperimentTissue(Tissue):
    _name='ce_tissues'
    _from="""
from controlAndExperiment
join lifespan_experiment_to_tissue on lifespan_experiment_to_tissue.lifespan_experiment_id=controlAndExperiment.id
join sample on lifespan_experiment_to_tissue.tissue_id=sample.id
"""

class ExperimentTissue(Tissue):
    _name='e_tissues'
    _from="""
from experiment
join lifespan_experiment_to_tissue on lifespan_experiment_to_tissue.lifespan_experiment_id=experiment.id
join sample on lifespan_experiment_to_tissue.tissue_id=sample.id
"""


class ControlAndExperiment(LifespanExperiment):
    tissues:List[ControlAndExperimentTissue]
    _from="""
from increaseLifespan
join lifespan_experiment on lifespan_experiment.general_lifespan_experiment_id=increaseLifespan.id
left join gene_intervention_method on lifespan_experiment.gene_intervention_method_id=gene_intervention_method.id
left join gene_intervention_way on lifespan_experiment.gene_intervention_way_id=gene_intervention_way.id
left join time_unit start_time_unit on lifespan_experiment.treatment_start_time_unit_id=start_time_unit.id
left join time_unit end_time_unit on lifespan_experiment.treatment_end_time_unit_id=end_time_unit.id
left join genotype on lifespan_experiment.genotype=genotype.id
left join active_substance_delivery_way on lifespan_experiment.active_substance_delivery_way_id=active_substance_delivery_way.id
left join treatment_stage_of_development ts on lifespan_experiment.treatment_start_stage_of_development_id=ts.id
left join treatment_stage_of_development te on lifespan_experiment.treatment_end_stage_of_development_id=te.id
left join experiment_treatment_period on lifespan_experiment.treatment_period_id=experiment_treatment_period.id
left join active_substance on lifespan_experiment.active_substance_id=active_substance.id
where lifespan_experiment.type='control'
"""

class Experiment(LifespanExperiment):
    tissues:List[ExperimentTissue]
    _from="""
from increaseLifespan
join lifespan_experiment on lifespan_experiment.general_lifespan_experiment_id=increaseLifespan.id
left join gene_intervention_method on lifespan_experiment.gene_intervention_method_id=gene_intervention_method.id
left join gene_intervention_way on lifespan_experiment.gene_intervention_way_id=gene_intervention_way.id
left join time_unit start_time_unit on lifespan_experiment.treatment_start_time_unit_id=start_time_unit.id
left join time_unit end_time_unit on lifespan_experiment.treatment_end_time_unit_id=end_time_unit.id
left join genotype on lifespan_experiment.genotype=genotype.id
left join active_substance_delivery_way on lifespan_experiment.active_substance_delivery_way_id=active_substance_delivery_way.id
left join treatment_stage_of_development ts on lifespan_experiment.treatment_start_stage_of_development_id=ts.id
left join treatment_stage_of_development te on lifespan_experiment.treatment_end_stage_of_development_id=te.id
left join experiment_treatment_period on lifespan_experiment.treatment_period_id=experiment_treatment_period.id
left join active_substance on lifespan_experiment.active_substance_id=active_substance.id
where lifespan_experiment.type='experiment'
"""


class Interventions(BaseModel):
    controlAndExperiment:List[ControlAndExperiment]
    experiment:List[Experiment]

class InterventionImprove(BaseModel):
    id:int
    name:str
    _select={
        'id':"vital_process.id",
        'name':"vital_process.name_@LANG@",
    }
    _from="""
from increaseLifespan
join general_lifespan_experiment_to_vital_process on general_lifespan_experiment_to_vital_process.general_lifespan_experiment_id=increaseLifespan.id
join vital_process on general_lifespan_experiment_to_vital_process.vital_process_id=vital_process.id
where general_lifespan_experiment_to_vital_process.intervention_result_for_vital_process_id=1 /* IMPROVE */
"""

class InterventionDeteriorate(BaseModel):
    id:int
    name:str
    _select={
        'id':"vital_process.id",
        'name':"vital_process.name_@LANG@",
    }
    _from="""
from increaseLifespan
join general_lifespan_experiment_to_vital_process on general_lifespan_experiment_to_vital_process.general_lifespan_experiment_id=increaseLifespan.id
join vital_process on general_lifespan_experiment_to_vital_process.vital_process_id=vital_process.id
where general_lifespan_experiment_to_vital_process.intervention_result_for_vital_process_id=2 /* DETERIOR */
"""

class IncreaseLifespan(GeneralLifespanExperiment):
    interventions:Interventions
    interventionImproves:List[InterventionImprove]
    interventionDeteriorates:List[InterventionDeteriorate]
    _select= {
        'id':'general_lifespan_experiment.id',
        'modelOrganism':'lifespan_experiment_model_organism.name_@LANG@',
        'organismLine':'lifespan_experiment_organism_line.name_@LANG@',
        'sex':'lifespan_experiment_organism_sex.name_@LANG@',
        'temperatureFrom': 'general_lifespan_experiment.temperature_from',
        'temperatureTo': 'general_lifespan_experiment.temperature_to',
        'diet': 'lifespan_experiment_diet.name_@LANG@',
        'expressionChangeTissue': 'general_lifespan_experiment_sample.name_@LANG@',
        'lifespanTimeUnit': 'general_lifespan_experiment_time_unit.name_@LANG@',
        'interventionResultForLifespan': 'intervention_result_for_longevity.name_@LANG@',
        'expressionMeasurementType': 'general_lifespan_experiment_measurement_type.name_@LANG@',
        'controlCohortSize': 'general_lifespan_experiment.control_number',
        'experimentCohortSize': 'general_lifespan_experiment.experiment_number',
        'expressionChangePercent': 'general_lifespan_experiment.expression_change',
        'lifespanMinControl': 'general_lifespan_experiment.control_lifespan_min',
        'lifespanMeanControl': 'general_lifespan_experiment.control_lifespan_mean',
        'lifespanMedianControl': 'general_lifespan_experiment.control_lifespan_median',
        'lifespanMaxControl': 'general_lifespan_experiment.control_lifespan_max',
        'lifespanMinExperiment': 'general_lifespan_experiment.experiment_lifespan_min',
        'lifespanMeanExperiment': 'general_lifespan_experiment.experiment_lifespan_mean',
        'lifespanMedianExperiment': 'general_lifespan_experiment.experiment_lifespan_median',
        'lifespanMaxExperiment': 'general_lifespan_experiment.experiment_lifespan_max',
        'lifespanMinChangePercent': 'general_lifespan_experiment.lifespan_min_change',
        'lifespanMeanChangePercent': 'general_lifespan_experiment.lifespan_mean_change',
        'lifespanMedianChangePercent': 'general_lifespan_experiment.lifespan_median_change',
        'lifespanMaxChangePercent': 'general_lifespan_experiment.lifespan_max_change',
        'lMinChangeStatSignificance': 'ssmin.name_@LANG@',
        'lMeanChangeStatSignificance': 'ssmean.name_@LANG@',
        'lMedianChangeStatSignificance': 'ssmedian.name_@LANG@',
        'lMaxChangeStatSignificance': 'ssmax.name_@LANG@',
        'doi': 'general_lifespan_experiment.reference',
        'pmid':'general_lifespan_experiment.pmid',
        'comment':'general_lifespan_experiment.comment_@LANG@',
        'populationDensity':'general_lifespan_experiment.organism_number_in_cage',
    }
    _from="""
from gene
join lifespan_experiment on lifespan_experiment.gene_id=gene.id
join general_lifespan_experiment on general_lifespan_experiment.id = lifespan_experiment.general_lifespan_experiment_id
left join intervention_result_for_longevity on intervention_result_for_longevity.id = general_lifespan_experiment.intervention_result_id
left join model_organism as lifespan_experiment_model_organism on lifespan_experiment_model_organism.id = lifespan_experiment.model_organism_id
left join organism_line as lifespan_experiment_organism_line on lifespan_experiment_organism_line.id = general_lifespan_experiment.organism_line_id
left join organism_sex as lifespan_experiment_organism_sex on lifespan_experiment_organism_sex.id = general_lifespan_experiment.organism_sex_id
left join diet as lifespan_experiment_diet on lifespan_experiment_diet.id = general_lifespan_experiment.diet_id
left join sample as general_lifespan_experiment_sample on general_lifespan_experiment_sample.id = general_lifespan_experiment.changed_expression_tissue_id
left join time_unit general_lifespan_experiment_time_unit on general_lifespan_experiment_time_unit.id = general_lifespan_experiment.age_unit_id
left join measurement_type as general_lifespan_experiment_measurement_type on general_lifespan_experiment_measurement_type.id = general_lifespan_experiment.measurement_type
left join statistical_significance as ssmin on ssmin.id = general_lifespan_experiment.lifespan_min_change_stat_sign_id
left join statistical_significance as ssmean on ssmean.id = general_lifespan_experiment.lifespan_mean_change_stat_sign_id
left join statistical_significance as ssmedian on ssmedian.id = general_lifespan_experiment.lifespan_median_change_stat_sign_id
left join statistical_significance as ssmax on ssmax.id = general_lifespan_experiment.lifespan_max_change_stat_sign_id
"""



class Researches(BaseModel):
    increaseLifespan:List[IncreaseLifespan]

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
    lMinChangeStatSignificance:bool|None
    lMeanChangeStatSignificance:bool|None
    lMedianChangeStatSignificance:bool|None
    lMaxChangeStatSignificance:bool|None
    doi:str|None
    pmid:str|None
    comment:str|None
    populationDensity:int|None

class LifespanExperiment(BaseModel):
    id: int
    gene:int|None
    interventionMethod:str|None
    interventionWay:str|None
    tissueSpecific:bool|None
    tissueSpecificPromoter:bool|None
    treatmentStart:float|None
    treatmentEnd:float|None
    inductionByDrugWithdrawal:int|None
    treatmentDescription:str|None
    startTimeUnit:str|None
    endTimeUnit:str|None
    genotype:str|None
    drugDeliveryWay:str|None
    drug:str|None
    startStageOfDevelopment:str|None
    endStageOfDevelopment:str|None
    treatmentPeriod:str|None
    experimentMainEffect:str|None
    _select= {
        'id':'lifespan_experiment.id',
        'gene':'lifespan_experiment.gene_id',
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
        "experimentMainEffect": "experiment_main_effect.name_@LANG@",
    }
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
left join experiment_main_effect on lifespan_experiment.experiment_main_effect_id=experiment_main_effect.id
"""

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
    _from=LifespanExperiment._from+"""
where lifespan_experiment.type='control' and lifespan_experiment.gene_id<>increaseLifespan.gene_id
"""

class Experiment(LifespanExperiment):
    tissues:List[ExperimentTissue]
    _from=LifespanExperiment._from+"""
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
        'gene_id':'gene.id',
        'modelOrganism':'general_lifespan_experiment_model_organism.name_@LANG@',
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
join model_organism as general_lifespan_experiment_model_organism on general_lifespan_experiment_model_organism.id = general_lifespan_experiment.model_organism_id
left join intervention_result_for_longevity on intervention_result_for_longevity.id = general_lifespan_experiment.intervention_result_id
left join organism_line as lifespan_experiment_organism_line on lifespan_experiment_organism_line.id = general_lifespan_experiment.organism_line_id
left join organism_sex as lifespan_experiment_organism_sex on lifespan_experiment_organism_sex.id = general_lifespan_experiment.organism_sex_id
left join diet as lifespan_experiment_diet on lifespan_experiment_diet.id = general_lifespan_experiment.diet_id
left join sample as general_lifespan_experiment_sample on general_lifespan_experiment_sample.id = general_lifespan_experiment.changed_expression_tissue_id
left join time_unit general_lifespan_experiment_time_unit on general_lifespan_experiment_time_unit.id = general_lifespan_experiment.lifespan_change_time_unit_id
left join measurement_type as general_lifespan_experiment_measurement_type on general_lifespan_experiment_measurement_type.id = general_lifespan_experiment.measurement_type
left join statistical_significance as ssmin on ssmin.id = general_lifespan_experiment.lifespan_min_change_stat_sign_id
left join statistical_significance as ssmean on ssmean.id = general_lifespan_experiment.lifespan_mean_change_stat_sign_id
left join statistical_significance as ssmedian on ssmedian.id = general_lifespan_experiment.lifespan_median_change_stat_sign_id
left join statistical_significance as ssmax on ssmax.id = general_lifespan_experiment.lifespan_max_change_stat_sign_id
"""

class GeneAssociatedWithProgeriaSyndrome(BaseModel):
    progeriaSyndrome:str
    doi:None|str
    pmid:None|str
    comment:None|str
    _select={
        'progeriaSyndrome':'progeria_syndrome.name_@LANG@',
        'doi':'gene_to_progeria.reference',
        'pmid':'gene_to_progeria.pmid',
        'comment':'gene_to_progeria.comment_@LANG@',
    }
    _from="""
from gene
join gene_to_progeria on gene_to_progeria.gene_id=gene.id
join progeria_syndrome on progeria_syndrome.id=gene_to_progeria.progeria_syndrome_id
"""

class GeneAssociatedWithLongevityEffect(BaseModel):
    longevityEffect:str
    allelicPolymorphism:None|str
    sex:None|str
    allelicVariant:None|str
    modelOrganism:str
    changeType:None|str
    dataType:None|str
    doi:None|str
    pmid:None|str
    comment:None|str
    _select={
        'longevityEffect':'longevity_effect.name_@LANG@',
        'allelicPolymorphism':'polymorphism.name_@LANG@',
        'sex':"concat(gene_to_longevity_effect.sex_of_organism,'@LANG@')",
        'allelicVariant':'gene_to_longevity_effect.allele_variant',
        'modelOrganism':'longevity_effect_model_organism.name_@LANG@',
        'changeType':'longevity_effect_age_related_change_type.name_@LANG@',
        'dataType':"concat(gene_to_longevity_effect.data_type,'@LANG@')",
        'doi':'gene_to_longevity_effect.reference',
        'pmid':'gene_to_longevity_effect.pmid',
        'comment':'gene_to_longevity_effect.comment_@LANG@',
    }
    _from="""
from gene
join gene_to_longevity_effect on gene_to_longevity_effect.gene_id=gene.id
join longevity_effect on longevity_effect.id = gene_to_longevity_effect.longevity_effect_id
left join polymorphism on polymorphism.id = gene_to_longevity_effect.polymorphism_id
left join age_related_change_type as longevity_effect_age_related_change_type on longevity_effect_age_related_change_type.id = gene_to_longevity_effect.age_related_change_type_id
left join model_organism as longevity_effect_model_organism on longevity_effect_model_organism.id=gene_to_longevity_effect.model_organism_id
"""

class AgeRelatedChangeOfGene(BaseModel):
    changeType:str
    sample:None|str
    modelOrganism:str
    organismLine:str|None
    ageFrom:None|str
    ageTo:None|str
    valueForMale:None|str
    valueForFemale:None|str
    valueForAll:None|str
    measurementType:None|str
    doi:None|str
    pmid:None|str
    comment:str
    _select= {
        'changeType':'age_related_change_age_related_change_type.name_@LANG@',
        'sample':'sample.name_@LANG@',
        'modelOrganism':'age_related_change_model_organism.name_@LANG@',
        'organismLine':'age_related_change_organism_line.name_@LANG@',
        'ageFrom':"concat(age_related_change.age_from,' ',age_related_change_time_unit.name_@LANG@)",
        'ageTo':"concat(age_related_change.age_to,' ',age_related_change_time_unit.name_@LANG@)",
        'valueForMale':'age_related_change.change_value_male',
        'valueForFemale':'age_related_change.change_value_female',
        'valueForAll':'age_related_change.change_value_common',
        'measurementType':"concat(age_related_change.measurement_type,'@LANG@')",
        'doi':'age_related_change.reference',
        'pmid':'age_related_change.pmid',
        'comment':'age_related_change.comment_@LANG@',
    }
    _from="""
from gene
join age_related_change on age_related_change.gene_id=gene.id
join age_related_change_type as age_related_change_age_related_change_type on age_related_change_age_related_change_type.id=age_related_change.age_related_change_type_id
left join sample on sample.id = age_related_change.sample_id
left join model_organism as age_related_change_model_organism on age_related_change_model_organism.id = age_related_change.model_organism_id
left join organism_line as age_related_change_organism_line on age_related_change_organism_line.id = age_related_change.organism_line_id
left join time_unit age_related_change_time_unit on age_related_change_time_unit.id = age_related_change.age_unit_id
"""

class InterventionImproveVitalProcess(BaseModel):
    id:str
    name:str
    _name='interventionImproveVitalProcess'
    _select={
        'id':"vitalProcessId",
        'name':"vitalProcess",
    }
    _from=""" from interventionToGeneImprovesVitalProcesses where resultCode=1 /* IMPROVE */ """

class InterventionDeteriorateVitalProcess(BaseModel):
    id:str
    name:str
    _name='interventionDeteriorateVitalProcess'
    _select={
        'id':"vitalProcessId",
        'name':"vitalProcess",
    }
    _from=""" from interventionToGeneImprovesVitalProcesses where resultCode=2 /* DETERIOR */ """

class InterventionToGeneImprovesVitalProcess(BaseModel):
    id:str
    geneIntervention:str
    result:str
    resultCode:int
    vitalProcess:str
    vitalProcessId:str
    modelOrganism:str
    organismLine:None|str
    age:None|str
    genotype:None|str
    sex:None|str
    doi:None|str
    pmid:None|str
    comment:None|str
    interventionImproves:List[InterventionImproveVitalProcess]
    interventionDeteriorates:List[InterventionDeteriorateVitalProcess]
    _select= {
        'id':'gene_intervention_to_vital_process.id',
        'geneIntervention':'gene_intervention_method.name_@LANG@',
        'result':'intervention_result_for_vital_process.name_@LANG@',
        'resultCode':'intervention_result_for_vital_process.id',
        'vitalProcess':'vital_process.name_@LANG@',
        'vitalProcessId':'vital_process.id',
        'modelOrganism':'gene_intervention_to_vital_process_model_organism.name_@LANG@',
        'organismLine':'gene_intervention_to_vital_process_organism_line.name_@LANG@',
        'age':"concat(gene_intervention_to_vital_process.age,' ',gene_intervention_to_vital_process_time_unit.name_@LANG@)",
        'genotype':'genotype.name_@LANG@',
        'sex':'gene_intervention_to_vital_process_organism_sex.name_@LANG@',
        'doi':'gene_intervention_to_vital_process.reference',
        'pmid':'gene_intervention_to_vital_process.pmid',
        'comment':'gene_intervention_to_vital_process.comment_@LANG@',
    }
    _from="""
from gene
join gene_intervention_to_vital_process on gene_intervention_to_vital_process.gene_id=gene.id
join gene_intervention_result_to_vital_process on gene_intervention_to_vital_process.id = gene_intervention_result_to_vital_process.gene_intervention_to_vital_process_id
join vital_process on vital_process.id = gene_intervention_result_to_vital_process.vital_process_id
join intervention_result_for_vital_process on intervention_result_for_vital_process.id = gene_intervention_result_to_vital_process.intervention_result_for_vital_process_id
join gene_intervention_method on gene_intervention_method.id = gene_intervention_to_vital_process.gene_intervention_method_id
left join organism_sex as gene_intervention_to_vital_process_organism_sex on gene_intervention_to_vital_process_organism_sex.id = gene_intervention_to_vital_process.sex_of_organism
left join model_organism as gene_intervention_to_vital_process_model_organism on gene_intervention_to_vital_process_model_organism.id = gene_intervention_to_vital_process.model_organism_id
left join organism_line as gene_intervention_to_vital_process_organism_line on gene_intervention_to_vital_process_organism_line.id = gene_intervention_to_vital_process.organism_line_id
left join time_unit gene_intervention_to_vital_process_time_unit on gene_intervention_to_vital_process_time_unit.id=gene_intervention_to_vital_process.age_unit
left join genotype on genotype.id=gene_intervention_to_vital_process.genotype
"""

class RegulatedGene(BaseModel):
    id:int
    symbol:str
    name:str
    ncbiId:int
    _select= {
        'id':'regulated_gene.id',
        'symbol':'regulated_gene.symbol',
        'name':'regulated_gene.name',
        'ncbiId':'regulated_gene.ncbi_id',
    }

class ProteinRegulatesOtherGene(BaseModel):
    proteinActivity:str
    regulationType:str
    doi:None|str
    pmid:None|str
    comment:None|str
    regulatedGene:RegulatedGene
    _select={
        'proteinActivity':'protein_activity.name_@LANG@',
        'regulationType':'gene_regulation_type.name_@LANG@',
        'doi':'protein_to_gene.reference',
        'pmid':'protein_to_gene.pmid',
        'comment':'protein_to_gene.comment_@LANG@',
    }
    _from="""
from gene
join protein_to_gene on protein_to_gene.gene_id=gene.id
join open_genes.gene as regulated_gene on regulated_gene.id = protein_to_gene.regulated_gene_id
join protein_activity on protein_activity.id = protein_to_gene.protein_activity_id
join gene_regulation_type on gene_regulation_type.id = protein_to_gene.regulation_type_id
"""

class AdditionalEvidence(BaseModel):
    doi:None|str
    pmid:None|str
    comment:str
    _select={
        'doi':'gene_to_additional_evidence.reference',
        'pmid':'gene_to_additional_evidence.pmid',
        'comment':'gene_to_additional_evidence.comment_@LANG@',
    }
    _from=""" from gene join gene_to_additional_evidence on gene_to_additional_evidence.gene_id=gene.id """

class Researches(BaseModel):
    increaseLifespan:List[IncreaseLifespan]
    geneAssociatedWithProgeriaSyndromes:List[GeneAssociatedWithProgeriaSyndrome]
    geneAssociatedWithLongevityEffects:List[GeneAssociatedWithLongevityEffect]
    ageRelatedChangesOfGene:List[AgeRelatedChangeOfGene]
    interventionToGeneImprovesVitalProcesses:List[InterventionToGeneImprovesVitalProcess]
    proteinRegulatesOtherGenes:List[ProteinRegulatesOtherGene]
    additionalEvidences:List[AdditionalEvidence]

class IncreaseLifespanSearchInput(PaginationInput, LanguageInput, SortInput):
    byGeneId:int|None
    sortBy: Literal['lifespanMinChangePercent','lifespanMeanChangePercent',
            'lifespanMedianChangePercent','lifespanMaxChangePercent']|None = None
    _filters = {
        'byGeneId':[lambda value: 'gene.id=%s',lambda value:[value]],
    }
    _sorts = {
        'lifespanMinChangePercent': 'general_lifespan_experiment.lifespan_min_change',
        'lifespanMeanChangePercent': 'general_lifespan_experiment.lifespan_mean_change',
        'lifespanMedianChangePercent': 'general_lifespan_experiment.lifespan_median_change',
        'lifespanMaxChangePercent': 'general_lifespan_experiment.lifespan_max_change',
    }

class IncreaseLifespanSearched(IncreaseLifespan):
    geneId:int
    geneNcbiId:int|None
    geneName:str|None
    geneSymbol:str|None
    geneAliases:List[str]
    _select=IncreaseLifespan._select|{
        'geneId':'gene.id',
        'geneSymbol':'gene.symbol',
        'geneNcbiId':'gene.ncbi_id',
        'geneName':'gene.name',
        'geneAliases':'gene.aliases',
    }
    _name='increaseLifespan'
    _from="""
from general_lifespan_experiment
join lifespan_experiment on lifespan_experiment.general_lifespan_experiment_id=general_lifespan_experiment.id
join gene on gene.id = lifespan_experiment.gene_id
join model_organism as general_lifespan_experiment_model_organism on general_lifespan_experiment_model_organism.id = general_lifespan_experiment.model_organism_id
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
@FILTERING@
@PAGING@
"""
    _order_by="gene.id, general_lifespan_experiment.id"

class IncreaseLifespanSearchOutput(PaginatedOutput):
    items:List[IncreaseLifespanSearched]

class AgeRelatedChangeOfGeneResearched(AgeRelatedChangeOfGene):
    geneId:int
    geneNcbiId:int|None
    geneName:str|None
    geneSymbol:str|None
    geneAliases:List[str]
    _select=AgeRelatedChangeOfGene._select|{
        'geneId':'gene.id',
        'geneSymbol':'gene.symbol',
        'geneNcbiId':'gene.ncbi_id',
        'geneName':'gene.name',
        'geneAliases':'gene.aliases',
    }
    _name='ageRelatedChangeOfGene'
    _from="""
from age_related_change
left join gene on age_related_change.gene_id=gene.id
join age_related_change_type as age_related_change_age_related_change_type on age_related_change_age_related_change_type.id=age_related_change.age_related_change_type_id
left join sample on sample.id = age_related_change.sample_id
left join model_organism as age_related_change_model_organism on age_related_change_model_organism.id = age_related_change.model_organism_id
left join organism_line as age_related_change_organism_line on age_related_change_organism_line.id = age_related_change.organism_line_id
left join time_unit age_related_change_time_unit on age_related_change_time_unit.id = age_related_change.age_unit_id
"""

class AgeRelatedChangeOfGeneResearchOutput(PaginatedOutput):
    items:List[AgeRelatedChangeOfGeneResearched]

from models import *
from pydantic import BaseModel


class GeneralLifespanExperiment(BaseModel):
    id: int
    modelOrganism: str | None
    organismLine: str | None
    sex: str | None
    temperatureFrom: float | None
    temperatureTo: float | None
    diet: str | None
    expressionChangeTissue: str | None
    lifespanTimeUnit: str | None
    interventionResultForLifespan: str | None
    expressionMeasurementType: str | None
    controlCohortSize: int | None
    experimentCohortSize: int | None
    expressionChangePercent: float | None
    lifespanMinControl: float | None
    lifespanMeanControl: float | None
    lifespanMedianControl: float | None
    lifespanMaxControl: float | None
    lifespanMinExperiment: float | None
    lifespanMeanExperiment: float | None
    lifespanMedianExperiment: float | None
    lifespanMaxExperiment: float | None
    lifespanMinChangePercent: float | None
    lifespanMeanChangePercent: float | None
    lifespanMedianChangePercent: float | None
    lifespanMaxChangePercent: float | None
    lMinChangeStatSignificance: bool | None
    lMeanChangeStatSignificance: bool | None
    lMedianChangeStatSignificance: bool | None
    lMaxChangeStatSignificance: bool | None
    doi: str | None
    pmid: str | None
    comment: str | None
    populationDensity: int | None


class LifespanExperiment(BaseModel):
    id: int
    gene: int | None
    interventionMethod: str | None
    interventionWay: str | None
    tissueSpecific: bool | None
    tissueSpecificPromoter: str | None
    treatmentStart: float | None
    treatmentEnd: float | None
    inductionByDrugWithdrawal: int | None
    treatmentDescription: str | None
    startTimeUnit: str | None
    endTimeUnit: str | None
    genotype: str | None
    drugDeliveryWay: str | None
    drug: str | None
    startStageOfDevelopment: str | None
    endStageOfDevelopment: str | None
    treatmentPeriod: str | None
    experimentMainEffect: str | None
    _select = {
        'id': 'lifespan_experiment.id',
        'gene': 'lifespan_experiment.gene_id',
        'interventionMethod': 'gene_intervention_method.name_@LANG@',
        'interventionWay': 'gene_intervention_way.name_@LANG@',
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
    _from = """
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
    id: int
    name: str | None
    _select = {
        'id': 'sample.id',
        'name': 'sample.name_@LANG@',
    }


class ControlAndExperimentTissue(Tissue):
    _name = 'ce_tissues'
    _from = """
from controlAndExperiment
join lifespan_experiment_to_tissue on lifespan_experiment_to_tissue.lifespan_experiment_id=controlAndExperiment.id
join sample on lifespan_experiment_to_tissue.tissue_id=sample.id
"""


class ExperimentTissue(Tissue):
    _name = 'e_tissues'
    _from = """
from experiment
join lifespan_experiment_to_tissue on lifespan_experiment_to_tissue.lifespan_experiment_id=experiment.id
join sample on lifespan_experiment_to_tissue.tissue_id=sample.id
"""


class ControlAndExperiment(LifespanExperiment):
    tissues: List[ControlAndExperimentTissue]
    _from = (
        LifespanExperiment._from
        + """
where lifespan_experiment.type='control' and lifespan_experiment.gene_id<>increaseLifespan.gene_id
"""
    )


class Experiment(LifespanExperiment):
    tissues: List[ExperimentTissue]
    _from = (
        LifespanExperiment._from
        + """
where lifespan_experiment.type='experiment'
"""
    )


class Interventions(BaseModel):
    controlAndExperiment: List[ControlAndExperiment]
    experiment: List[Experiment]


class InterventionImprove(BaseModel):
    id: int
    name: str
    _select = {
        'id': "vital_process.id",
        'name': "vital_process.name_@LANG@",
    }
    _from = """
from increaseLifespan
join general_lifespan_experiment_to_vital_process on general_lifespan_experiment_to_vital_process.general_lifespan_experiment_id=increaseLifespan.id
join vital_process on general_lifespan_experiment_to_vital_process.vital_process_id=vital_process.id
where general_lifespan_experiment_to_vital_process.intervention_result_for_vital_process_id=1 /* IMPROVE */
"""


class InterventionDeteriorate(BaseModel):
    id: int
    name: str
    _select = {
        'id': "vital_process.id",
        'name': "vital_process.name_@LANG@",
    }
    _from = """
from increaseLifespan
join general_lifespan_experiment_to_vital_process on general_lifespan_experiment_to_vital_process.general_lifespan_experiment_id=increaseLifespan.id
join vital_process on general_lifespan_experiment_to_vital_process.vital_process_id=vital_process.id
where general_lifespan_experiment_to_vital_process.intervention_result_for_vital_process_id=2 /* DETERIOR */
"""


class IncreaseLifespan(GeneralLifespanExperiment):
    interventions: Interventions
    interventionImproves: List[InterventionImprove]
    interventionDeteriorates: List[InterventionDeteriorate]
    _select = {
        'id': 'general_lifespan_experiment.id',
        'gene_id': 'gene.id',
        'modelOrganism': 'general_lifespan_experiment_model_organism.name_@LANG@',
        'organismLine': 'lifespan_experiment_organism_line.name_@LANG@',
        'sex': 'lifespan_experiment_organism_sex.name_@LANG@',
        'temperatureFrom': 'general_lifespan_experiment.temperature_from',
        'temperatureTo': 'general_lifespan_experiment.temperature_to',
        'diet': 'lifespan_experiment_diet.name_@LANG@',
        'expressionChangeTissue': 'general_lifespan_experiment_sample.name_@LANG@',
        'lifespanTimeUnit': 'general_lifespan_experiment_time_unit.name_@LANG@',
        'interventionResultForLifespan': 'intervention_result_for_longevity.name_@LANG@',
        'expressionMeasurementType': 'general_lifespan_experiment_expression_evaluation.name_@LANG@',
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
        'pmid': 'general_lifespan_experiment.pmid',
        'comment': 'general_lifespan_experiment.comment_@LANG@',
        'populationDensity': 'general_lifespan_experiment.organism_number_in_cage',
    }
    _from = """
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
left join expression_evaluation as general_lifespan_experiment_expression_evaluation on general_lifespan_experiment_expression_evaluation.id = general_lifespan_experiment.expression_evaluation_by_id
left join statistical_significance as ssmin on ssmin.id = general_lifespan_experiment.lifespan_min_change_stat_sign_id
left join statistical_significance as ssmean on ssmean.id = general_lifespan_experiment.lifespan_mean_change_stat_sign_id
left join statistical_significance as ssmedian on ssmedian.id = general_lifespan_experiment.lifespan_median_change_stat_sign_id
left join statistical_significance as ssmax on ssmax.id = general_lifespan_experiment.lifespan_max_change_stat_sign_id
"""


class GeneAssociatedWithProgeriaSyndrome(BaseModel):
    progeriaSyndrome: str
    doi: None | str
    pmid: None | str
    comment: None | str
    _select = {
        'progeriaSyndrome': 'progeria_syndrome.name_@LANG@',
        'doi': 'gene_to_progeria.reference',
        'pmid': 'gene_to_progeria.pmid',
        'comment': 'gene_to_progeria.comment_@LANG@',
    }
    _from = """
from gene
join gene_to_progeria on gene_to_progeria.gene_id=gene.id
join progeria_syndrome on progeria_syndrome.id=gene_to_progeria.progeria_syndrome_id
"""


class GeneAssociatedWithLongevityEffect(BaseModel):
    longevityEffect: str
    polymorphismId: None | str
    sex: None | str
    associatedAllele: None | str
    nucleotideChange: None | str
    aminoAcidChange: None | str
    polymorphismOther: None | str
    nonAssociatedAllele: None | str
    frequencyControls: None | float
    frequencyExperiment: None | float
    minAgeOfControls: None | float
    maxAgeOfControls: None | float
    meanAgeOfControls: None | float
    minAgeOfExperiment: None | float
    maxAgeOfExperiment: None | float
    meanAgeOfExperiment: None | float
    nOfControls: None | int
    nOfExperiment: None | int
    position: None | str
    polymorphismType: None | str
    ethnicity: None | str
    studyType: None | str
    significance: None | str
    changeType: None | str
    dataType: None | str
    doi: None | str
    pmid: None | str
    comment: None | str
    _select = {
        'longevityEffect': 'longevity_effect.name_@LANG@',
        'polymorphismId': 'polymorphism.name_@LANG@',
        'associatedAllele': 'gene_to_longevity_effect.allele_variant',
        'nucleotideChange': 'gene_to_longevity_effect.nucleotide_change',
        'aminoAcidChange': 'gene_to_longevity_effect.amino_acid_change',
        'polymorphismOther': 'gene_to_longevity_effect.polymorphism_other',
        'nonAssociatedAllele': 'gene_to_longevity_effect.non_associated_allele',
        'frequencyControls': 'gene_to_longevity_effect.frequency_controls',
        'frequencyExperiment': 'gene_to_longevity_effect.frequency_experiment',
        'nOfControls': 'gene_to_longevity_effect.n_of_controls',
        'nOfExperiment': 'gene_to_longevity_effect.n_of_experiment',
        'minAgeOfControls': 'gene_to_longevity_effect.min_age_of_controls',
        'maxAgeOfControls': 'gene_to_longevity_effect.max_age_of_controls',
        'meanAgeOfControls': 'gene_to_longevity_effect.mean_age_of_controls',
        'minAgeOfExperiment': 'gene_to_longevity_effect.min_age_of_experiment',
        'maxAgeOfExperiment': 'gene_to_longevity_effect.max_age_of_experiment',
        'meanAgeOfExperiment': 'gene_to_longevity_effect.mean_age_of_experiment',
        'significance': 'gene_to_longevity_effect.significance',
        'changeType': 'longevity_effect_age_related_change_type.name_@LANG@',
        'sex': 'longevity_effect_organism_sex.name_@LANG@',
        'position': 'longevity_effect_position.name_@LANG@',
        'polymorphismType': 'longevity_effect_polymorphism_type.name_en',
        'ethnicity': 'longevity_effect_ethnicity.name_@LANG@',
        'studyType': 'longevity_effect_study_type.name_@LANG@',
        'dataType': "concat(gene_to_longevity_effect.data_type,'@LANG@')",
        'doi': 'gene_to_longevity_effect.reference',
        'pmid': 'gene_to_longevity_effect.pmid',
        'comment': 'gene_to_longevity_effect.comment_@LANG@',
    }
    _from = """
from gene
join gene_to_longevity_effect on gene_to_longevity_effect.gene_id=gene.id
join longevity_effect on longevity_effect.id = gene_to_longevity_effect.longevity_effect_id
left join polymorphism on polymorphism.id = gene_to_longevity_effect.polymorphism_id
left join age_related_change_type as longevity_effect_age_related_change_type on longevity_effect_age_related_change_type.id = gene_to_longevity_effect.age_related_change_type_id
left join organism_sex as longevity_effect_organism_sex on longevity_effect_organism_sex.id = gene_to_longevity_effect.sex_of_organism
left join position as longevity_effect_position on longevity_effect_position.id = gene_to_longevity_effect.position_id
left join polymorphism_type as longevity_effect_polymorphism_type on longevity_effect_polymorphism_type.id = gene_to_longevity_effect.polymorphism_type_id
left join ethnicity as longevity_effect_ethnicity on longevity_effect_ethnicity.id = gene_to_longevity_effect.ethnicity_id
left join study_type as longevity_effect_study_type on longevity_effect_study_type.id = gene_to_longevity_effect.study_type_id
@FILTERING@
"""


class AgeRelatedChangeOfGene(BaseModel):
    changeType: str
    sample: None | str
    modelOrganism: str
    organismLine: str | None
    value: None | str
    pValue: None | str
    measurementMethod: None | str
    doi: None | str
    pmid: None | str
    meanAgeOfControls: None | float
    meanAgeOfExperiment: None | float
    minAgeOfControls: None | float
    maxAgeOfControls: None | float
    minAgeOfExperiment: None | float
    maxAgeOfExperiment: None | float
    ageUnit: None | str
    expressionEvaluationBy: None | str
    statisticalMethod: None | str
    controlCohortSize: None | float
    experimentCohortSize: None | float
    sex: None | str
    comment: None | str
    _select = {
        'changeType': 'age_related_change_age_related_change_type.name_@LANG@',
        'sample': 'sample.name_@LANG@',
        'modelOrganism': 'age_related_change_model_organism.name_@LANG@',
        'organismLine': 'age_related_change_organism_line.name_@LANG@',
        'ageUnit': "age_related_change_time_unit.name_@LANG@",
        'value': 'age_related_change.change_value',
        'doi': 'age_related_change.reference',
        'pmid': 'age_related_change.pmid',
        'comment': 'age_related_change.comment_@LANG@',
        'meanAgeOfControls': 'age_related_change.mean_age_of_controls',
        'meanAgeOfExperiment': 'age_related_change.mean_age_of_experiment',
        'minAgeOfControls': 'age_related_change.min_age_of_controls',
        'maxAgeOfControls': 'age_related_change.max_age_of_controls',
        'minAgeOfExperiment': 'age_related_change.min_age_of_experiment',
        'maxAgeOfExperiment': 'age_related_change.max_age_of_experiment',
        'controlCohortSize': 'age_related_change.n_of_controls',
        'experimentCohortSize': 'age_related_change.n_of_experiment',
        'pValue': 'age_related_change.p_value',
        'expressionEvaluationBy': 'expression_evaluation.name_@LANG@',
        'measurementMethod': 'measurement_method.name_@LANG@',
        'statisticalMethod': 'statistical_method.name_@LANG@',
        'sex': 'organism_sex.name_@LANG@',
    }
    _from = """
from gene
join age_related_change on age_related_change.gene_id=gene.id
join age_related_change_type as age_related_change_age_related_change_type on age_related_change_age_related_change_type.id=age_related_change.age_related_change_type_id
left join sample on sample.id = age_related_change.sample_id
left join model_organism as age_related_change_model_organism on age_related_change_model_organism.id = age_related_change.model_organism_id
left join organism_line as age_related_change_organism_line on age_related_change_organism_line.id = age_related_change.organism_line_id
left join time_unit age_related_change_time_unit on age_related_change_time_unit.id = age_related_change.age_unit_id
left join expression_evaluation on age_related_change.expression_evaluation_by_id = expression_evaluation.id
left join measurement_method on age_related_change.measurement_method_id = measurement_method.id
left join statistical_method on age_related_change.statistical_method_id = statistical_method.id
left join organism_sex on age_related_change.sex = organism_sex.id
"""


class InterventionImproveVitalProcess(BaseModel):
    id: str
    name: str
    _name = 'interventionImproveVitalProcess'
    _select = {
        'id': "vitalProcessId",
        'name': "vitalProcess",
    }
    _from = """ from interventionToGeneImprovesVitalProcesses where resultCode=1 /* IMPROVE */ """


class InterventionDeteriorateVitalProcess(BaseModel):
    id: str
    name: str
    _name = 'interventionDeteriorateVitalProcess'
    _select = {
        'id': "vitalProcessId",
        'name': "vitalProcess",
    }
    _from = """ from interventionToGeneImprovesVitalProcesses where resultCode=2 /* DETERIOR */ """


class InterventionToGeneImprovesVitalProcess(BaseModel):
    id: str
    geneIntervention: str
    result: str
    resultCode: int
    vitalProcess: str
    vitalProcessId: str
    modelOrganism: str
    organismLine: None | str
    age: None | str
    genotype: None | str
    sex: None | str
    doi: None | str
    pmid: None | str
    comment: None | str
    interventionImproves: List[InterventionImproveVitalProcess]
    interventionDeteriorates: List[InterventionDeteriorateVitalProcess]
    _select = {
        'id': 'gene_intervention_to_vital_process.id',
        'geneIntervention': 'gene_intervention_method.name_@LANG@',
        'result': 'intervention_result_for_vital_process.name_@LANG@',
        'resultCode': 'intervention_result_for_vital_process.id',
        'vitalProcess': 'vital_process.name_@LANG@',
        'vitalProcessId': 'vital_process.id',
        'modelOrganism': 'gene_intervention_to_vital_process_model_organism.name_@LANG@',
        'organismLine': 'gene_intervention_to_vital_process_organism_line.name_@LANG@',
        'age': "concat(gene_intervention_to_vital_process.age,' ',gene_intervention_to_vital_process_time_unit.name_@LANG@)",
        'genotype': 'genotype.name_@LANG@',
        'sex': 'gene_intervention_to_vital_process_organism_sex.name_@LANG@',
        'doi': 'gene_intervention_to_vital_process.reference',
        'pmid': 'gene_intervention_to_vital_process.pmid',
        'comment': 'gene_intervention_to_vital_process.comment_@LANG@',
    }
    _from = """
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
    id: int
    symbol: str
    name: str
    ncbiId: int
    _select = {
        'id': 'regulated_gene.id',
        'symbol': 'regulated_gene.symbol',
        'name': 'regulated_gene.name',
        'ncbiId': 'regulated_gene.ncbi_id',
    }


class ProteinRegulatesOtherGene(BaseModel):
    proteinActivity: str
    regulationType: str
    doi: None | str
    pmid: None | str
    comment: None | str
    regulatedGene: RegulatedGene
    _select = {
        'proteinActivity': 'protein_activity.name_@LANG@',
        'regulationType': 'gene_regulation_type.name_@LANG@',
        'doi': 'protein_to_gene.reference',
        'pmid': 'protein_to_gene.pmid',
        'comment': 'protein_to_gene.comment_@LANG@',
    }
    _from = """
from gene
join protein_to_gene on protein_to_gene.gene_id=gene.id
join open_genes.gene as regulated_gene on regulated_gene.id = protein_to_gene.regulated_gene_id
join protein_activity on protein_activity.id = protein_to_gene.protein_activity_id
join gene_regulation_type on gene_regulation_type.id = protein_to_gene.regulation_type_id
"""


class AdditionalEvidence(BaseModel):
    doi: None | str
    pmid: None | str
    comment: str
    _select = {
        'doi': 'gene_to_additional_evidence.reference',
        'pmid': 'gene_to_additional_evidence.pmid',
        'comment': 'gene_to_additional_evidence.comment_@LANG@',
    }
    _from = """ from gene join gene_to_additional_evidence on gene_to_additional_evidence.gene_id=gene.id """


class Researches(BaseModel):
    increaseLifespan: List[IncreaseLifespan]
    geneAssociatedWithProgeriaSyndromes: List[GeneAssociatedWithProgeriaSyndrome]
    geneAssociatedWithLongevityEffects: List[GeneAssociatedWithLongevityEffect]
    ageRelatedChangesOfGene: List[AgeRelatedChangeOfGene]
    interventionToGeneImprovesVitalProcesses: List[InterventionToGeneImprovesVitalProcess]
    proteinRegulatesOtherGenes: List[ProteinRegulatesOtherGene]
    additionalEvidences: List[AdditionalEvidence]


class IncreaseLifespanSearchInput(PaginationInput, LanguageInput, SortInput):
    byGeneId: int | None
    byDiseases: str = None
    byDiseaseCategories: str = None
    byAgeRelatedProcess: str = None
    byExpressionChange: str = None
    bySelectionCriteria: str = None
    byAgingMechanism: str = None
    byProteinClass: str = None
    bySpecies: str = None
    byOrigin: str = None
    byFamilyOrigin: str = None
    byConservativeIn: str = None
    byGeneSymbol: str = None
    bySuggestions: str = None
    byChromosomeNum: str = None
    sortBy: Literal[
        'lifespanMinChangePercent',
        'lifespanMeanChangePercent',
        'lifespanMedianChangePercent',
        'lifespanMaxChangePercent',
    ] | None = None
    researches: str = None
    isHidden: str = 1
    _filters = {
        'byGeneId': [lambda value: 'gene.id=%s', lambda value: [value]],
        'isHidden': [lambda value: 'gene.isHidden!=1', lambda value: []],
        'byChromosomeNum': [
            lambda value: 'gene.chromosome in (' + ','.join(['%s' for v in value.split(',')]) + ')',
            lambda value: value.split(','),
        ],
        'byGeneSymbol': [
            lambda value: 'gene.symbol in (' + ','.join(['%s' for v in value.split(',')]) + ')',
            lambda value: value.split(','),
        ],
        'byDiseases': [
            lambda value: '(select count(*) from gene_to_disease where gene_to_disease.gene_id=gene.id and disease_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byDiseaseCategories': [
            lambda value: '(select count(*) from gene_to_disease g join disease d on g.disease_id=d.id join disease c on c.icd_code=d.icd_code_visible where g.gene_id=gene.id and c.id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byAgeRelatedProcess': [
            lambda value: '(select count(*) from gene_to_functional_cluster where gene_id=gene.id and functional_cluster_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byExpressionChange': [
            lambda value: 'gene.expressionChange in ('
            + ','.join(['%s' for v in value.split(',')])
            + ')',
            lambda value: value.split(','),
        ],
        'bySelectionCriteria': [
            lambda value: '(select count(*) from gene_to_comment_cause where gene_id=gene.id and comment_cause_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byAgingMechanism': [
            lambda value: '(select count(distinct aging_mechanism_id) from gene_to_ontology o join gene_ontology_to_aging_mechanism_visible a on a.gene_ontology_id=o.gene_ontology_id where o.gene_id=gene.id and aging_mechanism_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byProteinClass': [
            lambda value: '(select count(*) from gene_to_protein_class where gene_id=gene.id and protein_class_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'bySpecies': [
            lambda value: '(select count(distinct model_organism_id) from lifespan_experiment where lifespan_experiment.gene_id=gene.id and model_organism_id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byOrigin': [
            lambda value: '(select count(*) from phylum where gene.phylum_id=phylum.id and phylum.name_phylo in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byFamilyOrigin': [
            lambda value: '(select count(*) from phylum where gene.phylum_id=family_phylum.id and phylum.id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
        'byConservativeIn': [
            lambda value: '(select count(*) from taxon where gene.taxon_id=taxon.id and taxon.id in ('
            + ','.join(['%s' for v in value.split(',')])
            + '))=%s',
            lambda value: value.split(',') + [len(value.split(','))],
        ],
    }
    _sorts = {
        'lifespanMinChangePercent': 'general_lifespan_experiment.lifespan_min_change',
        'lifespanMeanChangePercent': 'general_lifespan_experiment.lifespan_mean_change',
        'lifespanMedianChangePercent': 'general_lifespan_experiment.lifespan_median_change',
        'lifespanMaxChangePercent': 'general_lifespan_experiment.lifespan_max_change',
    }


class IncreaseLifespanSearched(IncreaseLifespan):
    geneId: int
    geneNcbiId: int | None
    geneName: str | None
    geneSymbol: str | None
    geneAliases: List[str]
    _select = IncreaseLifespan._select | {
        'geneId': 'gene.id',
        'geneSymbol': 'gene.symbol',
        'geneNcbiId': 'gene.ncbi_id',
        'geneName': 'gene.name',
        'geneAliases': 'gene.aliases',
    }
    _name = 'increaseLifespan'
    _from = """
from general_lifespan_experiment
join lifespan_experiment on lifespan_experiment.general_lifespan_experiment_id=general_lifespan_experiment.id
join gene on gene.id = lifespan_experiment.gene_id
join model_organism as general_lifespan_experiment_model_organism on general_lifespan_experiment_model_organism.id = general_lifespan_experiment.model_organism_id
left join intervention_result_for_longevity on intervention_result_for_longevity.id = general_lifespan_experiment.intervention_result_id
left join organism_line as lifespan_experiment_organism_line on lifespan_experiment_organism_line.id = general_lifespan_experiment.organism_line_id
left join organism_sex as lifespan_experiment_organism_sex on lifespan_experiment_organism_sex.id = general_lifespan_experiment.organism_sex_id
left join diet as lifespan_experiment_diet on lifespan_experiment_diet.id = general_lifespan_experiment.diet_id
left join sample as general_lifespan_experiment_sample on general_lifespan_experiment_sample.id = general_lifespan_experiment.changed_expression_tissue_id
left join time_unit general_lifespan_experiment_time_unit on general_lifespan_experiment_time_unit.id = general_lifespan_experiment.lifespan_change_time_unit_id
left join expression_evaluation as general_lifespan_experiment_expression_evaluation on general_lifespan_experiment_expression_evaluation.id = general_lifespan_experiment.expression_evaluation_by_id
left join statistical_significance as ssmin on ssmin.id = general_lifespan_experiment.lifespan_min_change_stat_sign_id
left join statistical_significance as ssmean on ssmean.id = general_lifespan_experiment.lifespan_mean_change_stat_sign_id
left join statistical_significance as ssmedian on ssmedian.id = general_lifespan_experiment.lifespan_median_change_stat_sign_id
left join statistical_significance as ssmax on ssmax.id = general_lifespan_experiment.lifespan_max_change_stat_sign_id
@FILTERING@
@PAGING@
"""
    _order_by = "gene.id, general_lifespan_experiment.id"


class IncreaseLifespanSearchOutput(PaginatedOutput):
    items: List[IncreaseLifespanSearched]


class AgeRelatedChangeOfGeneResearched(AgeRelatedChangeOfGene):
    geneId: int
    geneNcbiId: int | None
    geneName: str | None
    geneSymbol: str | None
    geneAliases: List[str]
    _select = AgeRelatedChangeOfGene._select | {
        'geneId': 'gene.id',
        'geneSymbol': 'gene.symbol',
        'geneNcbiId': 'gene.ncbi_id',
        'geneName': 'gene.name',
        'geneAliases': 'gene.aliases',
    }
    _name = 'ageRelatedChangeOfGene'
    _from = """
from age_related_change
left join gene on age_related_change.gene_id=gene.id
join age_related_change_type as age_related_change_age_related_change_type on age_related_change_age_related_change_type.id=age_related_change.age_related_change_type_id
left join sample on sample.id = age_related_change.sample_id
left join model_organism as age_related_change_model_organism on age_related_change_model_organism.id = age_related_change.model_organism_id
left join organism_line as age_related_change_organism_line on age_related_change_organism_line.id = age_related_change.organism_line_id
left join time_unit age_related_change_time_unit on age_related_change_time_unit.id = age_related_change.age_unit_id
left join expression_evaluation on age_related_change.expression_evaluation_by_id = expression_evaluation.id
left join measurement_method on age_related_change.measurement_method_id = measurement_method.id
left join statistical_method on age_related_change.statistical_method_id = statistical_method.id
left join organism_sex on age_related_change.sex = organism_sex.id
@FILTERING@
@PAGING@
"""


class AgeRelatedChangeOfGeneResearchOutput(PaginatedOutput):
    items: List[AgeRelatedChangeOfGeneResearched]


#
class GeneActivityChangeImpactResearched(InterventionToGeneImprovesVitalProcess):
    geneId: int
    geneNcbiId: int | None
    geneName: str | None
    geneSymbol: str | None
    geneAliases: List[str]
    _select = InterventionToGeneImprovesVitalProcess._select | {
        'geneId': 'gene.id',
        'geneSymbol': 'gene.symbol',
        'geneNcbiId': 'gene.ncbi_id',
        'geneName': 'gene.name',
        'geneAliases': 'gene.aliases',
    }
    _name = 'interventionToGeneImprovesVitalProcesses'
    _from = """
from gene_intervention_to_vital_process
left join gene on gene_intervention_to_vital_process.gene_id=gene.id
join gene_intervention_result_to_vital_process on gene_intervention_to_vital_process.id = gene_intervention_result_to_vital_process.gene_intervention_to_vital_process_id
join vital_process on vital_process.id = gene_intervention_result_to_vital_process.vital_process_id
join intervention_result_for_vital_process on intervention_result_for_vital_process.id = gene_intervention_result_to_vital_process.intervention_result_for_vital_process_id
join gene_intervention_method on gene_intervention_method.id = gene_intervention_to_vital_process.gene_intervention_method_id
left join organism_sex as gene_intervention_to_vital_process_organism_sex on gene_intervention_to_vital_process_organism_sex.id = gene_intervention_to_vital_process.sex_of_organism
left join model_organism as gene_intervention_to_vital_process_model_organism on gene_intervention_to_vital_process_model_organism.id = gene_intervention_to_vital_process.model_organism_id
left join organism_line as gene_intervention_to_vital_process_organism_line on gene_intervention_to_vital_process_organism_line.id = gene_intervention_to_vital_process.organism_line_id
left join time_unit gene_intervention_to_vital_process_time_unit on gene_intervention_to_vital_process_time_unit.id=gene_intervention_to_vital_process.age_unit
left join genotype on genotype.id=gene_intervention_to_vital_process.genotype
@FILTERING@
@PAGING@
"""


class GeneActivityChangeImpactResearchedOutput(PaginatedOutput):
    items: List[GeneActivityChangeImpactResearched]


#
class GeneRegulationResearched(ProteinRegulatesOtherGene):
    geneId: int
    geneNcbiId: int | None
    geneName: str | None
    geneSymbol: str | None
    geneAliases: List[str]
    _select = ProteinRegulatesOtherGene._select | {
        'geneId': 'gene.id',
        'geneSymbol': 'gene.symbol',
        'geneNcbiId': 'gene.ncbi_id',
        'geneName': 'gene.name',
        'geneAliases': 'gene.aliases',
    }
    _name = 'proteinRegulatesOtherGene'
    _from = """
from protein_to_gene
left join gene on protein_to_gene.gene_id=gene.id
join open_genes.gene as regulated_gene on regulated_gene.id = protein_to_gene.regulated_gene_id
join protein_activity on protein_activity.id = protein_to_gene.protein_activity_id
join gene_regulation_type on gene_regulation_type.id = protein_to_gene.regulation_type_id
@FILTERING@
@PAGING@
"""


class GeneRegulationResearchedOutput(PaginatedOutput):
    items: List[GeneRegulationResearched]


#
class AssociationWithAcceleratedAgingResearched(GeneAssociatedWithProgeriaSyndrome):
    geneId: int
    geneNcbiId: int | None
    geneName: str | None
    geneSymbol: str | None
    geneAliases: List[str]
    _select = GeneAssociatedWithProgeriaSyndrome._select | {
        'geneId': 'gene.id',
        'geneSymbol': 'gene.symbol',
        'geneNcbiId': 'gene.ncbi_id',
        'geneName': 'gene.name',
        'geneAliases': 'gene.aliases',
    }
    _name = 'geneAssociatedWithProgeriaSyndrome'
    _from = """
from gene_to_progeria
join gene on gene_to_progeria.gene_id=gene.id
join progeria_syndrome on progeria_syndrome.id=gene_to_progeria.progeria_syndrome_id
@FILTERING@
@PAGING@
"""


class AssociationWithAcceleratedAgingResearchedOutput(PaginatedOutput):
    items: List[AssociationWithAcceleratedAgingResearched]


#
class AssociationsWithLifespanResearched(GeneAssociatedWithLongevityEffect):
    geneId: int
    geneNcbiId: int | None
    geneName: str | None
    geneSymbol: str | None
    geneAliases: List[str]
    _select = GeneAssociatedWithLongevityEffect._select | {
        'geneId': 'gene.id',
        'geneSymbol': 'gene.symbol',
        'geneNcbiId': 'gene.ncbi_id',
        'geneName': 'gene.name',
        'geneAliases': 'gene.aliases',
    }
    _name = 'geneAssociatedWithLongevityEffect'
    if not GeneAssociatedWithLongevityEffect._from:
        _from = """
    from gene_to_longevity_effect
    join gene on gene_to_longevity_effect.gene_id=gene.id
    join longevity_effect on longevity_effect.id = gene_to_longevity_effect.longevity_effect_id
    left join polymorphism on polymorphism.id = gene_to_longevity_effect.polymorphism_id
    left join age_related_change_type as longevity_effect_age_related_change_type on longevity_effect_age_related_change_type.id = gene_to_longevity_effect.age_related_change_type_id
    left join model_organism as longevity_effect_model_organism on longevity_effect_model_organism.id=gene_to_longevity_effect.model_organism_id
    @FILTERING@
    @PAGING@
    """


class AssociationsWithLifespanResearchedOutput(PaginatedOutput):
    items: List[AssociationsWithLifespanResearched]


#
class OtherEvidenceResearched(AdditionalEvidence):
    geneId: int
    geneNcbiId: int | None
    geneName: str | None
    geneSymbol: str | None
    geneAliases: List[str]
    _select = AdditionalEvidence._select | {
        'geneId': 'gene.id',
        'geneSymbol': 'gene.symbol',
        'geneNcbiId': 'gene.ncbi_id',
        'geneName': 'gene.name',
        'geneAliases': 'gene.aliases',
    }
    _name = 'additionalEvidence'
    _from = """
from gene_to_additional_evidence
join gene on gene_to_additional_evidence.gene_id=gene.id 
@FILTERING@
@PAGING@
 """


class OtherEvidenceResearchedOutput(PaginatedOutput):
    items: List[OtherEvidenceResearched]


#

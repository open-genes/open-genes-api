from mysql import connector

from config import CONFIG
from entities import entities
from db.suggestion_handler import suggestion_request_builder

# TODO(dmtgk): Add relationships integration.
# TODO(dmtgk): Add versatility to BaseDAO and pydantic entity validation.
class BaseDAO:
    def __init__(self):
        # Connect to server.
        self.cnx = connector.connect(
            host=CONFIG['DB_HOST'],
            port=CONFIG['DB_PORT'],
            user=CONFIG['DB_USER'],
            password=CONFIG['DB_PASSWORD'],
            database=CONFIG['DB_NAME'],
            ssl_disabled=True  # TODO(imhelle): Deal with ssl for db connection on droplet
        )

    def fetch_all(self,query,params=[],consume=None):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(query,params)
        if not consume: return cur.fetchall()
        count=0
        while r:=cur.fetchone():
            if consume(r): break
        return count


class GeneDAO(BaseDAO):
    """Gene Table fetcher."""
    def search(self,request):

        output={
            'gene':
            {
                'id':'gene.id',
                'homologueTaxon':"COALESCE(taxon.name_@LANG@,taxon.name_en)",
                'symbol':"gene.symbol",
                'name':"gene.name",
                'ncbiId':"gene.ncbi_id",
                'uniprot':"gene.uniprot",
                'expressionChange':"gene.expressionChange",
                'timestamp':
                {
                    'created':"gene.created_at",
                    'changed':"gene.updated_at",
                },
                'ensembl':"gene.ensembl",
                'methylationCorrelation':"gene.methylation_horvath",
                'aliases':["gene.aliases"], # TODO split into array in the controller
                'origin':
                {
                    'id':"phylum.id",
                    'phylum':"phylum.name_phylo",
                    'age':"phylum.name_mya",
                    'order':"phylum.order",
                },
                'familyOrigin':
                {
                    'id':"family_phylum.id",
                    'phylum':"family_phylum.name_phylo",
                    'age':"family_phylum.name_mya",
                    'order':"family_phylum.order",
                },
                '_from':"""
FROM gene
LEFT JOIN phylum family_phylum ON gene.family_phylum_id = family_phylum.id
LEFT JOIN phylum ON gene.phylum_id = phylum.id
LEFT JOIN taxon ON gene.taxon_id = taxon.id
@FILTERING@
order by @ORDERING@ gene.id
@PAGING@
""",

                'diseaseCategories':
                [{
                    'id':"disease_category.id",
                    'icdCode':"disease_category.icd_code",
                    'icdCategoryName':"COALESCE(disease_category.icd_name_@LANG@,disease.icd_name_@LANG@)",
                    '_from':"""

from gene join gene_to_disease on gene_to_disease.gene_id=gene.id
join open_genes.disease on disease.id=gene_to_disease.disease_id and not exists (select 1 from open_genes.disease d where disease.icd_code_visible=d.icd_code_visible and disease.id>d.id)
join open_genes.disease disease_category on disease_category.icd_code=disease.icd_code_visible
""",
                }],
                'diseases':
                [{
                    'id':"disease.id",
                    'icdCode':"disease.icd_code",
                    'name':"COALESCE(disease.name_@LANG@,disease.name_@LANG@)",
                    'icdName':"COALESCE(disease.icd_name_@LANG@,disease.icd_name_@LANG@)",
                    '_from':"from gene join gene_to_disease on gene_to_disease.gene_id=gene.id join disease on disease.id=gene_to_disease.disease_id",
                }],
                'commentCause':
                [{
                    'id':"comment_cause.id",
                    'name':"COALESCE(comment_cause.name_@LANG@,comment_cause.name_en)",
                    '_from':"from gene join gene_to_comment_cause on gene_to_comment_cause.gene_id=gene.id join comment_cause on comment_cause.id=gene_to_comment_cause.comment_cause_id",
                }],
                'proteinClasses':
                [{
                    'id':"protein_class.id",
                    'name':"COALESCE(protein_class.name_en,protein_class.name_en)",
                    '_from':"from gene join gene_to_protein_class on gene_to_protein_class.gene_id=gene.id join  protein_class on protein_class.id=gene_to_protein_class.protein_class_id",
                }],
                'agingMechanisms':
                [{
                    'id':'aging_mechanism.id',
                    'name':'coalesce(aging_mechanism.name_@LANG@,aging_mechanism.name_en)',
                    '_from':"""
FROM gene
LEFT JOIN `gene_to_ontology` ON gene_to_ontology.gene_id = gene.id
LEFT JOIN `gene_ontology_to_aging_mechanism_visible` ON gene_to_ontology.gene_ontology_id = gene_ontology_to_aging_mechanism_visible.gene_ontology_id
INNER JOIN `aging_mechanism` ON gene_ontology_to_aging_mechanism_visible.aging_mechanism_id = aging_mechanism.id AND aging_mechanism.name_en != '' """,
                }],
                'researches':
                {
                    'increaseLifespan':
                    [{
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
                        '_from':"""
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
""",
                        'interventions':
                        {
                            "controlAndExperiment":
                            [{
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
                                '_from':"""
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
""",
                                "tissues":
                                [{
                                    'id':'sample.id',
                                    'name':'sample.name_@LANG@',
                                    '_from':"""
from controlAndExperiment
join lifespan_experiment_to_tissue on lifespan_experiment_to_tissue.lifespan_experiment_id=controlAndExperiment.id
join sample on lifespan_experiment_to_tissue.tissue_id=sample.id
""",
                                    '_name':'tissues1',
                                }],

                            }],
                            "experiment":
                            [{
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
                                '_from':"""
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
""",
                                "tissues":
                                [{
                                    'id':'sample.id',
                                    'name':'sample.name_@LANG@',
                                    '_from':"""
from experiment
join lifespan_experiment_to_tissue on lifespan_experiment_to_tissue.lifespan_experiment_id=experiment.id
join sample on lifespan_experiment_to_tissue.tissue_id=sample.id
""",
                                    '_name':'tissues2',
                                }],

                            }],
                        },
                        "interventionImproves":
                        [{
                            'id':"vital_process.id",
                            'name':"vital_process.name_@LANG@",
                            '_from':"""
from increaseLifespan
join general_lifespan_experiment_to_vital_process on general_lifespan_experiment_to_vital_process.general_lifespan_experiment_id=increaseLifespan.id
join vital_process on general_lifespan_experiment_to_vital_process.vital_process_id=vital_process.id
where general_lifespan_experiment_to_vital_process.intervention_result_for_vital_process_id=1 /* IMPROVE */
""",

                        }],
                        "interventionDeteriorates":
                        [{
                            'id':"vital_process.id",
                            'name':"vital_process.name_@LANG@",
                            '_from':"""
from increaseLifespan
join general_lifespan_experiment_to_vital_process on general_lifespan_experiment_to_vital_process.general_lifespan_experiment_id=increaseLifespan.id
join vital_process on general_lifespan_experiment_to_vital_process.vital_process_id=vital_process.id
where general_lifespan_experiment_to_vital_process.intervention_result_for_vital_process_id=2 /* DETERIOR */
""",

                        }],

                    }],
                    'geneAssociatedWithProgeriaSyndromes':
                    [{
                        'progeriaSyndrome':'progeria_syndrome.name_@LANG@',
                        'doi':'gene_to_progeria.reference',
                        'pmid':'gene_to_progeria.pmid',
                        'comment':'gene_to_progeria.comment_@LANG@',
                        '_from':"""
from gene
join gene_to_progeria on gene_to_progeria.gene_id=gene.id
join progeria_syndrome on progeria_syndrome.id=gene_to_progeria.progeria_syndrome_id
""",
                     }],
                    'geneAssociatedWithLongevityEffects':
                    [{
                        'longevityEffect':'longevity_effect.name_@LANG@',
                        'allelicPolymorphism':'polymorphism.name_@LANG@',
                        'sex':'gene_to_longevity_effect.sex_of_organism',
                        'allelicVariant':'gene_to_longevity_effect.allele_variant',
                        'modelOrganism':'longevity_effect_model_organism.name_@LANG@',
                        'changeType':'longevity_effect_age_related_change_type.name_@LANG@',
                        'dataType':'gene_to_longevity_effect.data_type',
                        'doi':'gene_to_longevity_effect.reference',
                        'pmid':'gene_to_longevity_effect.pmid',
                        'comment':'gene_to_longevity_effect.comment_@LANG@',
                        '_from':"""
from gene
join gene_to_longevity_effect on gene_to_longevity_effect.gene_id=gene.id
join longevity_effect on longevity_effect.id = gene_to_longevity_effect.longevity_effect_id
left join polymorphism on polymorphism.id = gene_to_longevity_effect.polymorphism_id
left join age_related_change_type as longevity_effect_age_related_change_type on longevity_effect_age_related_change_type.id = gene_to_longevity_effect.age_related_change_type_id
left join model_organism as longevity_effect_model_organism on longevity_effect_model_organism.id=gene_to_longevity_effect.model_organism_id
""",
                     }],
                    'ageRelatedChangesOfGene':
                    [{
                        'changeType':'age_related_change_age_related_change_type.name_@LANG@',
                        'sample':'sample.name_@LANG@',
                        'modelOrganism':'age_related_change_model_organism.name_@LANG@',
                        'organismLine':'age_related_change_organism_line.name_@LANG@',
                        'ageFrom':'age_related_change.age_from',
                        'ageTo':'age_related_change.age_to',
                        'ageUnit':'age_related_change.age_unit',
                        'valueForMale':'age_related_change.change_value_male',
                        'valueForFemale':'age_related_change.change_value_female',
                        'valueForAll':'age_related_change.change_value_common',
                        'measurementType':'age_related_change.measurement_type',
                        'doi':'age_related_change.reference',
                        'pmid':'age_related_change.pmid',
                        'comment':'age_related_change.comment_@LANG@',
                        '_from':"""
from gene
join age_related_change on age_related_change.gene_id=gene.id
join age_related_change_type as age_related_change_age_related_change_type on age_related_change_age_related_change_type.id=age_related_change.age_related_change_type_id
left join sample on sample.id = age_related_change.sample_id
left join model_organism as age_related_change_model_organism on age_related_change_model_organism.id = age_related_change.model_organism_id
left join organism_line as age_related_change_organism_line on age_related_change_organism_line.id = age_related_change.organism_line_id """
                    }],
                    'interventionToGeneImprovesVitalProcesses':
                    [{
                        'id':'gene_intervention_to_vital_process.id',
                        'geneIntervention':'gene_intervention_method.name_@LANG@',
                        'result':'intervention_result_for_vital_process.name_@LANG@',
                        'resultCode':'intervention_result_for_vital_process.id',
                        'vitalProcess':'vital_process.name_@LANG@',
                        'vitalProcessId':'vital_process.id',
                        'modelOrganism':'gene_intervention_to_vital_process_model_organism.name_@LANG@',
                        'organismLine':'gene_intervention_to_vital_process_organism_line.name_@LANG@',
                        'age':'gene_intervention_to_vital_process.age',
                        'genotype':'gene_intervention_to_vital_process.genotype',
                        'ageUnit':'gene_intervention_to_vital_process.age_unit',
                        'sex':'gene_intervention_to_vital_process_organism_sex.name_@LANG@',
                        'doi':'gene_intervention_to_vital_process.reference',
                        'pmid':'gene_intervention_to_vital_process.pmid',
                        'comment':'gene_intervention_to_vital_process.comment_@LANG@',
                        '_from':"""
from gene
join gene_intervention_to_vital_process on gene_intervention_to_vital_process.gene_id=gene.id
join gene_intervention_result_to_vital_process on gene_intervention_to_vital_process.id = gene_intervention_result_to_vital_process.gene_intervention_to_vital_process_id
join vital_process on vital_process.id = gene_intervention_result_to_vital_process.vital_process_id
join intervention_result_for_vital_process on intervention_result_for_vital_process.id = gene_intervention_result_to_vital_process.intervention_result_for_vital_process_id
join gene_intervention_method on gene_intervention_method.id = gene_intervention_to_vital_process.gene_intervention_method_id
left join organism_sex as gene_intervention_to_vital_process_organism_sex on gene_intervention_to_vital_process_organism_sex.id = gene_intervention_to_vital_process.sex_of_organism
left join model_organism as gene_intervention_to_vital_process_model_organism on gene_intervention_to_vital_process_model_organism.id = gene_intervention_to_vital_process.model_organism_id
left join organism_line as gene_intervention_to_vital_process_organism_line on gene_intervention_to_vital_process_organism_line.id = gene_intervention_to_vital_process.organism_line_id
""",
                        "interventionImproves":
                        [{
                            'id':"vitalProcessId",
                            'name':"vitalProcess",
                            '_name':'interventionImproves2',
                            '_from':""" from interventionToGeneImprovesVitalProcesses where resultCode=1 /* IMPROVE */ """,
                        }],
                        "interventionDeteriorates":
                        [{
                            'id':"vitalProcessId",
                            'name':"vitalProcess",
                            '_name':'interventionImproves2',
                            '_from':""" from interventionToGeneImprovesVitalProcesses where resultCode=2 /* DETERIOR */ """,
                        }],
                     }],
                    'proteinRegulatesOtherGenes':
                    [{
                        'proteinActivity':'protein_activity.name_@LANG@',
                        'regulationType':'gene_regulation_type.name_@LANG@',
                        'doi':'protein_to_gene.reference',
                        'pmid':'protein_to_gene.pmid',
                        'comment':'protein_to_gene.comment_@LANG@',
                        'regulatedGene':
                        {
                            'id':'regulated_gene.id',
                            'symbol':'regulated_gene.symbol',
                            'name':'regulated_gene.name',
                            'ncbiId':'regulated_gene.ncbi_id',
                        },
                        '_from':"""
from gene
join protein_to_gene on protein_to_gene.gene_id=gene.id
join open_genes.gene as regulated_gene on regulated_gene.id = protein_to_gene.regulated_gene_id
join protein_activity on protein_activity.id = protein_to_gene.protein_activity_id
join gene_regulation_type on gene_regulation_type.id = protein_to_gene.regulation_type_id
""",
                     }],
                    'additionalEvidences':
                    [{
                        'doi':'gene_to_additional_evidence.reference',
                        'pmid':'gene_to_additional_evidence.pmid',
                        'comment':'gene_to_additional_evidence.comment_@LANG@',
                        '_from':""" from gene join gene_to_additional_evidence on gene_to_additional_evidence.gene_id=gene.id """,
                     }],
                },
            },
        }

        if 'researches' not in request or request['researches']!='1': del output['gene']['researches'];

        tables={}
        queue=[('','',output,tables)]
        while len(queue):
            (n,k,o,t)=queue.pop(0)
            if isinstance(o,list):
                queue[0:0]=[(n,k,i,t) for i in o]
                continue
            if not isinstance(o,dict):
                t[n]=o
                continue
            if '_from' in o:
                t={'_def':o,'_name':o.get('_name',k),'_parent':t.get('_name')}
                tables[t['_name']]=t
                n=''
            queue[0:0]=[((n+'_'+k).strip('_'),k,o[k],t) for k in o if not k.startswith('_')]

        primary_table=list(tables.keys())[0]
        query="with "+",\n".join([t+' as ( select concat('+((tables[t]['_parent']+'.ordering, ') if tables[t]['_parent'] else '')+"lpad(row_number() over(),5,'0')) as ordering"+(', count(*) over() as row_count' if t==primary_table else '')+', '+', '.join([tables[t][f]+' as "'+f+'"' for f in tables[t].keys() if not f.startswith('_')])+' '+tables[t]['_def']['_from']+')' for t in tables])
        query=query+"\n"+"\nunion ".join(['select '+t+'.ordering, '+(t+'.row_count' if t==primary_table else 'null')+" as row_count, '"+str(tables[t]['_name'])+"' as table_name,"+', '.join([', '.join([t+'.'+f+' as '+t+'_'+f for f in tables[t] if not f.startswith('_')]) for t in tables])+' '+' '.join([('from'if t2==primary_table else ('right join' if t2==t else 'left join'))+' '+t2+('' if t2==primary_table else ' on false') for t2 in tables]) for t in tables])
        query=query+"\norder by 1"

        ordering={
            'criteriaQuantity':'(select count(*) from gene_to_comment_cause where gene_id=gene.id)',
            'familyPhylum':'(select `order` from phylum where phylum.id=family_phylum_id)',
        }.get(request.get('sortBy'),'')
        if ordering: ordering=ordering+' '+request.get('sortOrder','')+', '
        query=query.replace("@ORDERING@",ordering)

        filtering={}
        if request.get('isHidden')!='1':
            filtering['gene.isHidden!=1']=[]
        if request.get('byGeneId'):
            filtering['gene.id in ('+','.join(['%s' for v in request['byGeneId'].split(',')])+')']=request['byGeneId'].split(',')
        if request.get('byDiseases'):
            filtering['(select count(*) from gene_to_disease where gene_to_disease.gene_id=gene.id and disease_id in ('+','.join(['%s' for v in request['byDiseases'].split(',')])+'))=%s']=request['byDiseases'].split(',')+[len(request['byDiseases'].split(','))]
        if request.get('byDiseaseCategories'):
            filtering['(select count(*) from gene_to_disease g join disease d on g.disease_id=d.id join disease c on c.icd_code=d.icd_code_visible where g.gene_id=gene.id and c.id in ('+','.join(['%s' for v in request['byDiseaseCategories'].split(',')])+'))=%s']=request['byDiseaseCategories'].split(',')+[len(request['byDiseaseCategories'].split(','))]
        if request.get('byAgeRelatedProcess'):
            filtering['(select count(*) from gene_to_functional_cluster where gene_id=gene.id and functional_cluster_id in ('+','.join(['%s' for v in request['byagerelatedprocess'].split(',')])+'))=%s']=request['byAgeRelatedProcess'].split(',')+[len(request['byAgeRelatedProcess'].split(','))]
        if request.get('byExpressionChange'):
            filtering['gene.expressionChange in ('+','.join(['%s' for v in request['byExpressionChange'].split(',')])+')']=request['byExpressionChange'].split(',')
        if request.get('bySelectionCriteria'):
            filtering['(select count(*) from gene_to_comment_cause where gene_id=gene.id and comment_cause_id in ('+','.join(['%s' for v in request['bySelectionCriteria'].split(',')])+'))=%s']=request['bySelectionCriteria'].split(',')+[len(request['bySelectionCriteria'].split(','))]
        if request.get('byAgingMechanism'):
            filtering['(select count(distinct aging_mechanism_id) from gene_to_ontology o join gene_ontology_to_aging_mechanism_visible a on a.gene_ontology_id=o.gene_ontology_id where o.gene_id=gene.id and aging_mechanism_id in ('+','.join(['%s' for v in request['byAgingMechanism'].split(',')])+'))=%s']=request['byAgingMechanism'].split(',')+[len(request['byAgingMechanism'].split(','))]
        if request.get('byProteinClass'):
            filtering['(select count(*) from gene_to_protein_class where gene_id=gene.id and protein_class_id in ('+','.join(['%s' for v in request['byProteinClass'].split(',')])+'))=%s']=request['byProteinClass'].split(',')+[len(request['byProteinClass'].split(','))]
        if request.get('bySpecies'):
            filtering['(select count(distinct model_organism_id) from lifespan_experiment where lifespan_experiment.gene_id=gene.id and model_organism_id in ('+','.join(['%s' for v in request['bySpecies'].split(',')])+'))=%s']=request['bySpecies'].split(',')+[len(request['bySpecies'].split(','))]
        params=[]
        if filtering:
            for p in filtering.values(): params=params+p
            filtering='where '+' and '.join(filtering.keys())
        else:
            filtering=''
        #print(filtering,params)
        query=query.replace("@FILTERING@",filtering)

        query=query.replace("@LANG@",request.get('lang','en'))

        page=request.get('page')
        page=int(page) if page is not None else 1
        pageSize=request.get('pageSize')
        pageSize=int(pageSize) if pageSize is not None else 10
        query=query.replace('@PAGING@','limit '+str(pageSize)+' offset '+str(pageSize*(page-1)));
        #print (query)

        re=[]
        row=None
        row_count=0
        lists={}

        def handle_row(r):
            nonlocal re
            if not r: return
            #queue=[('',r)]
            #while len(queue):
            #    (k,o)=queue.pop(0)
            #    if isinstance(o,list):
            #        queue[0:0]=[(k,i) for i in o]
            #        continue
            #    for k in [k for k in o if o[k] is None]: o[k]=''
            #    queue[0:0]=[(k,o[k]) for k in o if isinstance(o[k],dict) or isinstance(o[k],list) ]

            r['aliases']=[a for a in r['aliases'].split(' ') if a]
            if not r['origin']['id']:r['origin']=None
            if not r['familyOrigin']['id']: r['familyOrigin']=None
            re.append(r)

        def row_consumer(r):
            nonlocal row,lists,row_count
            t=r['table_name']
            if r['row_count'] is not None: row_count=r['row_count']

            if t==primary_table:
                handle_row(row)
                row={}
                data=row
                lists={}
            else:
                data={}

            queue=[(t,'',tables[t]['_def'],data)]
            while len(queue):
                (n,k,o,d)=queue.pop(0)
                if isinstance(o,list) and len(o) and isinstance(o[0],dict):
                    d[k]=[]
                    lists[o[0].get('_name',k)]=d[k]
                    continue
                if not isinstance(o,dict):
                    d[k]=r.get(n)
                    continue
                if k:
                    d[k]={}
                    d=d[k]
                queue[0:0]=[((n+'_'+k).strip('_'),k,o[k],d) for k in o if not k.startswith('_')]
            if tables[t]['_name'] in lists: lists[tables[t]['_name']].append(data)


            #r['aliases']=r['aliases'].split(' ')
        self.fetch_all(query,params,row_consumer)
        handle_row (row)
        return {'options':{'objTotal':row_count,"pagination":{"page":page,"pageSize":pageSize,"pagesTotal":row_count//pageSize + (row_count%pageSize!=0)}},'items':re}

    def get_duplicates_genes(self):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute('''
            SELECT min(gene.id) AS MAIN_GENE, GROUP_CONCAT(gene.id) AS GENES, COUNT(gene.id) as gid
            FROM gene
            GROUP BY gene.symbol
            HAVING gid > 1
            ''')
        return cur.fetchall()

    def change_table(self, tables, duplicates):
        cur = self.cnx.cursor(dictionary=True)
        for table in tables:
            for item in duplicates:
                for gene_id in item['GENES'].split(',')[1::]:
                    cur.execute(
                        '''
                        UPDATE {table} SET gene_id = {main_gene}
                            WHERE gene_id = {gene}
                        '''.format(
                            table=table,
                            main_gene=item['MAIN_GENE'],
                            gene=gene_id
                            )
                    )
        self.cnx.commit()
        return True

    def delete_duplicates(self, genes_to_delete):
        cur = self.cnx.cursor(dictionary=True)
        for gene_id in genes_to_delete:
            cur.execute('''
                DELETE gene
                FROM gene
                WHERE id = {gene_id}
                    '''.format(gene_id=gene_id))
        self.cnx.commit()
        return True

    def get_source_gene(self, gene_symbol):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            '''
            SELECT s.name FROM
            gene JOIN gene_to_source gts on gene.id = gts.gene_id
            JOIN source s on gts.source_id = s.id
            WHERE gene.symbol = "{}"
            '''.format(gene_symbol)
        )
        return cur.fetchone()

    def get_origin_for_gene(self, phylum_id):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM phylum WHERE phylum.id = %(phylum_id)s;",
            {'phylum_id': phylum_id}
        )
        return cur.fetchone()

    def get(
        self,
        ncbi_id: int = None,
    ) -> entities.Gene:
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM `gene` WHERE ncbi_id= %(ncbi_id)s;",
            {'ncbi_id': ncbi_id},
        )
        result = cur.fetchone()
        return result

    def get_by_symbol(
        self,
        gene: str,
    ) -> entities.Gene:
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM `gene` WHERE symbol='{}';".format(gene)
        )
        result = cur.fetchone()
        return result

    def add(
        self,
        gene: entities.Gene,
    ) -> entities.Gene:
        gene_dict = gene.dict(exclude_none=True)

        # It's OK to use f-strings, because of Pydantic validation.
        query = f"INSERT INTO `gene` ({', '.join(gene_dict.keys())}) "
        subs = ', '.join([f'%({k})s' for k in gene_dict.keys()])
        query += f"VALUES ({subs});"
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(query, gene_dict)
        self.cnx.commit()

        cur.execute(
            "SELECT * FROM gene WHERE ID=%(id)s;",
            {'id': cur.lastrowid},
        )
        result = cur.fetchone()
        self.cnx.close()

        return result

    def update(self, gene: entities.Gene, ) -> entities.Gene:
        gene_dict = gene.dict(exclude_none=True)
        prep_str = [f"`{k}` = %({k})s" for k in gene_dict.keys()]

        query = f"""
            UPDATE gene
            SET {', '.join(prep_str)}
            WHERE ncbi_id={gene_dict['ncbi_id']};
        """

        cur = self.cnx.cursor(dictionary=True)
        cur.execute(query, gene_dict)
        self.cnx.commit()
        cur.close()

        return self.get(ncbi_id=gene_dict['ncbi_id'])


class FunctionalClusterDAO(BaseDAO):
    """Functional cluster Table fetcher."""

    def get_from_gene(self, gene_id):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT functional_cluster_id "
            "FROM `gene_to_functional_cluster` "
            "WHERE gene_id= %(gene_id)s;",
            {'gene_id': gene_id},
        )
        return cur.fetchall()

    def get_by_id(self, functional_cluster_id):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM `functional_cluster` WHERE id= %(functional_cluster_id)s;",
            {'functional_cluster_id': functional_cluster_id},
        )
        return cur.fetchone()

    def get_all(self, lang):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute('SET SESSION group_concat_max_len = 100000;')
        cur.execute(
            '''
            SELECT CAST(CONCAT('[', GROUP_CONCAT( distinct JSON_OBJECT(
            'id', functional_cluster.id,
            'name', functional_cluster.name_{}
            ) separator ","), ']') AS JSON) AS jsonobj
            FROM functional_cluster'''.format(lang)
        )
        return cur.fetchall()


class AgingMechanismDAO(BaseDAO):

    def get_all(self, lang):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute('SET SESSION group_concat_max_len = 100000;')
        cur.execute(
            '''
            SELECT CAST(CONCAT('[', GROUP_CONCAT( distinct JSON_OBJECT(
            'id', aging_mechanism.id,
            'name', aging_mechanism.name_{}
            ) separator ","), ']') AS JSON) AS jsonobj
            FROM aging_mechanism'''.format(lang)
        )
        return cur.fetchall()


class SourceDAO(BaseDAO):

    def get_source(self, source: entities.Source):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT source.id "
            "FROM source "
            "WHERE name='{}'".format(source.name)
        )
        return cur.fetchone()

    def add_source(self, source: entities.Source):
        source_dict = source.dict(exclude_none=True)

        query = f"INSERT INTO `source` ({', '.join(source_dict.keys())}) "
        subs = ', '.join([f'%({k})s' for k in source_dict.keys()])
        query += f"VALUES ({subs});"

        cur = self.cnx.cursor(dictionary=True)
        cur.execute(query, source_dict)
        self.cnx.commit()

        cur.execute(
            "SELECT * FROM source WHERE ID=%(id)s;",
            {'id': cur.lastrowid},
        )
        result = cur.fetchone()
        self.cnx.close()

        return result

    def add_relation(self, gene_to_source: entities.GeneToSource):
        dict = gene_to_source.dict(exclude_none=True)

        query = f"INSERT INTO gene_to_source ({', '.join(dict.keys())}) "
        subs = ', '.join([f'%({k})s' for k in dict.keys()])
        query += f"VALUES ({subs});"

        cur = self.cnx.cursor(dictionary=True)
        cur.execute(query, dict)
        self.cnx.commit()
        return 0


class CommentCauseDAO(BaseDAO):
    """Comment cause Table fetcher."""

    def get_from_gene(self, gene_id):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT comment_cause_id "
            "FROM `gene_to_comment_cause` "
            "WHERE gene_id= %(gene_id)s;",
            {'gene_id': gene_id},
        )
        return cur.fetchall()

    def get_by_id(self, comment_cause_id):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM `comment_cause` WHERE id= %(comment_cause_id)s;",
            {'comment_cause_id': comment_cause_id},
        )
        return cur.fetchone()

    def get_all(self, lang):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute('SET SESSION group_concat_max_len = 100000;')
        cur.execute(
            '''
            SELECT CAST(CONCAT('[', GROUP_CONCAT( distinct JSON_OBJECT(
            'id', comment_cause.id,
            'name', comment_cause.name_{}
            ) separator ","), ']') AS JSON) AS jsonobj
            FROM comment_cause'''.format(lang)
        )
        return cur.fetchall()


class DiseaseDAO(BaseDAO):
    """Disease Table fetcher."""

    def get(
        self,
        icd_code: int = None,
    ) -> entities.Disease:
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM `disease` WHERE icd_code= %(icd_code)s;",
            {'icd_code': icd_code},
        )
        result = cur.fetchone()
        return result

    def get_from_gene(self, gene_id):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT disease_id FROM `gene_to_disease` WHERE gene_id= %(gene_id)s;",
            {'gene_id': gene_id},
        )
        return cur.fetchall()

    def get_by_id(self, disease_id):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM `disease` WHERE id= %(disease_id)s;",
            {'disease_id': disease_id},
        )
        return cur.fetchone()

    def update(self, disease: entities.Disease, ) -> entities.Disease:
        disease_dict = disease.dict(exclude_none=True)
        prep_str = [f"`{k}` = %({k})s" for k in disease_dict.keys()]
        query = f"""
            UPDATE disease
            SET {', '.join(prep_str)}
            WHERE icd_code=\'{disease_dict['icd_code']}\';
        """

        cur = self.cnx.cursor(dictionary=True)
        cur.execute(query, disease_dict)
        self.cnx.commit()
        cur.close()

        return self.get(icd_code=disease_dict['icd_code'])

class GeneSuggestionDAO(BaseDAO):
    """Gene suggestion fetcher for gene table"""
    def search(self, input:str):
        terms=[term for term in [[w for w in t.strip().split(' ') if w] for t in input.split(',') if t] if term]
        re={'items':[],'found':[],'notFound':terms}
        if not terms: return re

        # where's block
        term_checks = []
        for term in terms:
            word_checks = []
            for word in term:
                word_checks.append(suggestion_request_builder.build(word))
            term_checks.append(" AND ".join("(" + b + ")" for b in word_checks))
        where_block = " OR ".join("(" + t + ")" for t in term_checks)

        # names block
        names_block = ",".join(suggestion_request_builder.get_names())

        # found/notFound block
        def consume_row(r):
            nonlocal re, terms
            re['items'].append(r)
            for term in terms:
                f=True
                for w in term:
                    f=f and len([v for v in r.values() if (w.lower() in v.lower() if isinstance(v,str) else w==v) ])>0

                print (term,f)
                if f and term in re['notFound']:
                    re['found'].append(' '.join(term))
                    re['notFound']=[t for t in re['notFound'] if t!=term]
        # sql block
        sql = f"SELECT {names_block} FROM gene WHERE {where_block};"
        self.fetch_all(sql,{},consume_row)

        re['notFound']=[' '.join(t) for t in re['notFound']]
        return re

class CalorieExperimentDAO(BaseDAO):
    """Calorie experiment Table fetcher."""

    def get_list(self, request):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute('SET SESSION group_concat_max_len = 100000;')
        cur.execute(request)
        return cur.fetchall()

    def add_experiment(self, experiment: entities.CalorieRestrictionExperiment):
        experiment_dict = experiment.dict(exclude_none=True)

        query = f"INSERT INTO calorie_restriction_experiment ({', '.join(experiment_dict.keys())}) "
        subs = ', '.join([f'%({k})s' for k in experiment_dict.keys()])
        query += f"VALUES ({subs});"

        cur = self.cnx.cursor(dictionary=True)
        cur.execute(query, experiment_dict)
        self.cnx.commit()

        cur.execute(
            "SELECT * FROM calorie_restriction_experiment WHERE ID=%(id)s;",
            {'id': cur.lastrowid},
        )
        result = cur.fetchone()

        return result

    def get_measurement_method(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM measurement_method WHERE name_en='{}';".format(name)
        )
        return cur.fetchone()

    def get_measurement_type(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM measurement_type WHERE name_en='{}';".format(name)
        )
        return cur.fetchone()

    def get_model_organism(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM model_organism WHERE name_en='{}';".format(name)
        )
        return cur.fetchone()

    def get_organism_sex(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM organism_sex WHERE name_en='{}';".format(name)
        )
        return cur.fetchone()

    def get_organism_line(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM organism_line WHERE name_en='{}';".format(name)
        )
        return cur.fetchone()

    def get_sample(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM sample WHERE name_en='{}';".format(name)
        )
        return cur.fetchone()

    def get_isoform(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM isoform WHERE name_en='{}';".format(name)
        )
        return cur.fetchone()

    def get_treatment_time(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM treatment_time_unit WHERE name_en='{}';".format(name)
        )
        return cur.fetchone()

    def add_treatment_time(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO treatment_time_unit(name_en) VALUES ('{}');".format(name)
        )
        self.cnx.commit()

        cur.execute(
            "SELECT * FROM treatment_time_unit WHERE ID=%(id)s;",
            {'id': cur.lastrowid},
        )
        result = cur.fetchone()

        return cur.fetchone()

    def add_measurement_type(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO measurement_type(name_en) VALUES ('{}');".format(name)
        )
        self.cnx.commit()

        cur.execute(
            "SELECT * FROM measurement_type WHERE ID=%(id)s;",
            {'id': cur.lastrowid},
        )
        result = cur.fetchone()

        return cur.fetchone()

    def add_sample(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO sample(name_en) VALUES ('{}');".format(name)
        )
        self.cnx.commit()

        cur.execute(
            "SELECT * FROM sample WHERE ID=%(id)s;",
            {'id': cur.lastrowid},
        )
        result = cur.fetchone()

        return cur.fetchone()

    def add_isoform(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "INSERT INTO isoform(name_en) VALUES ('{}');".format(name)
        )
        self.cnx.commit()

        cur.execute(
            "SELECT * FROM isoform WHERE ID=%(id)s;",
            {'id': cur.lastrowid},
        )
        result = cur.fetchone()

        return cur.fetchone()

    def get_isoform(self, name):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM isoform WHERE name_en='{}';".format(name)
        )
        return cur.fetchone()

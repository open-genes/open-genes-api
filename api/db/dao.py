from mysql import connector

from config import CONFIG
from entities import entities
import copy


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
                'gene_id':'gene.id',
                'count':"count(*) over()",
                'homologueTaxon':"COALESCE(NULLIF(taxon.name_@LANG@, ''), NULLIF(taxon.name_en, ''), '')",
                'symbol':"IFNULL(gene.symbol,'')",
                'name':"IFNULL(gene.name,'')",
                'ncbi_id':"gene.ncbi_id",
                'uniprot':"IFNULL(gene.uniprot,'')",
                'timestamp':
                {
                    'created':"IFNULL(gene.created_at,'')",
                    'changed':"IFNULL(gene.updated_at,'')",
                },
                'ensembl':"gene.ensembl",
                'methylationCorrelation':"IFNULL(gene.methylation_horvath,'')",
                'aliases':"gene.aliases",
                'origin':
                {
                    'id':"phylum.id",
                    'phylum':"IFNULL(phylum.name_phylo,'')",
                    'age':"IFNULL(phylum.name_mya,'')",
                    'order':"phylum.order",
                    'test':"112",
                },
                'familyOrigin':
                {
                    'id':"family_phylum.id",
                    'phylum':"IFNULL(family_phylum.name_phylo,'')",
                    'age':"IFNULL(family_phylum.name_mya,'')",
                    'order':"family_phylum.order",
                },
                '_from':"""
FROM gene
LEFT JOIN phylum family_phylum ON gene.family_phylum_id = family_phylum.id
LEFT JOIN phylum ON gene.phylum_id = phylum.id
LEFT JOIN taxon ON gene.taxon_id = taxon.id
@FILTERING@
order by @ORDERING@ gene.id limit 20000""",

                'diseaseCategories':
                [{
                    'id':"IFNULL(disease_category.id,'null')",
                    'icdCode':"IFNULL(disease_category.icd_code,'')",
                    'icdCategoryName':"COALESCE(NULLIF(disease_category.icd_name_@LANG@, ''), NULLIF(disease.icd_name_@LANG@, ''), '')",
                    '_from':"from gene join gene_to_disease on gene_to_disease.gene_id=gene.gene_id join open_genes.disease on disease.id=gene_to_disease.disease_id join open_genes.disease disease_category on disease_category.icd_code=disease.icd_code_visible AND disease_category.icd_name_en != ''",
                }],
                'disease':
                [{
                    'id':"IFNULL(disease.id,'null')",
                    'icdCode':"IFNULL(disease.icd_code ,'')",
                    'name':"COALESCE(NULLIF(disease.name_@LANG@, ''), NULLIF(disease.name_@LANG@, ''), '')",
                    'icdName':"COALESCE(NULLIF(disease.icd_name_@LANG@, ''), NULLIF(disease.icd_name_@LANG@, ''), '')",
                    '_from':"from gene join gene_to_disease on gene_to_disease.gene_id=gene.gene_id join disease on disease.id=gene_to_disease.disease_id",
                }],
                'commentCause':
                [{
                    'id':"IFNULL(comment_cause.id,'null')",
                    'name':"COALESCE(NULLIF(comment_cause.name_@LANG@, ''), NULLIF(comment_cause.name_en, ''), '')",
                    '_from':"from gene join gene_to_comment_cause on gene_to_comment_cause.gene_id=gene.gene_id join comment_cause on comment_cause.id=gene_to_comment_cause.comment_cause_id",
                }],
                'proteinClasses':
                [{
                    'id':"IFNULL(protein_class.id,'null')",
                    'name':"COALESCE(NULLIF(protein_class.name_en, ''), NULLIF(protein_class.name_en, ''), '')",
                    '_from':"from gene join gene_to_protein_class on gene_to_protein_class.gene_id=gene.gene_id join  protein_class on protein_class.id=gene_to_protein_class.protein_class_id",
                }],
                'agingMechanisms':
                [{
                    'id':'aging_mechanism.id',
                    'name':'coalesce(aging_mechanism.name_@LANG@,aging_mechanism.name_en)',
                    '_from':"""
FROM gene
LEFT JOIN `gene_to_ontology` ON gene_to_ontology.gene_id = gene.gene_id
LEFT JOIN `gene_ontology_to_aging_mechanism_visible` ON gene_to_ontology.gene_ontology_id = gene_ontology_to_aging_mechanism_visible.gene_ontology_id
INNER JOIN `aging_mechanism` ON gene_ontology_to_aging_mechanism_visible.aging_mechanism_id = aging_mechanism.id AND aging_mechanism.name_en != '' """,
                }],
                'researches':
                {
                    'increaseLifespan':[{
                        'interventionType':'gene_intervention.name_@LANG@',
                        'interventionResult':'intervention_result_for_longevity.name_@LANG@',
                        'modelOrganism':'lifespan_experiment_model_organism.name_@LANG@',
                        'organismLine':'lifespan_experiment_organism_line.name_@LANG@',
                        'sex':'lifespan_experiment_organism_sex.name_@LANG@',
                        'general_lifespan_experiment_id':'lifespan_experiment.general_lifespan_experiment_id',
                        'age':'general_lifespan_experiment.age',
                        'treatment_start':'lifespan_experiment.treatment_start',
                        'startTimeUnit':'treatment_time_unit.name_@LANG@',
                        'genotype':'lifespan_experiment.genotype',
                        'valueForMale':'general_lifespan_experiment.lifespan_change_percent_male',
                        'valueForFemale':'general_lifespan_experiment.lifespan_change_percent_female',
                        'valueForAll':'general_lifespan_experiment.lifespan_change_percent_common',
                        'doi':'general_lifespan_experiment.reference',
                        'pmid':'general_lifespan_experiment.pmid',
                        'comment':'general_lifespan_experiment.comment_@LANG@',
                        '_from':"""
from gene
join lifespan_experiment on lifespan_experiment.gene_id=gene.gene_id
join gene_intervention on gene_intervention.id=lifespan_experiment.gene_intervention_id
join intervention_result_for_longevity on intervention_result_for_longevity.id=lifespan_experiment.intervention_result_id
join general_lifespan_experiment on general_lifespan_experiment.id=lifespan_experiment.general_lifespan_experiment_id
left join model_organism as lifespan_experiment_model_organism on lifespan_experiment_model_organism.id=lifespan_experiment.model_organism_id
left join organism_line as lifespan_experiment_organism_line on lifespan_experiment_organism_line.id=general_lifespan_experiment.organism_line_id
left join organism_sex as lifespan_experiment_organism_sex on lifespan_experiment_organism_sex.id=general_lifespan_experiment.organism_sex_id
left join treatment_time_unit on treatment_time_unit.id=lifespan_experiment.treatment_start_time_unit_id
""",
                    }],
                    'geneAssociatedWithProgeriaSyndromes':[{
                        'progeriaSyndrome':'progeria_syndrome.name_@LANG@',
                        'doi':'gene_to_progeria.reference',
                        'pmid':'gene_to_progeria.pmid',
                        'comment':'gene_to_progeria.comment_@LANG@',
                        '_from':"""
from gene
join gene_to_progeria on gene_to_progeria.gene_id=gene.gene_id
join progeria_syndrome on progeria_syndrome.id=gene_to_progeria.progeria_syndrome_id
""",
                     }],
                    'geneAssociatedWithLongevityEffects':[{
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
join gene_to_longevity_effect on gene_to_longevity_effect.gene_id=gene.gene_id
join longevity_effect on longevity_effect.id = gene_to_longevity_effect.longevity_effect_id
left join polymorphism on polymorphism.id = gene_to_longevity_effect.polymorphism_id
left join age_related_change_type as longevity_effect_age_related_change_type on longevity_effect_age_related_change_type.id = gene_to_longevity_effect.age_related_change_type_id
left join model_organism as longevity_effect_model_organism on longevity_effect_model_organism.id=gene_to_longevity_effect.model_organism_id
""",
                     }],
                    'ageRelatedChangesOfGene': [{
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
join age_related_change on age_related_change.gene_id=gene.gene_id
join age_related_change_type as age_related_change_age_related_change_type on age_related_change_age_related_change_type.id=age_related_change.age_related_change_type_id
left join sample on sample.id = age_related_change.sample_id
left join model_organism as age_related_change_model_organism on age_related_change_model_organism.id = age_related_change.model_organism_id
left join organism_line as age_related_change_organism_line on age_related_change_organism_line.id = age_related_change.organism_line_id """
                    }],
                    'interventionToGeneImprovesVitalProcesses':[{
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
join gene_intervention_to_vital_process on gene_intervention_to_vital_process.gene_id=gene.gene_id
join gene_intervention_result_to_vital_process on gene_intervention_to_vital_process.id = gene_intervention_result_to_vital_process.gene_intervention_to_vital_process_id
join vital_process on vital_process.id = gene_intervention_result_to_vital_process.vital_process_id
join intervention_result_for_vital_process on intervention_result_for_vital_process.id = gene_intervention_result_to_vital_process.intervention_result_for_vital_process_id
join gene_intervention_method on gene_intervention_method.id = gene_intervention_to_vital_process.gene_intervention_method_id
left join organism_sex as gene_intervention_to_vital_process_organism_sex on gene_intervention_to_vital_process_organism_sex.id = gene_intervention_to_vital_process.sex_of_organism
left join model_organism as gene_intervention_to_vital_process_model_organism on gene_intervention_to_vital_process_model_organism.id = gene_intervention_to_vital_process.model_organism_id
left join organism_line as gene_intervention_to_vital_process_organism_line on gene_intervention_to_vital_process_organism_line.id = gene_intervention_to_vital_process.organism_line_id
""",
                     }],
                    'proteinRegulatesOtherGenes':[{
                        'regulatedGeneId':'regulated_gene.id',
                        'regulatedGeneSymbol':'regulated_gene.symbol',
                        'regulatedGeneName':'regulated_gene.name',
                        'regulatedGeneNcbiId':'regulated_gene.ncbi_id',
                        'proteinActivity':'protein_activity.name_@LANG@',
                        'regulationType':'gene_regulation_type.name_@LANG@',
                        'doi':'protein_to_gene.reference',
                        'pmid':'protein_to_gene.pmid',
                        'comment':'protein_to_gene.comment_@LANG@',
                        '_from':"""
from gene
join protein_to_gene on protein_to_gene.gene_id=gene.gene_id
join open_genes.gene as regulated_gene on regulated_gene.id = protein_to_gene.regulated_gene_id
join protein_activity on protein_activity.id = protein_to_gene.protein_activity_id
join gene_regulation_type on gene_regulation_type.id = protein_to_gene.regulation_type_id
""",
                     }],
                    'additionalEvidences':[{
                        'doi':'gene_to_additional_evidence.reference',
                        'pmid':'gene_to_additional_evidence.pmid',
                        'comment':'gene_to_additional_evidence.comment_@LANG@',
                        '_from':""" from gene join gene_to_additional_evidence on gene_to_additional_evidence.gene_id=gene.gene_id """,
                     }],
                },
            },
        }

        if 'researches' in request and request['researches']=='0': del output['gene']['researches'];

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
                t={'_from':o['_from'],'_output':o,'_name':n}
                tables[k]=t
                n=k
            queue[0:0]=[((n+'_'+k).strip('_'),k,o[k],t) for k in o if not k.startswith('_')]
        #print(tables)
        #return

        primary_table=list(tables.keys())[0]
        query="with "+",\n".join([t+' as ( select '+'row_number() over() as '+t+('_o1' if t==primary_table else '_o2')+', '+('0 as '+t+'_o2' if t==primary_table else primary_table+'_o1 as '+t+'_o1')+', '+', '.join([tables[t][f]+' as `'+f+'`' for f in tables[t].keys() if not f.startswith('_')])+' '+tables[t]['_from']+')' for t in tables])
        query=query+"\n"+"\nunion ".join(['select *, '+t+'_o1 as primary_ordering, '+t+'_o2 as secondary_ordering '+' '.join([('from'if t2==primary_table else ('right join' if t2==t else 'left join'))+' '+t2+('' if t2==primary_table else ' on false') for t2 in tables]) for t in tables])
        query=query+"\norder by primary_ordering,secondary_ordering"

        ordering={
            'criteriaQuantity':'(select count(*) from gene_to_comment_cause where gene_id=gene.id)',
            'familyPhylum':'(select `order` from phylum where phylum.id=family_phylum_id)',
        }.get(request.get('sortBy'),'')
        if ordering: ordering=ordering+' '+request.get('sortOrder','')+', '
        query=query.replace("@ORDERING@",ordering)

        filtering={}
        if request.get('byDiseases'):
            filtering['(select count(*) from gene_to_disease where gene_to_disease.gene_id=gene.id and disease_id in ('+','.join(['%s' for v in request['byDiseases'].split(',')])+'))=%s']=request['byDiseases'].split(',')+[len(request['byDiseases'].split(','))]
        params=[]
        if filtering:
            for p in filtering.values(): params=params+p
            filtering='where '+' and '.join(filtering.keys())
        else:
            filtering=''
        print(filtering,params)
        query=query.replace("@FILTERING@",filtering)

        query=query.replace("@LANG@",request.get('lang','en'))
        #print (query)

        re=[]
        row=None
        lists={}

        prev_id=None

        def handle_row(r):
            nonlocal re
            if not r: return
            re.append(r)

        def row_consumer(r):
            nonlocal row,lists
            t=None
            for n in r:
                s=n.rsplit('_o',1)
                if s[-1].isnumeric() and r[n]:
                    t=s[0]
                    break
            if not t:
                print ('Unexpected row',row)
                return

            if t==primary_table:
                handle_row(row)
                row={}
                data=row
                lists={}
            else:
                data={}

            queue=[(t,'',tables[t]['_output'],data)]
            while len(queue):
                (n,k,o,d)=queue.pop(0)
                if isinstance(o,list):
                    d[k]=[]
                    lists[n]=d[k]
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
        return re

    def get_list(self, request):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute('SET SESSION group_concat_max_len = 100000;')
        cur.execute(request)
        return cur.fetchall()

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

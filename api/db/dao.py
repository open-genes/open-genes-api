import json
from itertools import chain
from typing import get_args, get_origin

from config import CONFIG
from db.suggestion_handler import suggestion_request_builder
from entities import entities
from models.gene import (
    AgeRelatedChangeOfGeneResearched,
    AgeRelatedChangeOfGeneResearchOutput,
    AssociationsWithLifespanResearched,
    AssociationsWithLifespanResearchedOutput,
    AssociationWithAcceleratedAgingResearched,
    AssociationWithAcceleratedAgingResearchedOutput,
    CalorieExperimentOutput,
    GeneActivityChangeImpactResearched,
    GeneActivityChangeImpactResearchedOutput,
    GeneRegulationResearched,
    GeneRegulationResearchedOutput,
    GeneSearched,
    GeneSearchOutput,
    GeneSingle,
    IncreaseLifespanSearched,
    IncreaseLifespanSearchOutput,
    OtherEvidenceResearched,
    OtherEvidenceResearchedOutput,
)
from models.various import ModelOrganismOutput
from mysql import connector
from pydantic import BaseModel


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
            ssl_disabled=True,  # TODO(imhelle): Deal with ssl for db connection on droplet
        )

    def fetch_all(self, query, params=[], consume=None):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(query, params)
        if not consume:
            return cur.fetchall()
        count = 0
        while r := cur.fetchone():
            if consume(r):
                break
        return count

    def prepare_tables(self, model):
        tables = {}
        model = (get_args(model)[0] if get_origin(model) else model, model)
        queue = [('', '', model, tables, None)]
        while len(queue):
            (n, k, m, t, p) = queue.pop(0)
            m_outer_type = m[1]
            m = m[0]
            if hasattr(m, '_supress') and m._supress:
                continue
            if hasattr(m, '_from'):
                t = {
                    '_model': m,
                    '_outer_type': m_outer_type,
                    '_root_model': model,
                    '_name': m._name if hasattr(m, '_name') else (k if k else 'dummy'),
                    '_parent': t.get('_name'),
                    '_from': m._from,
                    '_join': '',
                }
                tables[t['_name']] = t
                n = ''
            if hasattr(m, '_join'):
                t['_join'] = (t['_join'] + "\n" + m._join).strip()
            if not issubclass(m, BaseModel):
                t[n] = p._select.get(k, k) if hasattr(p, '_select') else k
                continue
            queue[0:0] = [
                (
                    '_'.join(filter(None, [n, k])),
                    k,
                    (m.__fields__[k].type_, m.__fields__[k].outer_type_),
                    t,
                    m,
                )
                for k in m.__fields__
            ]
        if '_meta' in tables:
            m = tables['_meta']
            del tables['_meta']
            tables['_meta'] = m

        return tables

    def prepare_query(self, tables, input):
        primary_table = list(tables.keys())[0]
        for table in [tables[t] for t in tables if '@JOINS@' not in tables[t]['_from']]:
            table['_from'] = table['_from'].strip() + "\n@JOINS@\n"
        query = "with " + ",\n".join(
            [
                t
                + ' as ( select '
                + (
                    "'0'"
                    if t == '_meta'
                    else 'concat('
                    + (
                        (tables[t]['_parent'] + '.ordering, ')
                        if tables[t]['_parent'] and tables[t]['_parent'] != '_meta'
                        else ''
                    )
                    + "lpad(row_number() over(order by "
                    + ('@ORDERING@' if t == primary_table else '')
                    + ' '
                    + (
                        tables[t]['_model']._order_by
                        if hasattr(tables[t]['_model'], '_order_by')
                        else 'null'
                    )
                    + "),5,'0'))"
                )
                + ' as ordering, '
                + ('count(*) over() as row_count, ' if t == primary_table else '')
                + ', '.join(
                    [
                        tables[t][f] + ' as "' + f + '"'
                        for f in tables[t].keys()
                        if f and not f.startswith('_')
                    ]
                    + [
                        tables[t]['_model']._select[s] + ' as "' + s + '"'
                        for s in (
                            tables[t]['_model']._select
                            if hasattr(tables[t]['_model'], '_select')
                            else {}
                        )
                        if s not in tables[t]
                    ]
                )
                + '\n'
                + tables[t]['_from'].lstrip().replace('@JOINS@', tables[t].get('_join', ''))
                + ')'
                for t in tables
            ]
        )
        query = (
            query
            + "\n"
            + "\nunion ".join(
                [
                    'select '
                    + t
                    + ".ordering, '"
                    + str(tables[t]['_name'])
                    + "' as table_name,"
                    + ', '.join(
                        [
                            ', '.join(
                                [
                                    t + '.' + f + ' as ' + t + '_' + f
                                    for f in [f for f in tables[t] if f and not f.startswith('_')]
                                    + [
                                        s
                                        for s in (
                                            tables[t]['_model']._select
                                            if hasattr(tables[t]['_model'], '_select')
                                            else {}
                                        )
                                        if s not in tables[t]
                                    ]
                                ]
                            )
                            for t in tables
                        ]
                    )
                    + ' '
                    + ' '.join(
                        [
                            (
                                'from'
                                if t2 == primary_table
                                else ('right join' if t2 == t else 'left join')
                            )
                            + ' '
                            + t2
                            + ('' if t2 == primary_table else ' on false')
                            for t2 in tables
                        ]
                    )
                    for t in tables
                ]
            )
        )

        inputclass = type(input)
        inputdict = input.dict()
        filtering = {}
        for f in [
            f
            for f in input.__fields__
            if f in (inputclass._filters if hasattr(inputclass, '_filters') else {})
            and inputdict.get(f)
        ]:
            v = inputdict.get(f)
            filter = inputclass._filters[f]
            filtering[filter[0](v)] = filter[1](v)

        filtering_params = []
        if filtering:
            for p in filtering.values():
                filtering_params = filtering_params + p
            filtering = 'where ' + ' and '.join(filtering.keys())
        else:
            filtering = ''
        query = query.replace("@FILTERING@", filtering)

        ordering = (inputclass._sorts if hasattr(inputclass, '_sorts') else {}).get(
            inputdict.get('sortBy'), ''
        )
        if ordering:
            ordering = ordering + ' ' + inputdict.get('sortOrder', '') + ', '
        query = query.replace("@ORDERING@", ordering)

        query = query.replace("@LANG@", inputdict.get('lang', 'en'))
        query = query.replace("@LANG2@", inputdict.get('lang', 'en').upper().replace('RU', ''))

        query = query.replace('@DBNAME@', CONFIG['DB_NAME'])
        query = query.replace('@PRIMARY_TABLE@', primary_table)

        if 'page' in inputdict and inputdict.get('pageSize', 0):
            query = query.replace(
                '@PAGING@',
                'limit '
                + str(inputdict['pageSize'])
                + ' offset '
                + str(inputdict['pageSize'] * (inputdict['page'] - 1)),
            )
        else:
            query = query.replace('@PAGING@', '')

        params = []
        for m in [
            tables[t]['_model']
            for t in tables
            if hasattr(tables[t]['_model'], '_params') or '@FILTERING@' in tables[t]['_model']._from
        ]:
            for p in m._params if hasattr(m, '_params') else filtering_params:
                params.append(p(inputdict) if callable(p) else p)

        query = query + "\norder by 1"
        return query, params

    def read_query(self, query, params, tables, consume=None, process=None):
        primary_table = list(tables.keys())[0]
        root_model = tables[primary_table]['_root_model']

        root = [] if repr(root_model[1]).startswith('typing.List') else {}
        data = root if isinstance(root, dict) else {}
        lists = {}
        if isinstance(root, list):
            lists[primary_table] = root
        row = None
        re_count = 0

        def handle_row(r):
            nonlocal re_count, process, consume
            if not r:
                return
            if process:
                r = process(r)
            re_count = re_count + 1
            if consume:
                consume(r)

        def row_consumer(r):
            nonlocal data, lists, row
            t = r['table_name']

            if t == primary_table:
                handle_row(row)
                row = data

            queue = [(t, '', (tables[t]['_model'], tables[t]['_outer_type']), data)]
            while len(queue):
                (n, k, m, d) = queue.pop(0)
                m, m_outer_type = m
                if hasattr(m, '_supress') and m._supress:
                    continue

                list_name = m._name if hasattr(m, '_name') else k
                if repr(m_outer_type).startswith('typing.List') and list_name and k:
                    d[k] = []
                    lists[list_name] = d[k]
                    continue
                if not issubclass(m, BaseModel):
                    d[k] = r.get(n)
                    continue
                if k:
                    d[k] = {}
                    d = d[k]
                queue[0:0] = [
                    (
                        '_'.join(filter(None, [n, k])),
                        k,
                        (m.__fields__[k].type_, m.__fields__[k].outer_type_),
                        d,
                    )
                    for k in m.__fields__
                ]
            if tables[t]['_name'] in lists:
                lists[tables[t]['_name']].append(
                    data if issubclass(tables[t]['_model'], BaseModel) else r.get(t + '__value')
                )

            data = {}

        if not hasattr(root_model[0], '_from'):
            tables['_root'] = {'_model': root_model[0], '_outer_type': root_model[1], '_name': None}
            row_consumer({'table_name': '_root'})

        self.fetch_all(query, params, row_consumer)
        handle_row(row)
        if consume:
            return re_count
        return root


def increase_lifespan_common_fixer(r):
    for i in r['interventions']['experiment'] + r['interventions']['controlAndExperiment']:
        i['tissueSpecific'] = i['tissueSpecific'] == 1
    for f in [
        'lMinChangeStatSignificance',
        'lMeanChangeStatSignificance',
        'lMedianChangeStatSignificance',
        'lMaxChangeStatSignificance',
    ]:
        r[f] = {'yes': True, 'да': True, 'no': False, 'нет': False}.get(r[f])
    return r


def gene_common_fixer(r):
    if not r['origin']['id']:
        r['origin'] = None
    if not r['familyOrigin']['id']:
        r['familyOrigin'] = None
    r['aliases'] = [a for a in r['aliases'].split(' ') if a]

    if 'studies' not in r or sum([len(i) for i in r['studies'].values()]) == 0:
        r['studies'] = None
    if not r['studies']:
        return r
    for a in r['studies']['ageRelatedChangesOfGene']:
        a['value'] = str(a['value']) + '%' if a['value'] else a['value']
    for g in r['studies']['geneAssociatedWithLongevityEffects']:
        g['dataType'] = {
            '1en': 'genomic',
            '2en': 'transcriptomic',
            '3en': 'proteomic',
            '1ru': 'геномные',
            '2ru': 'транскриптомные',
            '3ru': 'протеомные',
        }.get(g['dataType'])
    for i in r['studies']['increaseLifespan']:
        i = increase_lifespan_common_fixer(i)

    return r


def age_related_changes_fixer(r):
    r['value'] = str(r['value']) + '%' if r['value'] else r['value']
    r['measurementMethod'] = {'1en': 'mRNA', '2en': 'protein', '1ru': 'мРНК', '2ru': 'белок'}.get(
        r['measurementMethod']
    )
    return r


class GeneDAO(BaseDAO):
    """Gene Table fetcher."""

    def search(self, input):
        GeneSearched.__fields__['studies'].type_._supress = not input.studies == '1'
        # mangle aliases type to string, to manually split it into list in fixer
        GeneSearched.__fields__['aliases'].outer_type_ = str

        tables = self.prepare_tables(GeneSearchOutput)
        query, params = self.prepare_query(tables, input)
        return self.read_query(query, params, tables, process=gene_common_fixer)

    def single(self, input):
        GeneSingle.__fields__['studies'].type_._supress = not input.studies == '1'
        # mangle aliases type to string, to manually split it into list in fixer
        GeneSingle.__fields__['aliases'].outer_type_ = str

        tables = self.prepare_tables(GeneSingle)
        query, params = self.prepare_query(tables, input)
        # print (query,file=open('api/query.sql','w'))

        hpa_fields = [
            'Ensembl',
            'Uniprot',
            'Chromosome',
            'Position',
            'ProteinClass',
            'BiologicalProcess',
            'MolecularFunction',
            'SubcellularLocation',
            'SubcellularMainLocation',
            'SubcellularAdditionalLocation',
            'DiseaseInvolvement',
            'Evidence',
        ]

        def fixer(r):
            nonlocal hpa_fields
            r = gene_common_fixer(r)

            hpa = json.loads(r['humanProteinAtlas'] if r['humanProteinAtlas'] else '{}')
            for f in list(hpa.keys()):
                if f not in hpa_fields:
                    del hpa[f]
            r['humanProteinAtlas'] = hpa

            return r

        re = self.read_query(query, params, tables, process=fixer)
        if not re.get('id'):
            return None

        return re

    def get_duplicates_genes(self):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            '''
            SELECT min(gene.id) AS MAIN_GENE, GROUP_CONCAT(gene.id) AS GENES, COUNT(gene.id) as gid
            FROM gene
            GROUP BY gene.symbol
            HAVING gid > 1
            '''
        )
        return cur.fetchall()

    def change_table(self, tables, duplicates):
        cur = self.cnx.cursor(dictionary=True)
        for table in tables:
            for item in duplicates:
                for gene_id in item['GENES'].split(',')[1::]:
                    cur.execute(
                        f"UPDATE {table} SET gene_id = %(main_gene)s WHERE gene_id = %(gene)s",
                        {"main_gene": item['MAIN_GENE'], "gene": gene_id},
                    )
        self.cnx.commit()
        return True

    def delete_duplicates(self, genes_to_delete):
        cur = self.cnx.cursor(dictionary=True)
        for gene_id in genes_to_delete:
            cur.execute("DELETE gene FROM gene WHERE id = %(gene_id)s", {"gene_id": gene_id})
        self.cnx.commit()
        return True

    def get_source_gene(self, gene_symbol):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            (
                "SELECT s.name FROM "
                "gene JOIN gene_to_source gts on gene.id = gts.gene_id "
                "JOIN source s on gts.source_id = s.id "
                "WHERE gene.symbol = %(gene_symbol)s"
            ),
            {"gene_symbol": gene_symbol},
        )
        return cur.fetchone()

    def get_origin_for_gene(self, phylum_id):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM phylum WHERE phylum.id = %(phylum_id)s;", {'phylum_id': phylum_id}
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
        cur.execute("SELECT * FROM `gene` WHERE symbol=%(gene)s;", {"gene": gene})
        result = cur.fetchone()
        return result

    def get_by_hugo_id(
        self,
        hugo_id: str,
    ):
        """
        HGNC:4263
        """
        hugo_id = hugo_id.upper()
        hugo_id = hugo_id if hugo_id.startswith('HGNC:') else f'HGNC:{hugo_id}'

        cur = self.cnx.cursor(dictionary=True)
        cur.execute("SELECT * FROM `gene` WHERE hgnc_id=%(hugo_id)s;", {"hugo_id": hugo_id})
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

    def update(
        self,
        gene: entities.Gene,
    ) -> entities.Gene:
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

    def get_list(self, request):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute('SET SESSION group_concat_max_len = 100000;')
        cur.execute(request)
        return cur.fetchall()

    def get_symbols(self):
        cur = self.cnx.cursor()
        cur.execute('SELECT JSON_ARRAYAGG(g.symbol) FROM gene g WHERE g.isHidden != 1;')
        return cur.fetchone()


class StudiesDAO(BaseDAO):
    def increase_lifespan_search(self, input):
        IncreaseLifespanSearched.__fields__['geneAliases'].outer_type_ = str

        tables = self.prepare_tables(IncreaseLifespanSearchOutput)
        query, params = self.prepare_query(tables, input)

        def fixer(r):
            r['geneAliases'] = [a for a in r['geneAliases'].split(' ') if a]
            return increase_lifespan_common_fixer(r)

        return self.read_query(query, params, tables, process=fixer)

    def age_related_changes(self, input):
        AgeRelatedChangeOfGeneResearched.__fields__['geneAliases'].outer_type_ = str

        tables = self.prepare_tables(AgeRelatedChangeOfGeneResearchOutput)
        query, params = self.prepare_query(tables, input)

        def fixer(r):
            r['geneAliases'] = [a for a in r['geneAliases'].split(' ') if a]
            return age_related_changes_fixer(r)

        return self.read_query(query, params, tables, process=fixer)

    def gene_activity_change_impact(self, input):
        GeneActivityChangeImpactResearched.__fields__['geneAliases'].outer_type_ = str

        tables = self.prepare_tables(GeneActivityChangeImpactResearchedOutput)
        query, params = self.prepare_query(tables, input)

        def fixer(r):
            r['geneAliases'] = [a for a in r['geneAliases'].split(' ') if a]
            return r

        return self.read_query(query, params, tables, process=fixer)

    def gene_regulation(self, input):
        GeneRegulationResearched.__fields__['geneAliases'].outer_type_ = str

        tables = self.prepare_tables(GeneRegulationResearchedOutput)
        query, params = self.prepare_query(tables, input)

        def fixer(r):
            r['geneAliases'] = [a for a in r['geneAliases'].split(' ') if a]
            return r

        return self.read_query(query, params, tables, process=fixer)

    def association_with_accelerated_aging(self, input):
        AssociationWithAcceleratedAgingResearched.__fields__['geneAliases'].outer_type_ = str

        tables = self.prepare_tables(AssociationWithAcceleratedAgingResearchedOutput)
        query, params = self.prepare_query(tables, input)

        def fixer(r):
            r['geneAliases'] = [a for a in r['geneAliases'].split(' ') if a]
            return r

        return self.read_query(query, params, tables, process=fixer)

    def other_evidence(self, input):
        OtherEvidenceResearched.__fields__['geneAliases'].outer_type_ = str

        tables = self.prepare_tables(OtherEvidenceResearchedOutput)
        query, params = self.prepare_query(tables, input)

        def fixer(r):
            r['geneAliases'] = [a for a in r['geneAliases'].split(' ') if a]
            return r

        return self.read_query(query, params, tables, process=fixer)

    def associations_with_lifespan(self, input):
        AssociationsWithLifespanResearched.__fields__['geneAliases'].outer_type_ = str

        tables = self.prepare_tables(AssociationsWithLifespanResearchedOutput)
        query, params = self.prepare_query(tables, input)

        def fixer(r):
            r['geneAliases'] = [a for a in r['geneAliases'].split(' ') if a]
            return r

        return self.read_query(query, params, tables, process=fixer)


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
            FROM functional_cluster'''.format(
                lang
            )
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
            FROM aging_mechanism'''.format(
                lang
            )
        )
        return cur.fetchall()


class SourceDAO(BaseDAO):
    def get_source(self, source: entities.Source):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute("SELECT source.id FROM source WHERE name='{}'".format(source.name))
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
            FROM comment_cause'''.format(
                lang
            )
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

    def update(
        self,
        disease: entities.Disease,
    ) -> entities.Disease:
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

    def search(self, input: str, suggestHidden: int):
        is_hidden_filter = "AND isHidden = %(suggestHidden)s" if suggestHidden == 0 else ""
        terms = [
            term
            for term in [[w for w in t.strip().split(' ') if w] for t in input.split(',') if t]
            if term
        ]
        re = {'items': [], 'found': [], 'notFound': terms}
        parameters = {i: f"%{i}%" for i in chain(*terms)}

        if not terms:
            return re

        # where's block
        term_checks = []
        for term in terms:
            word_checks = []
            for word in term:
                word_checks.append(suggestion_request_builder.build(f"%({word})s"))
            term_checks.append(" AND ".join("(" + b + ")" for b in word_checks))
        where_block = " OR ".join("(" + t + ")" for t in term_checks)

        # names block
        names_block = ",".join(suggestion_request_builder.get_names())

        # found/notFound block
        def consume_row(r):
            nonlocal re, terms
            re['items'].append(r)
            for term in terms:
                f = True
                for w in term:
                    f = (
                        f
                        and len(
                            [
                                v
                                for v in r.values()
                                if (w.lower() in v.lower() if isinstance(v, str) else w == v)
                            ]
                        )
                        > 0
                    )

                if f and term in re['notFound']:
                    re['found'].append(' '.join(term))
                    re['notFound'] = [t for t in re['notFound'] if t != term]

        # sql block
        sql = f"SELECT {names_block},isHidden FROM gene WHERE {where_block} {is_hidden_filter};"
        self.fetch_all(sql, {**parameters, "suggestHidden": suggestHidden}, consume_row)

        re['notFound'] = [' '.join(t) for t in re['notFound']]
        return re

    def search_by_genes_id(self, byGeneId: str, suggestHidden: int):
        is_hidden_filter = "AND isHidden = %s" if suggestHidden == 0 else ""
        idls = [i.strip() for i in byGeneId.split(',') if i.strip().isdigit()]
        re = {'items': [], 'found': [], 'notFound': idls}
        if not idls:
            return re

        # names block
        names_block = ",".join(suggestion_request_builder.get_names())

        # found/notFound block
        def consume_row(r):
            nonlocal re, idls
            re['items'].append(r)
            for gid in idls:
                f = gid == str(r['id'])

                if f and gid in re['notFound']:
                    re['found'].append(gid)
                    re['notFound'] = [t for t in re['notFound'] if t != gid]

        # sql block
        idls_tuple = tuple(idls)
        idls_params = ','.join(["%s" for i in range(len(idls))])
        sql = f"SELECT {names_block},isHidden FROM gene WHERE id IN ({idls_params}) {is_hidden_filter};"
        parameters = (*idls_tuple, suggestHidden) if is_hidden_filter else idls_tuple
        self.fetch_all(sql, parameters, consume_row)
        return re

    def search_by_genes_symbol(self, byGeneSmb: str, suggestHidden: int):
        is_hidden_filter = "AND isHidden = %s" if suggestHidden == 0 else ""
        symbols = [i.strip().upper() for i in byGeneSmb.split(',')]
        re = {'items': [], 'found': [], 'notFound': symbols}
        if not symbols:
            return re

        # names block
        names_block = ",".join(suggestion_request_builder.get_names())

        # found/notFound block
        def consume_row(r):
            nonlocal re, symbols
            re['items'].append(r)
            for gid in symbols:
                f = gid == r['symbol']

                if f and gid in re['notFound']:
                    re['found'].append(gid)
                    re['notFound'] = [t for t in re['notFound'] if t != gid]

        # sql block
        symbols_tuple = tuple(symbols)
        symbols_params = ','.join(["%s" for i in range(len(symbols))])
        sql = f"SELECT {names_block},isHidden FROM gene WHERE symbol IN ({symbols_params}) {is_hidden_filter};"
        parameters = (*symbols_tuple, suggestHidden) if is_hidden_filter else symbols_tuple
        self.fetch_all(sql, parameters, consume_row)
        return re


class ProteinClassDAO(BaseDAO):
    def get_all(self, lang):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute('SET SESSION group_concat_max_len = 100000;')
        cur.execute(
            '''
            SELECT CAST(CONCAT('[', GROUP_CONCAT( distinct JSON_OBJECT(
            'id', protein_class.id,
            'name', protein_class.name_{}
            ) separator ","), ']') AS JSON) AS jsonobj
            FROM protein_class'''.format(
                lang
            )
        )
        return cur.fetchall()


class PhylumDAO(BaseDAO):
    def get_all(self):
        cur = self.cnx.cursor(dictionary=True)
        cur.execute('SET SESSION group_concat_max_len = 100000;')
        cur.execute(
            '''
            SELECT CAST(CONCAT('[', GROUP_CONCAT( distinct JSON_OBJECT(
            'id', phylum.id,
            'name', phylum.name_phylo,
            'age', phylum.name_mya,
            'order', phylum.`order`
            ) separator ","), ']') AS JSON) AS jsonobj
            FROM phylum'''
        )
        return cur.fetchall()


class CalorieExperimentDAO(BaseDAO):
    """Calorie experiment Table fetcher."""

    def calorie_experiment_search(self, input):

        tables = self.prepare_tables(CalorieExperimentOutput)
        query, params = self.prepare_query(tables, input)

        return self.read_query(query, params, tables)


class WorkerStateDAO(BaseDAO):
    """Worker state Table fetcher."""

    def __init__(self, name: str, default_state: str):
        super(WorkerStateDAO, self).__init__()
        self.name = name
        self.start_state = default_state

    def get(self) -> str:
        cur = self.cnx.cursor(dictionary=True, buffered=True)
        cur.execute("SELECT state FROM worker_state WHERE name = %(name)s", {"name": self.name})
        wstate = cur.fetchone()
        cur.close()
        if wstate is None:
            self.set(self.start_state)
            return self.start_state
        else:
            return wstate['state']

    def set(self, st: str):
        cur = self.cnx.cursor(dictionary=True, buffered=True)
        cur.execute(
            (
                "INSERT INTO worker_state(name,state) "
                "VALUES (%(name)s,%(st)s) ON DUPLICATE KEY UPDATE state=%(st)s;"
            ),
            {"name": self.name, "st": st},
        )
        self.cnx.commit()
        cur.close()


class GeneGroupDAO(BaseDAO):
    """GeneGroup Table fetcher."""

    cash = {}

    def get_id(self, name: str) -> int:
        ggid = self.cash.get(name)
        if ggid is None:
            cur = self.cnx.cursor(dictionary=True, buffered=True)
            cur.execute("SELECT id FROM gene_group WHERE name = %(name)s;", {"name": name})
            ggid = cur.fetchone()
            if ggid is None:
                cur.execute("INSERT INTO gene_group(name) VALUES (%(name)s);", {"name": name})
                self.cnx.commit()
                ggid = cur.lastrowid
            else:
                ggid = ggid['id']
            self.cash[name] = ggid
            cur.close()
        return ggid


class LocuGroupDAO(BaseDAO):
    """GeneLocusGroup Table fetcher."""

    cash = {}

    def get_id(self, name: str) -> int:
        lgid = self.cash.get(name)
        if lgid is None:
            cur = self.cnx.cursor(dictionary=True, buffered=True)
            cur.execute("SELECT id FROM gene_locus_group WHERE name = '%(name)s';", {"name": name})
            lgid = cur.fetchone()

            if lgid is None:
                cur.execute(
                    "INSERT INTO gene_locus_group(name) VALUES (%(name)s);", {"name": name}
                )
                self.cnx.commit()
                lgid = cur.lastrowid
            else:
                lgid = lgid['id']

            self.cash[name] = lgid
            cur.close()
        return lgid


class GeneTranscriptDAO(BaseDAO):
    """Gene Transcript Table fetcher."""

    def add(self, tr: entities.GeneTranscript) -> int:
        source_dict = tr.dict(exclude_none=True)

        query = f"INSERT INTO gene_transcript ({', '.join(source_dict.keys())}) "
        subs = ', '.join([f'%({k})s' for k in source_dict.keys()])
        query += f"VALUES ({subs});"

        cur = self.cnx.cursor(dictionary=True, buffered=True)
        cur.execute(query, source_dict)
        self.cnx.commit()
        cur.close()
        return cur.lastrowid


class GeneTranscriptExonDAO(BaseDAO):
    """Gene Transcript Exon Table fetcher."""

    def add(self, ex: entities.GeneTranscriptExon) -> int:
        source_dict = ex.dict(exclude_none=True)

        query = f"INSERT INTO transcript_exon ({', '.join(source_dict.keys())}) "
        subs = ', '.join([f'%({k})s' for k in source_dict.keys()])
        query += f"VALUES ({subs});"

        cur = self.cnx.cursor(dictionary=True, buffered=True)
        cur.execute(query, source_dict)
        self.cnx.commit()
        cur.close()
        return cur.lastrowid


class ModelOrganismDAO(BaseDAO):
    def list(self, input):
        tables = self.prepare_tables(ModelOrganismOutput)
        query, params = self.prepare_query(tables, input)

        re = self.read_query(query, params, tables)

        return re


class OrthologDAO(BaseDAO):
    def get_id(self, symbol: str, model_organism: str, external_base_name: str, external_id: str):
        cur = self.cnx.cursor(dictionary=True, buffered=True)
        cur.execute(
            "SELECT o.id FROM ortholog o WHERE o.symbol = %(symbol)s AND o.external_base_name = %(external_base_name)s;",
            {"symbol": symbol, "external_base_name": external_base_name},
        )
        orth_id = cur.fetchone()

        if orth_id is None:
            ireq = (
                "INSERT INTO ortholog(symbol, model_organism_id, external_base_name, external_base_id) "
                "VALUES (%(symbol)s, (SELECT id FROM model_organism "
                "WHERE name_lat = %(model_organism)s), %(external_base_name)s, %(external_id)s) ;",
                {
                    "symbol": symbol,
                    "model_organism": model_organism,
                    "external_base_name": external_base_name,
                    "external_id": external_id,
                },
            )
            cur.execute(ireq)
            self.cnx.commit()
            orth_id = cur.lastrowid
        else:
            orth_id = orth_id['id']

        cur.close()
        return orth_id

    def link_gene(self, gene_id: int, ortholog_id: int):
        cur = self.cnx.cursor(dictionary=True, buffered=True)
        cur.execute(
            "SELECT id FROM gene_to_ortholog WHERE gene_id = %(gene_id)s AND ortholog_id = %(ortholog_id)s;",
            {"gene_id": gene_id, "ortholog_id": ortholog_id},
        )
        gto = cur.fetchone()

        if gto is None:
            cur.execute(
                "INSERT INTO gene_to_ortholog(gene_id, ortholog_id) VALUES (%(gene_id)s,%(ortholog_id)s);",
                {"gene_id": gene_id, "ortholog_id": ortholog_id},
            )
            self.cnx.commit()

        cur.close()

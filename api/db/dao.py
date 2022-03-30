from mysql import connector

from config import CONFIG
from entities import entities
from pydantic import BaseModel

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

    def prepare_tables(self,model):
            tables={}
            queue=[('','',model,tables,None)]
            while len(queue):
                (n,k,m,t,p)=queue.pop(0)
                if hasattr(m,'_supress') and m._supress: continue
                if not issubclass(m,BaseModel):
                    t[n]=p._select.get(k,k) if hasattr(p,'_select') else k
                    continue
                if hasattr(m,'_from'):
                    t={'_model':m,'_name':m._name if hasattr(m,'_name') else k,'_parent':t.get('_name'),'_from':m._from,'_join':''}
                    tables[t['_name']]=t
                    n=''
                if hasattr(m,'_join'):
                    t['_join']=(t['_join']+"\n"+m._join).strip()
                queue[0:0]=[((n+'_'+k).strip('_'),k,m.__fields__[k].type_,t,m) for  k in m.__fields__]

            return tables

    def prepare_query(self,tables,input):
        primary_table=list(tables.keys())[0]
        for table in [tables[t] for t in tables if '@JOINS@' not in tables[t]['_from']]: table['_from']=table['_from'].strip()+"\n@JOINS@\n"
        query="with "+",\n".join([t+' as ( select concat('+((tables[t]['_parent']+'.ordering, ') if tables[t]['_parent'] else '')+"lpad(row_number() over(),5,'0')) as ordering"+(', count(*) over() as row_count' if t==primary_table else '')+', '+', '.join([tables[t][f]+' as "'+f+'"' for f in tables[t].keys() if not f.startswith('_')]+[tables[t]['_model']._select[s]+' as "'+s+'"' for s in tables[t]['_model']._select if s not in tables[t]])+'\n'+tables[t]['_from'].lstrip().replace('@JOINS@',tables[t].get('_join',''))+')' for t in tables])
        query=query+"\n"+"\nunion ".join(['select '+t+'.ordering, '+(t+'.row_count' if t==primary_table else 'null')+" as row_count, '"+str(tables[t]['_name'])+"' as table_name,"+', '.join([', '.join([t+'.'+f+' as '+t+'_'+f for f in [f for f in tables[t] if not f.startswith('_')]+[s for s  in tables[t]['_model']._select if s not in tables[t]]]) for t in tables])+' '+' '.join([('from'if t2==primary_table else ('right join' if t2==t else 'left join'))+' '+t2+('' if t2==primary_table else ' on false') for t2 in tables]) for t in tables])

        inputclass=type(input)
        inputdict=input.dict()
        filtering={}
        for f in [f for f in input.__fields__ if f in inputclass._filters and inputdict.get(f)]:
            v=inputdict.get(f)
            filter=inputclass._filters[f]
            filtering[filter[0](v)]=filter[1](v)

        params=[]
        if filtering:
            for p in filtering.values(): params=params+p
            filtering='where '+' and '.join(filtering.keys())
        else:
            filtering=''
        query=query.replace("@FILTERING@",filtering)

        ordering=inputclass._sorts.get(inputdict.get('sortBy'),'')
        if ordering: ordering=ordering+' '+inputdict.get('sortOrder','')+', '
        query=query.replace("@ORDERING@",ordering)

        query=query.replace("@LANG@",inputdict.get('lang','en'))
        query=query.replace("@LANG2@",inputdict.get('lang','en').upper().replace('RU',''))

        meta={}
        if 'page' in inputdict and 'pageSize' in inputdict:
            meta['page']=inputdict.get('page')
            meta['page']=int(meta['page']) if meta['page'] is not None else 1
            meta['pageSize']=inputdict.get('pageSize')
            meta['pageSize']=int(meta['pageSize']) if meta['pageSize'] is not None else 10
            query=query.replace('@PAGING@','limit '+str(meta['pageSize'])+' offset '+str(meta['pageSize']*(meta['page']-1)));

        query=query+"\norder by 1"

        return query,params,meta

    def read_query(self,query,params,tables,consume=None,process=None):

        primary_table=list(tables.keys())[0]

        re=[]
        row=None
        row_count=None
        re_count=0
        lists={}

        def handle_row(r):
            nonlocal re,re_count,process,consume
            if not r: return
            if 'row_count' in r:
                if consume:
                    consume(r)
                else:
                    re.append(r)
                return
            if process: r=process(r)
            re_count=re_count+1
            if consume:
                consume(r)
                return
            re.append(r)

        def row_consumer(r):
            nonlocal row,lists,row_count
            t=r['table_name']
            if r['row_count'] is not None and row_count is None:
                row_count=r['row_count']
                handle_row({'row_count':row_count}|({'total_count':r[t+'_total_count']} if t+'_total_count' in r else {}))

            if t==primary_table:
                handle_row(row)
                row={}
                data=row
                lists={}
            else:
                data={}

            m_outer_type=None
            queue=[(t,'',tables[t]['_model'],data)]
            while len(queue):
                (n,k,m,d)=queue.pop(0)
                if hasattr(m,'_supress') and m._supress: continue

                if isinstance(m,tuple):
                    m_outer_type=m[1]
                    m=m[0]
                if repr(m_outer_type).startswith('typing.List'):
                    d[k]=[]
                    lists[m._name if hasattr(m,'_name') else k]=d[k]
                    continue
                if not issubclass(m,BaseModel):
                    d[k]=r.get(n)
                    continue
                if k:
                    d[k]={}
                    d=d[k]
                queue[0:0]=[((n+'_'+k).strip('_'),k,(m.__fields__[k].type_,m.__fields__[k].outer_type_),d) for k in m.__fields__]
            if tables[t]['_name'] in lists: lists[tables[t]['_name']].append(data)

        self.fetch_all(query,params,row_consumer)
        handle_row (row)
        if row_count is None: handle_row({'row_count':0})
        if consume: re=re_count
        return re


from models.gene import GeneSearched,GeneSearchOutput,GeneSingle
import json

def gene_common_fixer(r):
    if not r['origin']['id']:r['origin']=None
    if not r['familyOrigin']['id']: r['familyOrigin']=None
    r['aliases']=[a for a in r['aliases'].split(' ') if a]

    if not r['researches']: return r
    for a in r['researches']['ageRelatedChangesOfGene']:
        for f in ['valueForAll','valueForFemale','valueForMale']: a[f]=str(a[f])+'%' if a[f] else a[f]
        a['measurementType']={'1en':'mRNA','2en':'protein','1ru':'мРНК','2ru':'белок'}.get(a['measurementType'])
    for g in r['researches']['geneAssociatedWithLongevityEffects']:
        g['dataType']={'1en':'genomic','2en':'transcriptomic','3en':'proteomic','1ru':'геномные','2ru':'транскриптомные','3ru':'протеомные'}.get(g['dataType'])
        g['sex']={'9en':'female','1en':'male','2en':'both','0ru':'женский','1ru':'мужской','2ru':'оба пола'}.get(g['sex'])
    for g in r['researches']['increaseLifespan']:
        for i in g['interventions']['experiment']+g['interventions']['controlAndExperiment']:
            i['tissueSpecific']=i['tissueSpecific']==1
            i['tissueSpecificPromoter']=i['tissueSpecificPromoter']==1
            if not i['tissueSpecific']: i['tissueSpecificPromoter']=None
        for f in ['lMinChangeStatSignificance', 'lMeanChangeStatSignificance', 'lMedianChangeStatSignificance', 'lMaxChangeStatSignificance']:
            g[f]={'yes':True,'да':True,'no':False,'нет':False}.get(g[f])

    return r


class GeneDAO(BaseDAO):
    """Gene Table fetcher."""
    def search(self,input):
        GeneSearched.__fields__['researches'].type_._supress= not input.researches=='1'
        # mangle aliases type to string, to manually split it into list in fixer
        GeneSearched.__fields__['aliases'].outer_type_=str

        tables=self.prepare_tables(GeneSearched)
        query,params,meta=self.prepare_query(tables,input)

        re=self.read_query(query,params,tables,process=gene_common_fixer)

        meta.update(re.pop(0))

        return {'options':{'objTotal':meta['row_count'],'total':meta['total_count'],"pagination":{"page":meta['page'],"pageSize":meta['pageSize'],"pagesTotal":meta['row_count']//meta['pageSize'] + (meta['row_count']%meta['pageSize']!=0)}},'items':re}

    def single(self,input):
        GeneSingle.__fields__['researches'].type_._supress= not input.researches=='1'
        # mangle aliases type to string, to manually split it into list in fixer
        GeneSingle.__fields__['aliases'].outer_type_=str
        GeneSingle.__fields__['source'].outer_type_=str

        tables=self.prepare_tables(GeneSingle)
        query,params,meta=self.prepare_query(tables,input)

        hpa_fields=[ 'Ensembl', 'Uniprot', 'Chromosome', 'Position', 'ProteinClass', 'BiologicalProcess', 'MolecularFunction', 'SubcellularLocation', 'SubcellularMainLocation', 'SubcellularAdditionalLocation', 'DiseaseInvolvement', 'Evidence', ]

        def fixer(r):
            nonlocal hpa_fields
            r=gene_common_fixer(r);

            r['source']=[s for s in r['source'].split('||') if s]
            terms={}
            for t in r['terms'].split('||'):
                t=t.split('|')
                if len(t)!=3: continue
                identifier,name,category=t
                if category not in terms: terms[category]=[]
                terms[category].append({identifier:name})
            r['terms']=terms

            hpa=json.loads(r['humanProteinAtlas'])
            for f in list(hpa.keys()):
                if f not in hpa_fields: del hpa[f]
            r['humanProteinAtlas']=hpa

            return r

        re=self.read_query(query,params,tables,process=fixer)
        if len(re)!=2: return None

        return re[1]

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

from models.gene import IncreaseLifespanSearched,IncreaseLifespanSearchOutput

class ResearchesDAO(BaseDAO):
    def increase_lifespan_search(self,input):
        IncreaseLifespanSearched.__fields__['geneAliases'].outer_type_=str

        tables=self.prepare_tables(IncreaseLifespanSearched)
        query,params,meta=self.prepare_query(tables,input)

        def fixer(r):
            r['geneAliases']=[a for a in r['geneAliases'].split(' ') if a]
            return r

        re=self.read_query(query,params,tables,process=fixer)

        meta.update(re.pop(0))

        return {'options':{'objTotal':meta['row_count'],'total':meta.get('total_count'),"pagination":{"page":meta['page'],"pageSize":meta['pageSize'],"pagesTotal":meta['row_count']//meta['pageSize'] + (meta['row_count']%meta['pageSize']!=0)}},'items':re}

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

                if f and term in re['notFound']:
                    re['found'].append(' '.join(term))
                    re['notFound']=[t for t in re['notFound'] if t!=term]
        # sql block
        sql = f"SELECT {names_block} FROM gene WHERE {where_block} AND isHidden=0;"
        self.fetch_all(sql,{},consume_row)

        re['notFound']=[' '.join(t) for t in re['notFound']]
        return re

    def search_by_genes_id(self, byGeneId:str):
        idls = [i.strip() for i in byGeneId.split(',') if i.strip().isdigit()]
        re={'items':[],'found':[],'notFound':idls}
        if not idls: return re

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
                    re['notFound']=[t for t in re['notFound'] if t!=gid]

        # sql block
        idls_str = ','.join([str(i) for i in idls])
        sql = f"SELECT {names_block} FROM gene WHERE id IN ({idls_str}) AND isHidden=0;"
        self.fetch_all(sql, {}, consume_row)

        return re

    def search_by_genes_symbol(self, byGeneSmb:str):
        symbols = [i.strip().upper() for i in byGeneSmb.split(',')]
        re={'items':[],'found':[],'notFound':symbols}
        if not symbols: return re

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
                    re['notFound']=[t for t in re['notFound'] if t!=gid]

        # sql block
        idls_str = ','.join([f"'{i}'" for i in symbols])
        sql = f"SELECT {names_block} FROM gene WHERE symbol IN ({idls_str}) AND isHidden=0;"
        self.fetch_all(sql, {}, consume_row)

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
            FROM protein_class'''.format(lang)
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

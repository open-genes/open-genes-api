import json

import requests
from db import dao
from entities import entities
from ncbi.datasets.openapi import ApiClient as DatasetsApiClient
from ncbi.datasets.openapi import ApiException as DatasetsApiException
from ncbi.datasets.openapi.api.gene_api import GeneApi as DatasetsGeneApi


class GeneLocationFetcherNCBI:
    def __init__(self, symbol: str):
        self.gene = symbol
        self.taxon = 'human'

    def exec(self):
        with DatasetsApiClient() as api_client:
            gene_api = DatasetsGeneApi(api_client)
            try:
                gene_reply = gene_api.gene_metadata_by_tax_and_symbol([self.gene], self.taxon)
                if len(gene_reply.genes) > 0:
                    result = gene_reply.genes[0].gene.to_dict()
                    return result
            except DatasetsApiException as e:
                print(f'Exception when calling GeneApi: {e}\n')


class GeneFetcherHUGO:
    def __init__(self, symbol: str):
        self.gene = symbol

    def exec(self) -> dict:
        response_raw = requests.get(
            f'http://rest.genenames.org/fetch/symbol/{self.gene}',
            headers={'Accept': 'application/json'},
        )

        if response_raw.status_code != 200:
            raise Exception(response_raw.status_code)

        response_json = response_raw.json()
        response = response_json.get('response')
        if response is None:
            raise Exception('response is null')
        return response


class Worker:
    name = 'gene_local'
    def_state = '0'

    def __init__(self):
        self.state_dao = dao.WorkerStateDAO(self.name, self.def_state)
        self.gene_dao = dao.GeneDAO()
        self.gene_group_dao = dao.GeneGroupDAO()
        self.locus_group_dao = dao.LocuGroupDAO()
        self.trans_dao = dao.GeneTranscriptDAO()
        self.trans_exon_dao = dao.GeneTranscriptExonDAO()

    def handle_gene(self, symbol: str, gid: int):
        print(f"symbol {symbol}...")

        # ncbi
        try:
            self.ncbi_fetcher = GeneLocationFetcherNCBI(symbol)
            ncbi_result = self.ncbi_fetcher.exec()
        except Exception as e:
            print(f" GENE: {symbol} ERROR: {type(e)} {str(e)}")
            return

        print(ncbi_result)
        genomic_ranges = ncbi_result['genomic_ranges']
        if len(genomic_ranges) > 0:
            first_genomic_range = genomic_ranges[0]
            range = first_genomic_range['range']
            if len(range) > 0:
                first_range = range[0]
                loc_start = first_range['begin']
                loc_end = first_range['end']
                # orientation
                loc_orient = first_range['orientation']
                loc_orient_int = 1
                if loc_orient == 'minus':
                    loc_orient_int = -1
                # acc orf
                loc_acc_orf = first_range.get('accOrf')
                if not loc_acc_orf:
                    loc_acc_orf = ''
                # acc cds
                loc_acc_cds = first_range.get('accCds')
                if not loc_acc_cds:
                    loc_acc_cds = ''
            else:
                return

            # transcripts
            gene_transcript_raw = ncbi_result.get('transcripts')
            if gene_transcript_raw is not None and len(gene_transcript_raw) > 0:
                for gene_transcript in gene_transcript_raw:
                    tr_obj = entities.GeneTranscript()
                    tr_obj.gene_id = gid
                    #
                    tr_obj.acc_version = gene_transcript.get('accession_version') or ''
                    #
                    tr_obj.name = gene_transcript.get('name') or ''
                    #
                    tr_obj.length = gene_transcript.get('length') or 0
                    #
                    genomic_rng = gene_transcript.get('genomic_range')
                    tr_obj.genomic_range_acc_version = ''
                    if genomic_rng:
                        #
                        tr_obj.genomic_range_acc_version = (
                            genomic_rng.get('accession_version') or ''
                        )
                        #
                        range_genomic_rng = genomic_rng.get('range')
                        if range_genomic_rng and len(range_genomic_rng) > 0:
                            range_genomic_rng = range_genomic_rng[0]
                            tr_obj.genomic_range_begin = range_genomic_rng.get('begin')
                            #
                            tr_obj.genomic_range_end = range_genomic_rng.get('end')
                            #
                            tr_obj.genomic_range_orientation = (
                                -1 if range_genomic_rng.get('orientation') == 'minus' else 1
                            )

                    tr_id = self.trans_dao.add(tr_obj)

                    #
                    if tr_id is not None:
                        # exons
                        exons_raw = gene_transcript.get('exons')
                        if exons_raw:
                            exons = exons_raw.get('range')
                            if exons:
                                for exon in exons:
                                    ex_obj = entities.GeneTranscriptExon()
                                    ex_obj.transcript_id = tr_id
                                    #
                                    ex_obj.begin = exon.get('begin') or 0
                                    #
                                    ex_obj.end = exon.get('end') or 0
                                    #
                                    ex_obj.ord = exon.get('order') or 0
                                    #
                                    self.trans_exon_dao.add(ex_obj)

                # hugo
                hgnc_id = ''
                gene_group_id = 0
                gene_locus_group_id = 0
                hugo_location = ''

                fetcher_hugo = GeneFetcherHUGO(symbol)
                try:
                    self.hugo_fetcher = GeneFetcherHUGO(symbol)
                    hugo_resp = fetcher_hugo.exec()
                    if hugo_resp is not None:
                        hugo_docs = hugo_resp.get('docs')
                        if hugo_docs is not None and len(hugo_docs) > 0:
                            hugo_docs = hugo_docs[0]
                            # print(hugo_docs)
                            #
                            hgnc_id = hugo_docs['hgnc_id']

                            # gene group
                            gene_group = hugo_docs.get('gene_group')
                            if gene_group is not None:
                                if len(gene_group) > 0:
                                    gene_group = gene_group[0]
                                    gene_group_id = self.gene_group_dao.get_id(gene_group)
                                    print("gene group:", gene_group_id)

                            # locus group
                            locus_group = hugo_docs.get('locus_group')
                            if locus_group is not None:
                                if locus_group != '':
                                    gene_locus_group_id = self.locus_group_dao.get_id(locus_group)
                                    print("locus group:", gene_locus_group_id)

                            # location
                            hugo_location = hugo_docs['location']

                            # acc orf
                            loc_acc_orf_ls = hugo_docs['refseq_accession']
                            if loc_acc_orf_ls:
                                loc_acc_orf = loc_acc_orf_ls[0]

                except Exception as e:
                    print(f" GENE: {symbol} ERROR: {type(e)} {str(e)}")

                # update gene
                self.update_gene(
                    gid,
                    loc_start,
                    loc_end,
                    loc_orient_int,
                    hgnc_id,
                    gene_group_id,
                    gene_locus_group_id,
                    hugo_location,
                    loc_acc_orf,
                    loc_acc_cds,
                )

                # set state
                self.state_dao.set(str(gid))

    def update_gene(
        self,
        id: int,
        loc_start,
        loc_end,
        loc_orient,
        hgnc_id,
        gene_group_id,
        gene_locus_group_id,
        location,
        loc_acc_orf,
        loc_acc_cds,
    ):
        chstr = ''
        for l in location:
            if l.isdigit():
                chstr += l
            else:
                break
        try:
            chromosome_num = int(chstr)
        except:
            chromosome_num = 'NULL'
        print('chromosome:', chromosome_num)
        #
        gene_group_id = gene_group_id or 'NULL'
        #
        gene_locus_group_id = gene_locus_group_id or 'NULL'

        #
        cur = self.gene_dao.cnx.cursor(dictionary=True, buffered=True)
        sql = f'''
        UPDATE gene 
        SET locationStart={loc_start},locationEnd={loc_end},orientation={loc_orient},hgnc_id='{hgnc_id}',
        gene_group={gene_group_id},locus_group={gene_locus_group_id},band='{location}',chromosome={chromosome_num},
        accOrf='{loc_acc_orf}'
        WHERE id = {id};'''
        cur.execute(sql)
        self.gene_dao.cnx.commit()

    def get_care_list(self):
        current_state = self.state_dao.get()
        if not current_state.isdigit():
            raise Exception("current state is not digit")
        sql = f"SELECT g.id,g.symbol FROM gene g WHERE g.id > {current_state} ORDER BY g.id;"
        return self.gene_dao.get_list(request=sql)


if __name__ == '__main__':
    w = Worker()
    ls = w.get_care_list()
    for gene_obj in ls:
        gid = gene_obj['id']
        symbol = gene_obj['symbol']
        w.handle_gene(symbol, gid)

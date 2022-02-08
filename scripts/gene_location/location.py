from ncbi.datasets.openapi import ApiClient as DatasetsApiClient
from ncbi.datasets.openapi import ApiException as DatasetsApiException
from ncbi.datasets.openapi.api.gene_api import GeneApi as DatasetsGeneApi


# "location": {
#   accCds: "NP_000034",
#   accOrf: "NM_000043",
#   accPromoter: null,
#   band "10q24.1"
# }
class GeneLocationFetcher():
    def __init__(self, symbol: str, taxon: str):
        self.gene = symbol
        self.taxon = taxon
        # location
        self.acc_cds = None
        self.acc_orf = None
        self.acc_prom = None
        self.acc_band = None
        self.loc_start = None
        self.loc_end = None
        self.loc_orient = None

    def _ncbi_exec(self):
        with DatasetsApiClient() as api_client:
            gene_api = DatasetsGeneApi(api_client)
            try:
                gene_reply = gene_api.gene_metadata_by_tax_and_symbol([self.gene], self.taxon)
                if len(gene_reply.genes) > 0:
                    result = gene_reply.genes[0].gene.to_dict()
                    self._ncbi_handler(result)
            except DatasetsApiException as e:
                print(f'Exception when calling GeneApi: {e}\n')

    def _ncbi_handler(self, ans: dict):
        genomic_ranges = ans['genomic_ranges']
        if len(genomic_ranges) > 0:
            first_genomic_range = genomic_ranges[0]
            #
            range = first_genomic_range['range']
            if len(range) > 0:
                first_range = range[0]
                self.loc_start = first_range['begin']
                self.loc_end = first_range['end']
                self.loc_orient = first_range['orientation']

    def get_acc_cds(self):
        pass

    def get_acc_orf(self):
        pass

    def get_acc_promoter(self):
        pass

    def get_band(self):
        pass

    def get_loc_start(self):
        if self.loc_start is None:
            self._ncbi_exec()
        return self.loc_start

    def get_loc_end(self):
        if self.loc_end is None:
            self._ncbi_exec()
        return self.loc_end


if __name__ == '__main__':
    fetcher = GeneLocationFetcher('IRC1', 'human')
    print(fetcher.get_loc_start())

import requests

human_type = 'Homo sapiens'
fly_type = 'Drosophila melanogaster'
source_file_c_elegance_name = 'Caenorhabditis elegans'


class WormBaseOrtholog:
    def __init__(self, fields: []):
        spec = fields[0].strip()
        if spec in [human_type, fly_type]:
            self.spec_type = spec
            self.gene_symbol = fields[1]
        else:
            self.spec_type = ''


class WormBaseOrthologsBlock:
    def __init__(self, block: []):
        #
        self.gene_symbol = ''
        self.wb_id = ''
        self.homo_orthologs = []
        self.fly_orthologs = []
        # header
        first_row = block[0]
        fls = first_row.split('\t')
        if len(fls) == 2:
            self.wb_id = fls[0].strip()
            self.gene_symbol = fls[1].strip()
        # orthologs
        for orth in block[1:]:
            ls = orth.split('\t')
            if len(ls) > 0:
                ortholog = WormBaseOrtholog(ls)
                if ortholog.spec_type == human_type:
                    self.homo_orthologs.append(ortholog.gene_symbol)
                elif ortholog.spec_type == fly_type:
                    self.fly_orthologs.append(ortholog.gene_symbol)

    def print(self):
        print(
            f'symbol:{self.gene_symbol}, homo_len:{len(self.homo_orthologs)}, fly_len:{len(self.fly_orthologs)}'
        )
        exit(13)


class WormBaseOrthologsList:
    def __init__(self, path: str):
        self.blocks = []
        fl = open(path)
        lines = fl.readlines()
        fl.close()
        self.parse(lines)
        print(f'file {path} len:{len(self.blocks)}')

    def new_block(self, rows: []):
        if not rows:
            return
        block = WormBaseOrthologsBlock(rows)
        self.blocks.append(block)
        # block.print()

    def parse(self, lines: []):
        block_rows = []
        for row in lines:
            row = row.strip()
            if len(row) == 0 or row[0] == '#':
                continue
            if row == '=':
                self.new_block(block_rows)
                block_rows = []
            else:
                block_rows.append(row)
        self.new_block(block_rows)


class GeneFetcherHUGO:
    def __init__(self, hugo_id: str):
        if ':' in hugo_id:
            hugo_id = hugo_id.strip().split(':')[1]

        self.hogo_id = hugo_id

    def exec(self) -> dict | None:
        try:
            response_raw = requests.get(
                f'http://rest.genenames.org/fetch/hgnc_id/{self.hogo_id}',
                headers={'Accept': 'application/json'},
            )

            if response_raw.status_code != 200:
                raise Exception(response_raw.status_code)

            response_json = response_raw.json()
            response = response_json.get('response')
            return response
        except:
            return None


class GenAgeGene:
    found_blocks = 0

    def __init__(self, row: str):
        self.row = row
        self.fields = [f.strip() for f in row.split(',')]
        self.wbase_block: WormBaseOrthologsBlock | None = None

    def get_symbol(self):
        return self.fields[1]

    def is_c_elegance(self):
        return self.fields[3] == source_file_c_elegance_name

    def find_orthologs(self, wbase_orthologs: WormBaseOrthologsList):
        gene_symbol = self.get_symbol()
        for wbase_ortholog in wbase_orthologs.blocks:
            if gene_symbol == wbase_ortholog.gene_symbol and self.is_c_elegance():
                self.wbase_block = wbase_ortholog
                GenAgeGene.found_blocks += 1
                break

    def build_line(self):
        def build_ortholog_field(orths_hugo_id_ls: [str]):
            orths_human_symbol_ls: [str] = []
            for hugo_id in orths_hugo_id_ls:
                gf = GeneFetcherHUGO(hugo_id)
                hugo_resp = gf.exec()
                if hugo_resp is None:
                    continue
                if hugo_resp and hugo_resp['numFound'] > 0:
                    hugo_gene = hugo_resp['docs'][0]
                    hugo_symbol = hugo_gene['symbol']
                    if hugo_symbol:
                        print(f'hugo symbol is found: {hugo_id} => {hugo_symbol}')
                        orths_human_symbol_ls.append(hugo_symbol)

            return '"' + ';'.join(orths_human_symbol_ls) + '"'

        homo_block = (
            build_ortholog_field(self.wbase_block.homo_orthologs) if self.wbase_block else ""
        )
        # fly_block = build_ortholog_field(self.wbase_block.fly_orthologs) if self.wbase_block else ""

        return self.row + f',{homo_block}'


class MissingGenes:
    def __init__(self, path: str):
        self.path = path
        self.symbol_list: [str] = []
        self.hugo_list = set([])

    def hugo_is_exist(self, hugo_id: str):
        return hugo_id in self.hugo_list

    def add_gene(self, hugo_id: str):
        if self.hugo_is_exist(hugo_id):
            return
        self.hugo_list.add(hugo_id)
        gf = GeneFetcherHUGO(hugo_id)
        hugo_resp = gf.exec()
        if hugo_resp is None:
            return
        if hugo_resp and hugo_resp['numFound'] > 0:
            hugo_gene = hugo_resp['docs'][0]
            hugo_symbol = hugo_gene['symbol']
            if hugo_symbol:
                print(f'hugo symbol is found: {hugo_id} => {hugo_symbol}')
                self.symbol_list.append(hugo_symbol)

    def save(self):
        body = '\n'.join(s.strip() for s in self.symbol_list if s)
        with open(self.path, 'w') as fl:
            fl.write(body)


class GenAgeOrthologsFile:
    missing_genes = MissingGenes('missing_genes.txt')

    def __init__(self, path: str):
        fl = open(path)
        rows = fl.readlines()
        fl.close()
        self.header = rows[0]
        self.genes = []
        for row in rows[1:]:
            row = row[: len(row) - 1]
            gag = GenAgeGene(row)
            self.genes.append(gag)
        print(f'source file len:{len(self.genes)}')

    def save_ext_file(self, path: str, wbase_orthologs: WormBaseOrthologsList):
        ext_header = self.header[: len(self.header) - 1] + ',human'
        for ga_orth in self.genes:
            ga_orth.find_orthologs(wbase_orthologs)
        print(GenAgeGene.found_blocks)
        lines = [ext_header]
        for ga_orth in self.genes:
            lines.append(ga_orth.build_line())
        fl = open(path, 'w')
        fl.write('\n'.join(lines))
        fl.close()


from db import dao


class OrthologHandlerDB:
    wormbase_name = 'wormbase'
    model_organism_lat = 'Caenorhabditis elegans'
    gene_dao = dao.GeneDAO()
    model_orgamism_dao = dao.ModelOrganismDAO()
    ortholog_dao = dao.OrthologDAO()

    def __init__(self, block: WormBaseOrthologsBlock):
        if not block:
            return
        self.gene_symbol = block.gene_symbol
        self.wormbase_id = block.wb_id
        self.human_orthologs = block.homo_orthologs

    def _handle_human_ortholog(self, ortholog_symbol: str, wormbase_id: str, hgnc_id: str):
        # gene id
        gene = OrthologHandlerDB.gene_dao.get_by_hugo_id(hgnc_id)
        if not gene:
            return
        print(
            f"ortholog handling: gene:{gene['symbol']}, ortholog_symbol: {self.gene_symbol}, hugo_id:{hgnc_id}"
        )

        # ortholog id
        try:
            ortholog_id = OrthologHandlerDB.ortholog_dao.get_id(
                ortholog_symbol,
                OrthologHandlerDB.model_organism_lat,
                OrthologHandlerDB.wormbase_name,
                wormbase_id,
            )
        except:
            return
        # gene to ortholog
        if ortholog_id:
            OrthologHandlerDB.ortholog_dao.link_gene(gene['id'], ortholog_id)

    def save(self):
        if not self.gene_symbol:
            return

        for hgnc_id in self.human_orthologs:
            self._handle_human_ortholog(self.gene_symbol, self.wormbase_id, hgnc_id)


def update_db_orthologs(worm_base_orthologs: WormBaseOrthologsList):
    for i, block in enumerate(worm_base_orthologs.blocks):
        if block:
            gag_handler = OrthologHandlerDB(block)
            gag_handler.save()


def update_file_genage(worm_base_orthologs: WormBaseOrthologsList):
    genage_orthologs_file = GenAgeOrthologsFile('genage_models.txt')
    genage_orthologs_file.save_ext_file('./gename_models_ext_human_fly.csv', worm_base_orthologs)


class MissingGenesWithOrthologs:
    def __init__(self, path: str):
        with open(path) as fl:
            rows = fl.readlines()
            self.symbols: [str] = []
            for row in rows[1:]:
                row = row[: len(row) - 1]
                ls = row.rsplit(',')
                if len(ls) == 9:
                    field = ls[8][1:-2]
                    if field:
                        symbols = [s.strip() for s in field.split(';') if s]
                        if len(symbols):
                            self.symbols += symbols

    def save(self, missing_path: str):
        with open(missing_path, 'w') as fl:
            fl.write('\n'.join(self.symbols))


WORK_MODE_UPDATE_DB_ORTHOLOGS = True

if __name__ == '__main__':
    print("orthologs parser start...")
    # mss = MissingGenesWithOrthologs('./gename_models_ext_human_fly.csv')
    # mss.save('missing_genes.txt')
    # exit()

    worm_base_orthologs = WormBaseOrthologsList('./c_elegans_gene_orthologs.txt')
    if WORK_MODE_UPDATE_DB_ORTHOLOGS:
        update_db_orthologs(worm_base_orthologs)
    else:
        update_file_genage(worm_base_orthologs)
    #

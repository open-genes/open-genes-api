from mysql import connector

from config import CONFIG
from entities import entities


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


class GeneDAO(BaseDAO):
    """Gene Table fetcher."""

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
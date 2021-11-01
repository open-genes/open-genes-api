from mysql import connector

from opengenes.config import CONFIG
from opengenes.entities import entities


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

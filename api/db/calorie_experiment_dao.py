from api.db.dao import BaseDAO
from models.gene import CalorieExperimentInput, CalorieExperimentOutput, CalorieExperiment


class CalorieExperimentDAO(BaseDAO):
    """Calorie experiment Table fetcher."""

    def calorie_experiment_search(self, input):

        tables = self.prepare_tables(CalorieExperiment)
        query, params, meta = self.prepare_query(tables, input)
        print(query)

        re = self.read_query(query, params, tables)

        meta.update(re.pop(0))

        return {'options': {'objTotal': meta['row_count'], 'total': meta.get('total_count'),
                "pagination": {"page": meta['page'], "pageSize": meta['pageSize'],
               "pagesTotal": meta['row_count'] // meta['pageSize'] + (
                   meta['row_count'] % meta['pageSize'] != 0)}}, 'items': re}

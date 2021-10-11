from opengenes.db.filters import FILTERS


class RequestHandler():

    def __init__(self, sql_row:str):
        self.sql_row = sql_row

    def set_pagination(self, page:int = None, pagesize:int = None):
        temp_sql_row = self.sql_row
        if page or pagesize:
            if pagesize and not page:
                page = 1
            elif not pagesize and page:
                pagesize = 10
            temp_sql_row = temp_sql_row.replace('@PAGE@', str(page))
            temp_sql_row = temp_sql_row.replace('@PAGESIZE@', str(pagesize))
            temp_sql_row = temp_sql_row.replace(
                '@LIMIT@',
                'LIMIT {} OFFSET {}'.format(
                    str(pagesize), str(pagesize * (page - pagesize))
                )
            )
        else:
            temp_sql_row = self.sql_row.replace('@PAGE@', '1')
            temp_sql_row = temp_sql_row.replace('@PAGESIZE@', 'jsout.fRows')
            temp_sql_row = temp_sql_row.replace(
                '@LIMIT@',
                ''
            )
        self.sql_row = temp_sql_row

    def set_language(self, lang:str):
        self.sql_row = self.sql_row.replace('_en', '_' + lang)

    @property
    def sql(self):
        return self.sql_row

    def add_filters(self, filters:dict):
        filter_array = []
        for key, value in filters.items():
            filter_array.append(FILTERS[key].format(value))
        temp_filters_row = 'AND'.join(filter_array)
        self.sql_row = self.sql_row.replace('@FILTERS@', temp_filters_row)
import re
import os

from mysql import connector

from opengenes.config import CONFIG


STR = 'str'
INT = 'int'
FLOAT = 'float'
DATE = 'date'
DATETIME = 'datetime'
TIME = 'time'

MYSQL_TYPES_MAP = {
    'char': STR,
    'varchar': STR,
    'tinytext': STR,
    'text': STR,
    'blob': STR,
    'mediumtext': STR,
    'mediumblob': STR,
    'longtext': STR,
    'longblob': STR,
    'tinyint': INT,
    'smallint': INT,
    'mediumint': INT,
    'int': INT,
    'bigint': INT,
    'float': FLOAT,
    'double': FLOAT,
    'decimal': STR,
    'date': DATE,
    'datetime': DATETIME,
    'time': TIME,
}

CUR_DIR = os.path.dirname(os.path.abspath(__file__))


class MySQLGenerator():
    def __init__(self, cnx: connector.CMySQLConnection):
        self.cnx = cnx

    def generate_entity(self, table_name: str):
        cur = self.cnx.cursor()
        cur.execute(f"SHOW COLUMNS FROM {table_name}")
        columns_info = cur.fetchall()

        class_name = ''.join([
            substring.capitalize() for substring in table_name.split('_')
        ])

        text = f'class {class_name}(BaseModel):\n'
        for column in columns_info:
            # Field type tuning.
            field_type = re.sub(r'[()0-9+]', '', column[1])
            try:
                field_type_name = MYSQL_TYPES_MAP[field_type]

                # Optional type checking.
                if column[2] == 'YES':
                    field_type_name = f'Optional[{field_type_name}] = None'

                text += f"    {column[0]}: {field_type_name}\n"
            except KeyError:
                print(f'Type {field_type} is not realised yet.')
        text += '\n\n'
        with open(os.path.join(CUR_DIR, f'generated_{table_name}.py'), 'w') as pyf:
            pyf.write(text)

    # def generate(self):
    #     cur = self.cnx.cursor()
    #     # cur.execute("select * from INFORMATION_SCHEMA.TABLES;")
    #     cur.execute('SHOW COLUMNS FROM gene;')
    #     tabels_info = cur.fetchall()
    #     print(tabels_info)
    #     # summary = ''
    #     # summary += 'from typing import Optional\n\n'
    #     # summary += 'from pydantic import BaseModel\n\n\n'
    #     # for table_name in tabels_info:
    #     #     summary += self.generate_entity(table_name[0])
    #     # with open('test.py', 'w') as pyf:
    #     #     pyf.write(summary)

    # def _get_relations_map(self):
    #     cur = self.cnx.cursor()
    #     cur.execute(
    #         """
    #         SELECT * FROM information_schema.KEY_COLUMN_USAGE
    #         WHERE information_schema.KEY_COLUMN_USAGE.TABLE_NAME = 'gene_to_protein_class'
    #         """
    #         # WHERE information_schema.TABLE_CONSTRAINTS.CONSTRAINT_TYPE = 'FOREIGN KEY' """
    #         # AND information_schema.TABLE_CONSTRAINTS.TABLE_NAME = 'gene';
    #         # """
    #     )
    #     relations_info = cur.fetchall()
    #     for relation in relations_info:
    #         print(relation)
    #         # temp = relation[2]
    #         # res = temp.split(relation[4])
    #         # print(res)


cnx = connector.connect(
    host=CONFIG['DB_HOST'],
    port=CONFIG['DB_PORT'],
    user=CONFIG['DB_USER'],
    password=CONFIG['DB_PASSWORD'],
    database=CONFIG['DB_NAME'],
)

gen = MySQLGenerator(cnx=cnx)
gen.generate_entity('gene')

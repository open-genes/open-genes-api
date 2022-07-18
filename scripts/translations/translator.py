import argparse
import re

from deep_translator import GoogleTranslator

from api.db import dao


def translate(table_name: str, field_name_en: str, field_name_ru: str):
    TRANSLATOR = GoogleTranslator(source='en', target='ru')

    cnx = dao.BaseDAO().cnx
    cur = cnx.cursor()
    cur.execute(f'SELECT id, {field_name_en}, {field_name_ru} FROM {table_name}')
    fields_info = cur.fetchall()
    for row in fields_info:
        field_id = row[0]
        field_en = row[1]
        field_ru = row[2]
        # print(field_en, field_ru)
        if field_en is not None and len(field_en) > 0 and (field_ru is None or len(field_ru) == 0):
            subcnx = dao.BaseDAO().cnx
            subsubcur = subcnx.cursor()
            if len(field_en) < 5000:
                translated_en_field = TRANSLATOR.translate(field_en)
            else:
                translated_en_field = ''
                for sentence in field_en.split('.'):
                    translated_en_field += ' ' + TRANSLATOR.translate(sentence)
                translated_en_field = translated_en_field[1:]  # For the first sentence space.
            ru_field = re.sub('[«»"]', '', translated_en_field)  # For incorrect quotes.
            query = f"""
                UPDATE {table_name}
                SET `{field_name_ru}` = %({field_name_ru})s
                WHERE id = {field_id};
            """
            subsubcur.execute(query, {field_name_ru: translated_en_field})
            subcnx.commit()
            subsubcur.close()
            subcnx.close()
            print(f"TRANSLATED IN {table_name}: id={field_id}, {field_en} => {ru_field}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Translate specific fields')
    parser.add_argument('--table-name', dest='table_name', required=True, help='table name')
    parser.add_argument(
        '--field_name_en', dest='field_name_en', help='field_name en', required=True
    )
    parser.add_argument(
        '--field_name_ru', dest='field_name_ru', help='field_name ru', required=True
    )
    args = parser.parse_args()
    translate(
        table_name=args.table_name,
        field_name_en=args.field_name_en,
        field_name_ru=args.field_name_ru,
    )

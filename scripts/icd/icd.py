import os

import pandas as pd

from api.db import dao
from api.entities import entities


def icd_ru_upload():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    icd_ru = pd.read_csv(
        os.path.join(cur_dir, 'icd10_ru.csv'),
        names=['id', 'icd_id', 'icd_code', 'name_ru', 'parent_id', '?', '??', '???'],
    ).dropna(subset=['icd_code'])
    updated_counter = 0
    for _, row in icd_ru.iterrows():
        icd_code = row['icd_code']
        if dao.DiseaseDAO().get(icd_code) is not None:
            dao.DiseaseDAO().update(
                disease=entities.Disease(
                    icd_code=icd_code,
                    icd_name_ru=row['name_ru'],
                )
            )
            updated_counter += 1
            print(f"UPDATED: icd_code={icd_code}, icd_name_ru=\'{row['name_ru']}\'")
    print(f'UPDATED: {updated_counter} rows!')


icd_ru_upload()

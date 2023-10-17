import json
import os
import re
import time
from collections import defaultdict

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CUR_DIR, 'drugage.csv')
DRUGAGE_MODIFIED = os.path.join(CUR_DIR, 'drugage_modified.tsv')

# uploads.
UPLOAD_DRUGAGE_DIR = os.path.join(CUR_DIR, 'drugage_articles')
UPLOAD_ITP_DIR = os.path.join(CUR_DIR, 'itp')
DRUGAGE_PMID_INFO_PATH = os.path.join(CUR_DIR, 'pmids_info_drugage.json')
ITP_PMID_INFO_PATH = os.path.join(CUR_DIR, 'pmids_info_itp.json')

# urls.
BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
SCIHUB_URL = 'https://sci-hub.ru/'


def drugage_articles_fetcher():
    if not os.path.exists(UPLOAD_DRUGAGE_DIR):
        os.mkdir(UPLOAD_DRUGAGE_DIR)
    drugage = pd.read_csv(DATA_DIR)

    # Get articles info by pmids.
    pmids_info_drugage = generate_pmid_info(set(drugage['pubmed_id']))

    # We use counters and threshhold because of strange SciHub behaviour.
    counter_all = 0
    counter_done = 0
    print('Starting download and save files from DrugAge.')
    print('Wait...')
    for compound_pmid, _ in tqdm(drugage.groupby(['compound_name', 'pubmed_id'])):
        # Get compound name with specific format.
        compound = compound_pmid[0].lstrip().lower().capitalize().replace('/', ' ')[:255]

        # Get and create compund dir if did not before.
        compound_dir = os.path.join(UPLOAD_DRUGAGE_DIR, compound)
        if not os.path.exists(compound_dir):
            os.mkdir(compound_dir)

        pmid = compound_pmid[1]
        doi = pmids_info_drugage[str(pmid)]['doi']
        title = pmids_info_drugage[str(pmid)]['title']
        pubdate = pmids_info_drugage[str(pmid)]['pubdate']

        # Generate file name.
        file_name = f'{pubdate} {pmid} {title}'

        # Upload article.
        done = upload_by_doi(doi=doi, file_name=file_name, dir=compound_dir)

        # Count uploaded.
        if done:
            counter_done += 1
        counter_all += 1
    print('Downloading ended.')
    print('done:', counter_done, 'missed:', counter_all - counter_done)


def itp_articles_fetcher():
    """NIH Aging Institute html with publications."""
    if not os.path.exists(UPLOAD_ITP_DIR):
        os.mkdir(UPLOAD_ITP_DIR)

    # Get NIH Aging Institute html with publications.
    r = requests.get(
        'https://www.nia.nih.gov/'
        + 'research/dab/interventions-testing-program-itp/publications-nia-interventions-testing-program'
    )

    # Prepare for parse
    html = r.text
    soup = BeautifulSoup(html, "html.parser")

    # Get PMIDs from links.
    pmids_from_href = set(
        [
            re.search(r'\d+', a.attrs['href']).group()
            for a in soup.find_all('a')
            if 'href' in a.attrs.keys() and 'pubmed' in a.attrs['href']
        ]
    )

    # Get raw text with PMID or DOI in.
    texts_doi_pmid = [
        p.text for p in soup.find_all('p') if re.search('PMID:|doi:|DOI:', p.text) is not None
    ]

    # Extract PMIDs or DOIs.
    pmids_from_raw = set()
    dois_from_raw = set()
    for text in texts_doi_pmid:
        if 'PMID' in text:
            group = text.split('PMID')[1]
            pmid = re.search(r'\d+', group).group()
            pmids_from_raw.add(pmid)
        elif 'doi' in text or 'DOI' in text:
            doi_raw = text.lower().split('doi: ')[1].replace(' ', '')
            doi = re.search(r'\d+\.\d+\/\D+[\d\.]+', doi_raw).group()
            dois_from_raw.add(doi)
    all_pmids = pmids_from_raw.union(pmids_from_href)

    pmids_info_itp = generate_pmid_info(all_pmids, ITP_PMID_INFO_PATH)

    print('Starting download and save files from ITP.')
    print('Wait...')
    counter_all = 0
    counter_done = 0
    for doi in tqdm(dois_from_raw):
        # Upload article.
        done = upload_by_doi(doi=doi, file_name=doi, dir=UPLOAD_ITP_DIR)
        if done:
            counter_done += 1
        counter_all += 1
    for pmid, values in tqdm(pmids_info_itp.items()):
        doi = values['doi']
        title = values['title']
        pubdate = values['pubdate']
        file_name = f'{pubdate} {pmid} {title}'[:250]
        # Upload article.
        done = upload_by_doi(doi=doi, file_name=file_name, dir=UPLOAD_ITP_DIR)
        if done:
            counter_done += 1
        counter_all += 1
    print('Downloading ended.')
    print('done:', counter_done, 'missed:', counter_all - counter_done)


def generate_pmid_info(pmids: set, path: str):
    print('Start getting info by pmids.')

    if os.path.isfile(path):
        with open(path) as f:
            return json.load(f)

    print('Saved file not found. Wait for generating info ...')

    pmid_info = defaultdict(dict)
    for pmid in tqdm(pmids):
        doi = None
        article = requests.get(BASE_URL + f'esummary.fcgi?db=pubmed&id={pmid}&retmode=json').json()

        # doi
        for id_info in article['result'][str(pmid)]['articleids']:
            if id_info['idtype'] == 'doi':
                doi = id_info['value']
        if doi is None or doi == '':
            doi = article['result'][str(pmid)]['elocationid']
        pmid_info[pmid]['doi'] = doi

        # title
        pmid_info[pmid]['title'] = article['result'][str(pmid)]['title']

        # pubdate
        pubdate = article['result'][str(pmid)]['pubdate']
        pmid_info[pmid]['pubdate'] = re.findall(r'\d+', pubdate)[0]

        # limit requests rate
        time.sleep(1.5)

    # Save info.
    with open(path, 'w') as f:
        json.dump(pmid_info, f)

    print('Ended.')
    return pmid_info


def pdf_link_generator(html):
    pdf_link = None
    soup = BeautifulSoup(html, "html.parser")

    iframe = soup.find(id='pdf')
    plugin = soup.find(id='plugin')

    if iframe is not None:
        pdf_link = iframe.get("src")

    if plugin is not None and pdf_link is None:
        pdf_link = plugin.get("src")

    if pdf_link is not None and pdf_link[0] != "h":
        pdf_link = "https:" + pdf_link

    return pdf_link


def upload_by_doi(doi, file_name, dir):
    """Upload file from scihub by doi."""
    SCIHUB_ATTEMPTS_THRESHHOLD = 5

    # Get common file name
    common_file_name = f'{file_name[:250]}.pdf'.replace('/', ' ').replace('..', '.')

    file_path = os.path.join(dir, common_file_name)
    if os.path.isfile(file_path):
        return True

    # Trying get appropriate pdf link.
    counter_attempt = 0
    pdf_link = None
    while pdf_link is None:
        time.sleep(3)
        r = requests.get(SCIHUB_URL + doi)
        pdf_link = pdf_link_generator(r.text)
        counter_attempt += 1
        if counter_attempt > SCIHUB_ATTEMPTS_THRESHHOLD:
            break

    # Download if found.
    if pdf_link is not None:
        # Get content.
        r = requests.get(pdf_link)

        # Save article.
        f = open(file_path, 'wb')
        f.write(r.content)
        f.close()
        return True
    else:
        return False


def fetch_pubchem_id():
    print('Fetching PubChem cids...')
    drugage = pd.read_csv(DATA_DIR)
    cas_to_cid = dict()
    for cas in set(drugage['cas_number']):
        url = f'https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas}/cids/TXT'
        cid = requests.get(url)
        if cid.ok:
            cas_to_cid[cas] = cid.text.split('\n')[0]
        time.sleep(1)

    drugage['PubChemCID'] = drugage['cas_number'].apply(
        lambda x: cas_to_cid[x] if x in cas_to_cid.keys() else ''
    )
    drugage.to_csv(DRUGAGE_MODIFIED, sep='\t', index=False)
    print('Done.')
    print('Found:', len(cas_to_cid), 'Missed:', len(set(drugage['cas_number'])) - len(cas_to_cid))


drugage_articles_fetcher()
itp_articles_fetcher()
fetch_pubchem_id()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

# // Some tests meant to get and organize
# // preprints data. This should lay the groundwork
# // for future preprints upload tests.


# Get a dictionary containing the first
# and last names of the authors of a Dissemin paper,
# ready to be implemented in an OSF Preprints data dict.
def translate_authors(dissemin_authors):
    first_name = dissemin_authors['name']['first']
    last_name = dissemin_authors['name']['last']

    structure = {
        "attributes": {
            "family_name": last_name,
            "given_name": first_name
        }
    }
    return structure


# Collect required data from a Dissemin paper
# to further create a preprint on OSF Preprints.
def get_metadeta_from_dissemin(paper_doi):
    url = "http://dissem.in/api/" + paper_doi
    paper_data = json.loads(json.dumps(requests.get(url).json()))
    paper = paper_data['paper']
    p_title = paper['title']
    p_records = paper['records']
    p_authors = paper['authors']

    # Look for a given key through a nested list.
    def get_item(entry, key):
        count = 0
        for item in paper[entry]:
            if key in item:
                return count
            else:
                count += 1

    data_dict = {
        "license": "TODO",
        "title": p_title,
        "category": "TODO",
        "description": p_records[get_item("records", "abstract")]['abstract'],
        "doi": paper_doi,
        "contributors": [translate_authors(author) for author in p_authors],
        'tags': p_records[get_item("records", "keywords")]['keywords']
    }

    print("|====================================|")
    print("|  Preparing data for OSF Preprints  |")
    print("|====================================|")

    for key in data_dict:
        print(key, data_dict[key])


paper_doi = raw_input("Enter Paper DOI: ")
get_metadeta_from_dissemin(paper_doi)
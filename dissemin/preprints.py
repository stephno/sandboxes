#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

# // Some tests meant to get and organize
# // preprints data. This should lay the groundwork
# // for future preprints upload tests.


# Collect required data from a Dissemin paper
# to further create a preprint on OSF Preprints
def get_metadeta_from_dissemin(paperDOI):
    url = "http://dissem.in/api/" + paperDOI
    paperData = json.loads(json.dumps(requests.get(url).json()))
    paper = paperData['paper']
    pTitle = paper['title']
    pRecords = paper['records']
    pAuthors = paper['authors']

    # Look for a given key through a nested list
    def get_item(level, key):
        count = 0
        for item in paper[level]:
            key = key
            if key in item:
                return count
            else:
                count += 1

    # Create authors dictionary
    def create_authors_dict(level):
        count = 0
        for item in level:
            last = level[count]['name']['last']
            first = level[count]['name']['first']
            structure = {
                "attributes": {
                    "family_name": last,
                    "given_name": first
                }
            }
        return structure

        if count == len(level):
            count += 1

    dataDict = {
        "license": "TODO",
        "title": pTitle,
        "category": "TODO",
        "description": pRecords[get_item("records", "abstract")]['abstract'],
        "preprint_doi": paperDOI,
        # 'contributors': paper['authors'],
        "contributors": [{
            create_authors_dict(pAuthors)
        }],
        # 'PDF_URL:': paper['pdf_url'],
        # 'preprint_doi': pRecords[get_item("records", "doi")]['doi'],
        'tags': pRecords[get_item("records", "keywords")]['keywords']
    }

    print("|====================================|")
    print("|  Preparing data for OSF Preprints  |")
    print("|====================================|")

    for key in dataDict:
        print(key, dataDict[key])


paperDOI = raw_input("Enter Paper DOI: ")
get_metadeta_from_dissemin(paperDOI)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

#  ======================================
# | STEP 1: GET THE DISSEMIN PAPER DATA  |
#  ======================================


# Get a dictionary containing the first and last names
# of the authors of a Dissemin paper,
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


# Collect the required data from a Dissemin paper
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
            if key in item and item[key] != "":
                return count
            else:
                count += 1

    # Look for an abstract
    def get_abstract(key):
        abstract_list = [subVal[key] for subVal in p_records
                         if key in subVal]

        abstract = ""
        for item in abstract_list:
            if item != "":
                abstract = item
            else:
                abstract = "None"

        return abstract

    #p_abstract = p_records[get_item("records", "abstract")]['abstract']
    p_abstract = get_abstract('abstract')
    p_contrib = [translate_authors(author) for author in p_authors]
    p_tags = p_records[get_item("records", "keywords")]['keywords']

# Required to create a new node.
# The project will then host the preprint.
    min_node_structure = {
        "data": {
            "type": "nodes",
            "attributes": {
                "title": p_title,
                "category": "project",
                "description": p_abstract
                # "tags": p_tags.replace('-', '').split(),
            }
        }
    }

    return min_node_structure

paper_doi = raw_input("Enter Paper DOI: ")
min_node_structure = get_metadeta_from_dissemin(paper_doi)

#  ==================================================
# | STEP 2: CREATE THE OSF PROJECT FOR THE PREPRINT  |
#  ==================================================
node_url = 'https://api.osf.io/v2/nodes/'
token = (open('osf-token.txt', 'r').read()).strip('\n')

headers = {
    'Authorization': 'Bearer %s' % token,
    'Content-Type': 'application/vnd.api+json'
}


# Extract the OSF Storage link
def translate_links(node_links):
    upload_link = node_links['links']['upload']
    return upload_link


# Send the min. structure.
# The response should contain the node ID.
def create_node():
    osf_response = requests.post(node_url,
                                 data=json.dumps(min_node_structure),
                                 headers=headers).json()
    return osf_response

osf_response = create_node()
print(osf_response)
node_id = osf_response['data']['id']
osf_nodes_url = "https://api.osf.io/v2/nodes/"


# Get OSF Storage link
# to later upload the Preprint PDF file.
def get_newnode_osf_storage(node_id):
    storage_url = osf_nodes_url + "{}/files/".format(node_id)
    osf_storage_data = requests.get(storage_url,
                                    headers=headers).json()

    return osf_storage_data

osf_storage_data = get_newnode_osf_storage(node_id)
osf_links = osf_storage_data['data']
osf_upload_link = str(list({translate_links(entry) for entry in osf_links}))
osf_upload_link = osf_upload_link.replace("[u'", '').replace("']", '')


# Now we send our first PDF, which will be
# the “primary_file” in the project.
def upload_preprint_pdf():
    upload_url_suffix = "?kind=file&name=dissemin_pdf_test.pdf"
    upload_url = osf_upload_link + upload_url_suffix
    upload_response = requests.put(upload_url,
                                   headers=headers).json()

    return upload_response

primary_file_data = upload_preprint_pdf()
pf_path = primary_file_data['data']['attributes']['path'][1:]
print(pf_path)

#  ==========================================
# | STEP 2: PREPAPRE THE PREPRINT STRUCTURE  |
#  ==========================================

# YET TO BE TOTALLY DEFINED
min_preprint_structure = {
    "data": {
        "attributes": {
            "doi": paper_doi
        },
        "relationships": {
            "node": {
                "data": {
                    "type": "nodes",
                    "id": node_id
                }
            },
            "primary_file": {
                "data": {
                    "type": "primary_files",
                    "id": pf_path
                }
            },
            "provider": {
                "data": {
                    "type": "providers",
                    "id": "osf"
                }
            }
        }
    }
}

# REMINDER OF WHAT REMAINS TO BE DEFINED
# data_dict = {
#         "license": "TODO",
#         "title": p_title,
#         "category": "TODO",
#         "description": p_records[get_item("records", "abstract")]['abstract'],
#         "doi": paper_doi,
#         "contributors": [translate_authors(author) for author in p_authors],
#         'tags': p_records[get_item("records", "keywords")]['keywords']
#     }
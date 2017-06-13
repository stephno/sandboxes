#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

# // Those tests are meant to see
# // how post requests work.

node_url = 'https://api.osf.io/v2/nodes/'
token = (open('osf-token.txt', 'r').read()).strip('\n')

headers = {
    'Authorization': 'Bearer %s' % token,
    'Content-Type': 'application/vnd.api+json'
}

# Required to create a new node.
# The project will then host the preprint.
min_node_structure = {
    "data": {
        "type": "nodes",
        "attributes": {
            "title": "First node creation test",
            "category": "project",
            "description": "Project meant to see "
                           "how one can send "
                           "preprints to OSF Preprints."
        }
    }
}


# Extract the OSF Storage link
def translate_links(node_links):
    upload_link = node_links['links']['upload']
    return upload_link


# Send the min. structure.
# The response should contain the node ID.
def create_node():
    with open('osf-response.json', 'w') as f:
        osf_response = requests.post(node_url,
                                     data=json.dumps(min_node_structure),
                                     headers=headers).json()

        f.write(json.dumps(osf_response, indent=3))

# create_node()

# --------------------------------------------
# Here after: Prepare the preprint for upload |
# --------------------------------------------
osf_data = json.load(open('osf-response.json', 'r'))
node_id = osf_data['data']['id']
osf_nodes_url = "https://api.osf.io/v2/nodes/"


# Get OSF Storage link
# to later upload the Preprint PDF file.
def get_newnode_osf_storage(node_id):
    with open('osf-storage-links.json', 'w') as f:
        storage_url = osf_nodes_url + "{}/files/".format(node_id)
        osf_storage_data = requests.get(storage_url,
                                        headers=headers).json()

        f.write(json.dumps(osf_storage_data, indent=3))

get_newnode_osf_storage(node_id)


osf_storage_data = json.load(open('osf-storage-links.json', 'r'))
osf_links = osf_storage_data['data']
osf_upload_link = str(list({translate_links(entry) for entry in osf_links}))
osf_upload_link = osf_upload_link.replace("[u'", '').replace("']", '')
# print(osf_upload_link)


# Now we send our first PDF, which will be
# the “primary_file” in the project.
def upload_preprint_pdf():
    with open('osf-primaryFile-path.json', 'w') as f:
        upload_url_suffix = "?kind=file&name=dissemin_pdf_test.pdf"
        upload_url = osf_upload_link + upload_url_suffix
        upload_response = requests.put(upload_url,
                                       headers=headers).json()

        f.write(json.dumps(upload_response, indent=3))

# upload_preprint_pdf()

primary_file_data = json.load(open('osf-primaryFile-path.json', 'r'))
pf_path = primary_file_data['data']['attributes']['path'][1:]
# print(pf_path)


# YET TO BE DEFINED
# preprint_structure = {
#     "data": {
#         "attributes": {},
#         "relationships": {
#             "node": {
#                 "data": {
#                     "type": "nodes",
#                     "id": node_id
#                 }
#             },
#             "primary_file": {
#                 "data": {
#                     "type": "primary_files",
#                     "id": pf_path
#                 }
#             }
#         }
#     }
# }
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

# // Those tests are meant to see
# // how post requests work.

# some useful URL
node_url = 'https://api.osf.io/v2/nodes/'

token = open('osf-token.txt', 'r').read()
headers = {
    'Authorization': 'Bearer {}'.format(token),
    'Content-Type': 'application/vdn.api+json'
}

# Required to create a new node.
# The project will then host the preprint.
min_structure = {
    "data": {
        "type": "nodes",
        "attributes": {
            "title": "First node creation test",
            "category": "project",
            "description": "Project meant to see how one can send preprints to OSF Preprints."
        }
    }
}


# Send the min. structure.
# Then should return the node ID.
def create_node():
    osf_request = requests.post(node_url,
        data = json.dumps(min_structure),
        headers=headers).json()
    print(osf_request.status_code, osf_request.reason)

    osf_request = json.loads(json.dumps(osf_request))
    atts_level = osf_request['data']

    print("|====================================|")
    print("|   Display the new node JSON tree   |")
    print("|====================================|")

    for item in atts_level:
        print("- {}: {}".format(item, atts_level[item]))
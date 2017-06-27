#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Dissemin: open access policy enforcement tool
# Copyright (C) 2014 Antonin Delpeuch
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
from __future__ import unicode_literals

import json

import requests

from deposit.protocol import DepositError
from deposit.protocol import DepositResult
from deposit.protocol import RepositoryProtocol
from deposit.registry import protocol_registry
from deposit.osf.forms import OSFForm
from django.utils.translation import ugettext as __
from django.utils.translation import ugettext_lazy as __
from papers.utils import kill_html


class OSFProtocol(RepositoryProtocol):
    """
    A protocol to submit using the OSF REST API
    """
    form_class = OSFForm

    def __init__(self, repository, **kwargs):
        super(OSFProtocol, self).__init__(repository, **kwargs)
        # we let the interface define another API endpoint (sandbox…)
        self.api_url = repository.endpoint
        if not self.api_url:
            self.api_url = "https://api.osf.io/v2/nodes/"

    def init_deposit(self, paper, user):
        """
        Refuse deposit when the paper is already on OSF
        """
        super(OSFProtocol, self).init_deposit(paper, user)
        return True

    def get_form_initial_data(self):
        data = super(OSFProtocol, self).get_form_initial_data()
        license_id = data['license']

        return license_id

    def createMetadata(self, form):
        paper = self.paper.json()
        authors = paper['authors']
        records = paper['records']

        # Look for specific subkey
        def get_key_data(key):
            for item in records:
                if item.get(key):
                    return item[key]

            return None

        abstract = get_key_data('abstract')
        paper_doi = get_key_data('doi')

        # Check that there is an abstract
        if abstract:
            self.log('No abstract found, aborting')
            raise DepositError(__('No abstract is available for this paper but ' +
                                  'OSF Preprints requires to attach one. ' +
                                  'Please use the metadata panel to provide one'))

        # tags = get_key_data('keywords')

        # Required to create a new node.
        # The project will then host the preprint.
        min_node_structure = {
            "data": {
                "type": "nodes",
                "attributes": {
                    "title": paper['title'],
                    "category": "project",
                    "description": abstract
                    # "description": "This text is a simple description to fill this field."
                    # "tags": p_tags.replace('-', '').split(),
                }
            }
        }

        return min_node_structure, authors, paper_doi

    def submit_deposit(self, pdf, form, dry_run=False):
        if self.repository.api_key is None:
            raise DepositError(__("No OSF token provided."))

        api_key = self.repository.api_key 

        deposit_result = DepositResult()

        # Creating the metadata
        self.log("### Creating the metadata")
        min_node_structure, authors, paper_doi = self.createMetadata(form)
        self.log(json.dumps(min_node_structure, indent=4)+'')
        self.log(json.dumps(authors, indent=4)+'')

        # Get a dictionary containing the first and last names
        # of the authors of a Dissemin paper,
        # ready to be implemented in an OSF Preprints data dict.
        def translate_authors(dissemin_authors):
            first_name = dissemin_authors['name']['first']
            last_name = dissemin_authors['name']['last']

            structure = {
                "data": {
                    "type": "contributors",
                    "attributes": {
                        "full_name": "{} {}".format(first_name, last_name)
                    }
                }
            }
            return structure

        # Extract the OSF Storage link
        def translate_links(node_links):
            upload_link = node_links['links']['upload']
            return upload_link

        # Creating a new depository
        self.log("### Creating a new depository")
        headers = {
            'Authorization': 'Bearer %s' % api_key,
            'Content-Type': 'application/vnd.api+json'
        }

        # Send the min. structure.
        # The response should contain the node ID.
        def create_node():
            osf_response = requests.post(self.api_url,
                                         data=json.dumps(min_node_structure),
                                         headers=headers).json()
            return osf_response

        osf_response = create_node()
        node_id = osf_response['data']['id']

        # Get OSF Storage link
        # to later upload the Preprint PDF file.
        def get_newnode_osf_storage(node_id):
            self.storage_url = self.api_url + "{}/files/".format(node_id)
            osf_storage_data = requests.get(self.storage_url,
                                            headers=headers).json()
            return osf_storage_data

        self.osf_storage_data = get_newnode_osf_storage(node_id)
        osf_links = self.osf_storage_data['data']
        osf_upload_link = str(list({translate_links(entry) for entry in osf_links}))
        osf_upload_link = osf_upload_link.replace("[u'", '').replace("']", '')

        # Uploading the PDF
        self.log("### Uploading the PDF")
        upload_url_suffix = "?kind=file&name=article.pdf"
        upload_url = osf_upload_link + upload_url_suffix
        data = open(pdf, 'r')
        primary_file_data = requests.put(upload_url,
                                         data=data,
                                         headers=headers).json()
        pf_path = primary_file_data['data']['attributes']['path'][1:]

        # Add contributors
        def add_contributors():
            contrib_url = self.api_url + node_id + "/contributors/"

            for author in authors:
                contrib = translate_authors(author)
                contrib_response = requests.post(contrib_url,
                                                 data=json.dumps(contrib),
                                                 headers=headers).json()

        add_contributors()

        # Submitting the metadata
        self.log("### Submitting the metadata")

        def create_preprint():
            license_url = "https://api.osf.io/v2/licenses/"
            license_url = license_url + "{}".format(license_id)
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
                        "license": {
                            "links": {
                                "related": {
                                    "href": license_url,
                                    "meta": {}
                                }
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

        return deposit_result

protocol_registry.register(OSFProtocol)
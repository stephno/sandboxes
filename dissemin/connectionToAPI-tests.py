#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

# // Some connection tests to see how one can access
# // metadata from the OSF Preprints API.


# Get some user data (rough draft)
def createUsrData():
    with open('user-bvmce.json', 'w') as f:
        usrData = requests.get('https://api.osf.io/v2/users/bvmce').json()
        f.write(json.dumps(usrData, indent=3))


# Get a project of this last user (rough draft)
def createProjectData():
    with open('data-bvmce-nfd5c.json', 'w') as f:
        projectData = requests.get('https://api.osf.io/v2/nodes/nfd5c').json()
        f.write(json.dumps(projectData, indent=3))


# Get a project
def getProjectData(projectID):
    # fileName = "project-" + projectID + "-data.json"
    url = "https://api.osf.io/v2/nodes/" + projectID
    projectData = json.loads(json.dumps(requests.get(url).json()))
    attsLvl = projectData['data']['attributes']

    print("|====================================|")
    print("| Playing with the OSF Preprints API |")
    print("|====================================|")

    for item in attsLvl:
        print("- {}: {}".format(item, attsLvl[item]))

    # with open(fileName, 'w') as f:
    #     projectData = requests.get(url).json()
    #     f.write(json.dumps(projectData, indent=3))


# Extract some specific data
def extractData():
    dataDict = {}
    with open('user-bvmce.json', 'r') as rep:
        dataDict = json.load(rep)
        attLvl = dataDict['data']['attributes']  # Save some repetitive typing.

        print("|===========================================|")
        print("|    Playing with the OSF Preprints API     |")
        print("| (Data previously gathered in a JSON file) |")
        print("|===========================================|")
        print("DICTIONARY LENGTH: {}".format(len(dataDict)))

        for item in attLvl:
            print("- {}: {}".format(item, attLvl[item]))
            print("======================================")


# Equivalent to extractData(), but directly querying the API
def extractDirectlyFromAPI():
    usrData = requests.get('https://api.osf.io/v2/users/bvmce').json()
    attLvl = usrData['data']['attributes']

    print("|====================================|")
    print("| Playing with the OSF Preprints API |")
    print("|====================================|")

    for item in attLvl:
        print("- {}: {}".format(item, attLvl[item]))


# Let’s create some fake project data
def createProject(aTitle, aCategory, aDescription):
    structure = {
        "data": {
            "type": "nodes",
            "attributes": {
                'title': aTitle,
                'category': aCategory,
                'description': aDescription
                }
            }
        }

    with open('newProject.json', 'w') as f:
        f.write(json.dumps(structure, sort_keys=True, indent=3))


# Collect a Paper data form Dissemin
def getDisseminPapers(paperDOI):
    url = "http://dissem.in/api/" + paperDOI
    paperData = json.loads(json.dumps(requests.get(url).json()))
    paperLvl = paperData['paper']

    print("|====================================|")
    print("|    Playing with the Dissemin API   |")
    print("|====================================|")

    for item in paperLvl:
        print("- {}: {}".format(item, paperLvl[item]))


# Collect required data from a Dissemin paper
# to further create a Preprints on OSF Preprints
def preparePaper(paperDOI):
    url = "http://dissem.in/api/" + paperDOI
    paperData = json.loads(json.dumps(requests.get(url).json()))
    paperLvl = paperData['paper']
    dataDict = {
        'TITLE:': paperLvl['title'],
        'AUTHORS:': paperLvl['authors'],
        'PDF_URL:': paperLvl['pdf_url'],
        'LICENSE:': 'TO BE FOUND',
        'DOI:': paperLvl['records'][1]['doi'],
        'KEYWORDS:': paperLvl['records'][1]['keywords'],
        'ABSTRACT:': paperLvl['records'][1]['abstract']
    }

    print("|====================================|")
    print("|  Preparing data for OSF Preprints  |")
    print("|====================================|")
    for key in dataDict:
        print(key, dataDict[key])

# extractDirectlyFromAPI()
# createProject(
#    'My Super Title', 'My Great Category', 'Here is a useful description.')

# projectID = raw_input("Enter Project ID: ")
# getProjectData(projectID)

paperDOI = raw_input("Enter Paper DOI: ")
preparePaper(paperDOI)
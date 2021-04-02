import requests
import json
import re

API_ID_URL = "https://v2.sherpa.ac.uk/cgi/object_ids"
API_URL = "https://v2.sherpa.ac.uk/cgi/retrieve"
API_RETRIEVE_BY_ID = "https://v2.sherpa.ac.uk/cgi/retrieve_by_id"
DATA_ACCESS = "?item-type=publisher_policy&api-key="
MY_KEY = # SHERPA/RoMEO key
JSON = "&format=Json"
LIMIT = "&limit=6"
IDENTIFIER = "&identifier="
ID_URL = (API_ID_URL + DATA_ACCESS + MY_KEY + LIMIT)
CHOSEN_IDENTIFIER_URL = (API_RETRIEVE_BY_ID + DATA_ACCESS
                         + MY_KEY + JSON + IDENTIFIER)
ID_FORMAT = re.compile(r'^(?P<id>\d+)\t(?P<date>\d{4}-\d{2}-\d{2}) ' 
                       '(?P<time>\d{2}:\d{2}:\d{2})$')

class Policy:
    def __init__(self, policy_id, sherpa_uri,
                 oa_authorization, submitted_info,
                 last_reviewed, date_created, last_modified,
                 publisher_id, publisher_name,
                 publisher_website, publisher_urls):

        self.policy_id = ''.join(policy_id)
        self.sherpa_uri = sherpa_uri
        self.oa_authorization = oa_authorization
        self.submitted_info = submitted_info 
        self.publisher_id = publisher_id
        self.publisher_name = publisher_name
        self.last_reviewed = last_reviewed
        self.date_created = date_created
        self.last_modified = last_modified
        self.publisher_website = publisher_website
        self.publisher_urls = publisher_urls

    def test(self):
        pass


    def display_publisher_urls(self):
        """The API provides complementary information
        about the policy (old and new policy comparison,
        copyright & permissions, etc.)

        Take a list and return a string.
        """
        formatted_response = []

        for item in self.publisher_urls:
            url = f'\t{item["url"]} ({item["description"]})'
            formatted_response.append(url)

        urls = '\n'.join(formatted_response)

        return urls


    def display_policy(self):
        policy = (
            f"\t\t=== {self.publisher_name} Policy ===\n"
            f"\n  Publisher Information\n  ---------------------\n"
            f"ID: {self.publisher_id}\n"
            f"Website: {self.publisher_website}\n"
            f"URLs:\n{self.display_publisher_urls()}\n"
            f"> {self.oa_authorization}\n"
            f"\n  Routes to OA\n  ------------\n"
            f"{self.submitted_info}\n"
            f"\n  Record Information\n  ------------------\n"
            f"ID: {self.policy_id}\n"
            f"Last Reviewed: {self.last_reviewed}\n"
            f"Created on: {self.date_created} UTC\n"
            f"Last Modified: {self.last_modified} UTC\n"
            f"SHERPA/RoMEO URI: {self.sherpa_uri}\n"
        )

        return print(policy)


def get_ids(line):
    """Sherpa/RoMEO API v2 provides a list of ids
    in a very simple text format. Each line is as follow:
        id  yyy-mm-dd hh:mm:ss
    
    Return a list.
    """
    lot = ID_FORMAT.match(line)

    return lot.group('id')


def get_all_policy_ids():
    """To know exactly which policies are available,
    we first need to get the list of all the policies.
    
    Return a list.
    """
    query = requests.get(ID_URL).text

    return [get_ids(line) for line in query.splitlines()]


def retrieve_raw_data(sherpa_id):
    """Retrive all the data from a specific publisher policy.

    Take a string and return a dictionary.
    """
    raw_data = requests.get(CHOSEN_IDENTIFIER_URL + sherpa_id).json()

    if any(raw_data.values()) == False:
        return "This publisher policy is not available."
    else:
        return raw_data


def get_sherpa_uri(raw_data):
    """
    Take a string and return a string.
    """
    return raw_data["items"][0]["system_metadata"]["uri"]


def get_oa_authorization(raw_data):
    """
    Take a string and return a string.
    """
    path = raw_data["items"][0]

    if path["open_access_prohibited"] == "no":
        return "Open Access is allowed."
    else:
        return "Open Access is prohibited."


def get_last_reviewed(raw_data):
    """
    Take a string and return a string.
    """
    partial_path = raw_data["items"][0] # Because PEP-8 compliancy!
    
    return partial_path["workflow_dates"]["policy_last_reviewed"]


def get_date_created(raw_data):
    """
    Take a string and return a string.
    """
    return raw_data["items"][0]["system_metadata"]["date_created"]


def get_last_modified(raw_data):
    """
    Take a string and return a string.
    """
    return raw_data["items"][0]["system_metadata"]["date_modified"]


def get_publisher_id(raw_data):
    """
    Take a string and return an integer.
    """
    publisher_id = raw_data["items"][0]["publisher"]["id"]
    
    return publisher_id


def get_publisher_name(raw_data):
    """
    Take a string and return a string.
    """
    return raw_data["items"][0]["publisher"]["name"][0]["name"]


def get_publisher_website(raw_data):
    """
    Take a string and return a string.
    """
    return raw_data["items"][0]["publisher"]["url"]


def get_publisher_urls(raw_data):
    """SHERPA/RoMEO provides URLS with more info
    about the publisher policy (OA, copyright & permissions,
    publishing agreement, old and new policy comparison, etc.)
    
    Take a string and return a list of dictionaries. 
    """
    urls = [item for item in raw_data["items"][0]["urls"]]

    return urls


def get_submitted_info(raw_data, version):
    """Give the following set of info
    about where this version can be archived:
        - conditions (if any);
        ‑ embargo (if any);
        ‑ license (if any).
    
    Take a string and return a ???.
    """
    #version = "submitted"
    partial_path = raw_data["items"][0]["permitted_oa"]

    # First, we get the type of repository
    # in which this version can be archived.
    for item in partial_path:
        if (any(version) in entry.values()
        for entry in item["location"]):
            location = []

            for value in item["location"]["location_phrases"]:
                place = value["phrase"]

                if place not in location:
                    location.append(place)

                if "Named Repository" in location:
                    repos_path = item["location"]["named_repository"]
                    repos = ', '.join([repo for repo in repos_path])
                    location[location.index('Named Repository')] = (
                            f"Named Repository ({repos})"
                            )
            return location
        else:
            return "No information provided for this version."


def get_routes_info(raw_data, version):
    routes = [] # All the data we need
    
    # Gather all the data
    locations = get_location(raw_data, version)
    conditions = get_conditions(raw_data, version)
    embargo = get_embargo(raw_data, version)
    oa_fees = get_additional_oa_fee(raw_data, version)
    license = get_license(raw_data, version)
    notes = get_public_notes(raw_data, version)
    version = version.capitalize()
    
    # Depending on certain conditions,
    # a version can be archived in a bunch of different locations.
    # If so, we need to split the data set.
    if len(locations) >= 1:
        final_message = []
        for (item, elem, emb, fee, lic, note) in (
        zip(locations, conditions, embargo, oa_fees, license, notes)):
            places = '\n'.join([place for place in item])
            restrictions = '\n'.join([cond for cond in elem])
            embargos = '\n'.join([period for period in emb])
            oa_fee = oa_fees[oa_fees.index(fee)]
            licenses = '\n'.join([value for value in lic])
            add_notes = '\n'.join([info for info in note])

            message = (
                f"The {version} version can be archived in:\n"
                f"{places}\n\n"
                f"… with the following conditions:\n"
                f"{restrictions}\n\n"
                f"{embargos}\n\n"
                f"{oa_fee}\n\n"
                f"… with one of the following licenses:\n"
                f"{licenses}\n\n"
                f"{add_notes}\n"
            )
            final_message.append(message)

        routes.append('\n'.join([value for value in final_message]))

    #else:
    #    places = '\n'.join([place for place in locations[0]])
    #    message = (f"The {version} version can be archived in:\n"
    #               f"{places}\n")
    #    routes.append(message)
    
    return routes[0]
    #return len(locations)


def get_location(raw_data, version):
    """Get the type of location and repository
    in which the current version can be archived.

    Take a string and return a list.
    """
    partial_path = raw_data["items"][0]["permitted_oa"]

    location = []
    for item in partial_path:
        for entry in item["article_version"]:
            if entry == version:
                loc_path = item["location"]["location_phrases"]
                location.append([p["phrase"] for p in loc_path])
                
                for elem in location:
                    if "Named Repository" in elem:
                        repos_path = (
                            item["location"]["named_repository"]
                        )
                        repos = ', '.join([r for r in repos_path])
                        value = "Named Repository"
                        elem[elem.index(value)] = (
                            f"Named Repository ({repos})"
                        )

                    if "Named Academic Social Network" in elem:
                        subpath = item["location"]
                        repos_path = (
                            subpath["named_academic_social_network"]
                        )
                        repos = ', '.join([r for r in repos_path])
                        value = "Named Academic Social Network"
                        elem[elem.index(value)] = (
                            f"Named Academic Social Network ({repos})"
                        )

    if not location:
        return "No information provided for this version."
    else:
        return location


def get_conditions(raw_data, version):
    """Get the conditions with which the version must be archived. 

    Take two strings and return a list.
    """
    partial_path = raw_data["items"][0]["permitted_oa"]

    conditions = []
    for item in partial_path:
        if "conditions" in item:
            for entry in item["article_version"]:
                if entry == version:
                    conditions.append(
                        [value for value in item["conditions"]]
                )
        else:
            conditions.append(["No Conditions"])

    return conditions


def get_embargo(raw_data, version):
    """
    Take a string and return a list.
    """
    partial_path = raw_data["items"][0]["permitted_oa"]
    
    embargo = []
    for item in partial_path:
        for entry in item["article_version"]:
            if entry == version:
                if "embargo" in item:
                    amount = str(item["embargo"]["amount"])
                    units = item["embargo"]["units"]
                    embargo.append(
                        [f"… with an embargo of {amount} {units}"])
                else:
                    embargo.append([f"… with no embargo"])

    return embargo 


def get_additional_oa_fee(raw_data, version):
    """
    Take a string and return a list.
    """
    partial_path = raw_data["items"][0]["permitted_oa"]

    additional_fee = []
    for item in partial_path:
        for entry in item["article_version"]:
            if entry == version:
                if item["additional_oa_fee"] == "yes":
                    additional_fee.append(
                        f"A fee must be paid to the publisher.")
                else:
                    additional_fee.append(
                        f"No additional fee required.")
    
    return additional_fee


def get_license(raw_data, version):
    """
    Take a string and return a list.
    """
    partial_path = raw_data["items"][0]["permitted_oa"]

    licenses = []
    for item in partial_path:
        for entry in item["article_version"]:
            if entry == version:
                if "license" in item:
                    group = []
                    for elem in item["license"]:
                        value = (
                            elem["license_phrases"][0]["phrase"]
                        )
                        if "version" in elem:
                            license_version = elem["version"]
                            group.append(f"{value} {license_version}")
                        else:
                            group.append(f"{value}")
                    licenses.append([content for content in group])
                else:
                    licenses.append([f"None required"])
    
    return licenses


def get_public_notes(raw_data, version):
    """
    Take a string and return a list.
    """
    partial_path = raw_data["items"][0]["permitted_oa"]

    notes = []
    for item in partial_path:
        for entry in item["article_version"]:
            if entry == version:
                if "public_notes" in item:
                    notes.append(
                        [note for note in item["public_notes"]])
                else:
                    notes.append("")
    return notes


def test_policy_retrieval(pol_id, pol_data):
    # Prepare a Policy
    policy_id = pol_id
    sherpa_uri = get_sherpa_uri(pol_data)
    oa_authorization = get_oa_authorization(pol_data)
    #submitted_info = get_submitted_info(pol_data, "accepted")
    submitted_info = get_routes_info(pol_data, "published")
    last_reviewed = get_last_reviewed(pol_data)
    date_created = get_date_created(pol_data)
    last_modified = get_last_modified(pol_data)
    publisher_id = get_publisher_id(pol_data)
    publisher_name = get_publisher_name(pol_data)
    publisher_website = get_publisher_website(pol_data)
    publisher_urls = get_publisher_urls(pol_data)
    
    test = Policy(policy_id, sherpa_uri,
                oa_authorization, submitted_info,
                last_reviewed, date_created, last_modified,
                publisher_id, publisher_name,
                publisher_website, publisher_urls)

    return test.display_policy()


policy_ids = get_all_policy_ids()
policies_raw_data = [] # list of policies

# Store all the nested dictionaries
for p_id in policy_ids:
    policies_raw_data.append(retrieve_raw_data(p_id))

test_policy_retrieval(policy_ids[4], policies_raw_data[4])
#print(get_license(policies_raw_data[2], "published"))
#print(get_conditions(policies_raw_data[0], "submitted"))
#print(get_additional_oa_fee(policies_raw_data[5], "published"))

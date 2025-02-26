import json
import requests
from pprint import pprint
from pathlib import Path
from src.registration import data_dir

# Base URLs
BASE_URL = "https://in-info-web20.luddy.indianapolis.iu.edu/apis/default/fhir"
BASE_HERMES_URL = 'http://159.65.173.51:8080/v1/snomed'
PRIMARY_CARE_URL = "http://137.184.71.65:8080/fhir/Patient"
CONDITION_URL = "http://137.184.71.65:8080/fhir/Condition"

# File to store resource ID
RESOURCE_FILE = "data/primary_care_patient_resource_id.txt"

# Functions for Authorization and Headers
def get_access_token_from_file():
    """Retrieve access token from file."""
    file_path = Path(data_dir / "access_token.json")
    if not file_path.exists():
        print("Error: access_token.json file not found.")
        return None
    try:
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)
            return json_data.get("access_token")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error reading access token from file: {e}")
        return None


def get_headers():
    """Generate headers for API requests."""
    access_token = get_access_token_from_file()
    if access_token:
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    else:
        return {"Content-Type": "application/json"}

# Patient Operations
def search_patient_by_name(name_string):
    """Search for a patient by name."""
    url = f'{BASE_URL}/Patient?name={name_string}'
    response = requests.get(url, headers=get_headers())
    print(response.url)
    data = response.json()
    if 'entry' in data:
        patient = data['entry'][0]['resource']
        resource_id = patient['id']
        given_name = patient['name'][0]['given'][0]
        family_name = patient['name'][0]['family']
        print(f"Resource ID: {resource_id} - {given_name} {family_name}")
        return resource_id
    print("No patients found.")
    return None


def fetch_patient_details(patient_resource_id):
    """Fetch patient details using resource ID."""
    url = f"{BASE_URL}/Patient/{patient_resource_id}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch patient details. HTTP Status Code: {response.status_code}")
        print(f"Error: {response.text}")
        return None


def generate_patient_json_from_fhir(patient_data):
    """Generate a simplified JSON representation of a patient."""
    return {
        "resourceType": "Patient",
        "name": patient_data.get("name", []),
        "gender": patient_data.get("gender"),
        "birthDate": patient_data.get("birthDate"),
        "address": patient_data.get("address", [])
    }


def post_patient_to_primary_care(patient_data):
    """Post patient data to Primary Care."""
    response = requests.post(PRIMARY_CARE_URL, headers=get_headers(), json=patient_data)
    if response.status_code in [200, 201]:
        print("Patient data posted successfully to Primary Care!")
        return response.json().get("id")
    else:
        print(f"Failed to post patient data. Status code: {response.status_code}")
        print(f"Error: {response.text}")
        return None


def save_resource_id_to_file(resource_id):
    """Save resource ID to a file."""
    with open(RESOURCE_FILE, 'w') as file:
        file.write(resource_id)
    print(f"Resource ID {resource_id} saved to {RESOURCE_FILE}.")

# Condition Operations
def get_one_condition(patient_resource_id):
    """Retrieve one condition for a given patient."""
    url = f'{BASE_URL}/Condition?patient={patient_resource_id}'
    response = requests.get(url, headers=get_headers())
    print(response.url)
    data = response.json()
    if 'entry' in data and data['entry']:
        resource = data['entry'][0]['resource']
        return resource.get('code', {}).get('coding', [{}])[0].get('code', 'Unknown Code')
    print("No conditions found.")
    return None


def get_direct_parent_snomed(snomed_code):
    """Retrieve the direct parent SNOMED concept for a given code."""
    url = f'{BASE_HERMES_URL}/search?constraint=>! {snomed_code}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            parent = data[0]
            return parent['conceptId'], parent['preferredTerm']
    print(f"Failed to fetch data from Hermes. HTTP Status Code: {response.status_code}")
    return None, None


def generate_condition_json(patient_id, snomed_code, snomed_display):
    """Generate a JSON representation of a condition."""
    return {
        "resourceType": "Condition",
        "clinicalStatus": {
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]
        },
        "verificationStatus": {
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-ver-status", "code": "confirmed"}]
        },
        "category": [
            {
                "coding": [
                    {"system": "http://terminology.hl7.org/CodeSystem/condition-category", "code": "encounter-diagnosis"}
                ]
            }
        ],
        "code": {
            "coding": [{"system": "http://snomed.info/sct", "code": snomed_code, "display": snomed_display}],
            "text": snomed_display
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "onsetDateTime": "2024-12-03"
    }


def post_condition_to_primary_care(condition_data):
    """Post condition data to Primary Care."""
    response = requests.post(CONDITION_URL, headers=get_headers(), json=condition_data)
    if response.status_code in [200, 201]:
        print("Condition data posted successfully to Primary Care!")
        pprint(response.json())
    else:
        print(f"Failed to post condition data. Status code: {response.status_code}")
        print(f"Error: {response.text}")

# Main Execution
if __name__ == '__main__':
    patient_name = "Thiel"
    patient_id = search_patient_by_name(name_string=patient_name)

    if patient_id:
        print(f"\nFetching details for patient with ID: {patient_id}")
        patient_details = fetch_patient_details(patient_resource_id=patient_id)

        if patient_details:
            patient_json = generate_patient_json_from_fhir(patient_details)
            print(f"Generated Patient JSON:\n{json.dumps(patient_json, indent=4)}")

            print("\nPosting patient data to Primary Care...")
            primary_care_patient_id = post_patient_to_primary_care(patient_json)

            if primary_care_patient_id:
                save_resource_id_to_file(primary_care_patient_id)

                condition_code = get_one_condition(patient_resource_id=patient_id)

                if condition_code:
                    parent_snomed_code, parent_snomed_display = get_direct_parent_snomed(condition_code)
                    if parent_snomed_code and parent_snomed_display:
                        print("\nGenerating and posting condition data for direct parent...")
                        condition_json = generate_condition_json(
                            primary_care_patient_id, parent_snomed_code, parent_snomed_display
                        )
                        post_condition_to_primary_care(condition_json)
import json
import requests
from pathlib import Path
from src.registration import data_dir
from pprint import pprint

# Base URLs
BASE_URL = "https://in-info-web20.luddy.indianapolis.iu.edu/apis/default/fhir"
PRIMARY_CARE_URL = "http://137.184.71.65:8080/fhir/Patient"
CONDITION_URL = "http://137.184.71.65:8080/fhir/Condition"
OBSERVATION_URL = "http://137.184.71.65:8080/fhir/Observation"

# File to store resource ID
RESOURCE_FILE = "data/primary_care_patient_resource_id.txt"


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


def read_patient_id_from_file():
    """Read the patient ID from the resource file."""
    try:
        with open(RESOURCE_FILE, 'r') as file:
            patient_id = file.read().strip()
            print(f"Patient ID from file: {patient_id}")
            return patient_id
    except FileNotFoundError:
        print(f"Error: {RESOURCE_FILE} not found.")
        return None


def generate_observation_json(patient_id, snomed_code, snomed_display):
    """Generate a JSON representation of an observation."""
    observation_json = {
        "resourceType": "Observation",
        "id": "5",
        "meta": {
            "versionId": "1",
            "lastUpdated": "2024-12-07T05:43:53.874+00:00",
            "source": "#sohE8q34od2zZuED",
            "profile": ["http://hl7.org/fhir/StructureDefinition/vitalsigns"]
        },
        "text": {
            "status": "generated"
        },
        "identifier": [{
            "system": "urn:ietf:rfc:3986",
            "value": "urn:uuid:187e0c12-8dd2-67e2-99b2-bf273c878281"
        }],
        "basedOn": [{
            "identifier": {
                "system": "https://acme.org/identifiers",
                "value": "1234"
            }
        }],
        "status": "final",
        "category": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "85354-9",
                "display": "Blood pressure panel with all children optional"
            }],
            "text": "Blood pressure systolic & diastolic"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": "2012-09-17",
        "performer": [{
            "reference": "Practitioner/4"
        }],
        "interpretation": [{
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": "L",
                "display": "low"
            }],
            "text": "Below low normal"
        }],
        "bodySite": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": snomed_code,
                "display": snomed_display
            }]
        },
        "component": [{
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8480-6",
                    "display": "Systolic blood pressure"
                }]
            },
            "valueQuantity": {
                "value": 107,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org",
                "code": "mm[Hg]"
            },
            "interpretation": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    "code": "N",
                    "display": "normal"
                }],
                "text": "Normal"
            }]
        }, {
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8462-4",
                    "display": "Diastolic blood pressure"
                }]
            },
            "valueQuantity": {
                "value": 60,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org",
                "code": "mm[Hg]"
            },
            "interpretation": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    "code": "L",
                    "display": "low"
                }],
                "text": "Below low normal"
            }]
        }]
    }
    return observation_json


def post_observation_to_primary_care(observation_data):
    """Post observation data to Primary Care."""
    response = requests.post(OBSERVATION_URL, headers=get_headers(), json=observation_data)
    if response.status_code in [200, 201]:
        print("Observation data posted successfully to Primary Care!")
        pprint(response.json())
    else:
        print(f"Failed to post observation data. Status code: {response.status_code}")
        print(f"Error: {response.text}")


if __name__ == '__main__':
    patient_id = read_patient_id_from_file()

    if patient_id:
        snomed_code = "368209003"
        snomed_display = "Right arm"

        observation_json = generate_observation_json(patient_id, snomed_code, snomed_display)

        post_observation_to_primary_care(observation_json)

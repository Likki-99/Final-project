import json
import requests
from pprint import pprint
from pathlib import Path
from src.registration import data_dir

# Base URLs
PRIMARY_CARE_URL = "http://137.184.71.65:8080/fhir/Procedure"
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

def generate_procedure_json(patient_id):
    """Generate a JSON representation of a Procedure."""
    procedure_json = {
        "resourceType": "Procedure",
        "id": "6",
        "meta": {
            "versionId": "1",
            "lastUpdated": "2024-12-07T05:43:59.291+00:00",
            "source": "#5MYycLD52F7ms8PO"
        },
        "text": {
            "status": "generated"
        },
        "status": "completed",
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "1155885007",  # Aortic Valve Repair
                    "display": "Aortic Valve Repair (Procedure)"
                }
            ],
            "text": "Aortic Valve Repair"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "recorder": {
            "reference": "Practitioner/4",
            "display": "Dr Adam Careful"
        },
        "performer": [
            {
                "actor": {
                    "reference": "Practitioner/4",
                    "display": "Dr Adam Careful"
                }
            }
        ],
        "followUp": [
            {
                "text": "ROS 7 days - 2024-04-10"
            }
        ],
        "note": [
            {
                "text": "Routine Aortic Valve Repair. Valve was repaired successfully."
            }
        ]
    }
    return procedure_json

# Function to post Procedure data to Primary Care
def post_procedure_to_primary_care(procedure_data):
    """Post Procedure data to Primary Care."""
    response = requests.post(PRIMARY_CARE_URL, headers=get_headers(), json=procedure_data)
    if response.status_code in [200, 201]:
        print("Procedure data posted successfully to Primary Care!")
        pprint(response.json())
    else:
        print(f"Failed to post procedure data. Status code: {response.status_code}")
        print(f"Error: {response.text}")

# Main Execution
if __name__ == '__main__':
    # Read patient resource ID from file
    try:
        with open(RESOURCE_FILE, 'r') as file:
            primary_care_patient_id = file.read().strip()
    except FileNotFoundError:
        print(f"Error: {RESOURCE_FILE} not found.")
        exit(1)

    if not primary_care_patient_id:
        print("Error: Patient ID is empty in the file.")
        exit(1)

    print(f"Using Patient ID: {primary_care_patient_id}")

    # Generate Procedure JSON for Aortic Valve Repair
    procedure_json = generate_procedure_json(primary_care_patient_id)

    # Post Procedure to Primary Care
    post_procedure_to_primary_care(procedure_json)

INFO-B 581 Health Informatics Standards and Terminologies - Final Project

ETL Pipeline Project Description

This project involves designing and implementing an ETL (Extract, Transform, Load) pipeline to interact with a FHIR (Fast Healthcare Interoperability Resources) API. The pipeline retrieves patient data and associated medical conditions from the OpenEMR FHIR API, transforms the data to meet Primary Care EHR FHIR API standards, and loads the data into the target system

Project Website - https://pages.github.iu.edu/snomula/final_project/index.html

Features
Extraction:

The source EHR is OpenEMR, and the data is accessed using its FHIR API.
Data is also extracted from the Hermes SNOMED API for hierarchical coding transformations.
OAuth 2.0 is used for secure API authentication.
Retrieves patient data, conditions, observations, and procedures from the source EHR.
Includes robust error handling for API authentication and data retrieval issues.

Transformation:

Follows FHIR-compliant JSON structures for all resources.
Transforms SNOMED CT codes to their parent and child codes using the Hermes API.
Includes logic for handling missing fields to ensure data integrity.
Generates unique identifiers for patient and condition records to maintain consistency across systems.

Loading:

Posts FHIR-compliant patient data, conditions, observations, and procedures to the Primary Care EHR FHIR API.
Ensures all data is linked to a single patient resource for integrity and seamless data flow.

Requirements

To successfully run the project, the following Python libraries and dependencies are required:

requests

matplotlib

urllib3

idna

certifi

charset-normalizer

These libraries must be installed before running the scripts.

Configure API and Running Scripts

API Configuration

Set up Access Tokens: Ensure the access_token.json file is in the data/ directory. This file is required for API authentication.

Provide Required API Details: Update the following parameters in the relevant scripts located in src/:

BASE_URL for the source EHR API.

PRIMARY_CARE_URL for the target FHIR server.

BASE_HERMES_URL for SNOMED operations.

Ensure the client_id, client_secret, and redirect_uri are correctly configured in the registration module.

Running Scripts

To execute the ETL tasks:

Clone the repository:
git clone https://github.com/username/project_name.git

cd project_name

Run Individual tasks located in src/:

Task 1: Run the script to fetch patient data and post parent term of the condition python src/task_1.py

Task 2: Run the script to fetch patient data and post child term of the condition python src/task_2.py

Task 3: Run the script to post observation to the patient python src/task_3.py

Task 4: Run the script to post procedure to the patient python src/task_4.py

Viewing Visualization of the insights
To view the visualizations described on the insights page, run the script for analysis:

Visualization 1 - For Top 5 states with the most patients, run the code - visualization.py
Visualization 2 - For Top 5 states with the most patients, run the code - city_viz.py

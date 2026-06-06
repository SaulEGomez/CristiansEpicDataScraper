# main.py
import json
import csv
from src.models import LeadModel
from src.search.google_xray import google_xray_search
from src.crm.sf_uploader import push_to_salesforce

def load_config():
    with open("config/search_targets.json", "r") as f:
        return json.load(f)

def run_pipeline():
    config = load_config()
    roles = config["target_roles"]
    
    # Read target accounts generated from your property harvesters
    with open("target_companies.csv", mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            company_name = row["PARENT_ENTITY"]
            city = row["CITY"]
            
            # Matrix execution: Search every target role for this specific company
            for role in roles:
                print(f"Searching for {role} at {company_name}...")
                
                # 1. Gather raw data matches
                raw_matches = google_xray_search(company_name, role)
                
                for match in raw_matches:
                    # 2. Map data into your scalable Lead Model
                    # (Assuming your scraper extracts lists of available emails/phones)
                    lead = LeadModel(
                        first_name=match["first_name"],
                        last_name=match["last_name"],
                        company=company_name,
                        roles=[role],
                        emails=match.get("found_emails", []),
                        phones=match.get("found_phones", []),
                        linkedin_url=match.get("profile_url"),
                        city=city
                    )
                    
                    # 3. Securely push the normalized payload to Salesforce
                    push_to_salesforce(lead.to_salesforce_payload())

if __name__ == "__main__":
    run_pipeline()

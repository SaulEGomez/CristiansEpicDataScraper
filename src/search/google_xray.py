# src/search/google_xray.py

from bs4 import BeautifulSoup
import requests
import urllib.parse
import time

def extract_name_from_title(title_text):
    """A simple helper to split 'John Doe - Chief Engineer - Kaiser...' into first/last name."""
    clean_title = title_text.split(" - ")[0] # Usually grabs just the name
    parts = clean_title.split()
    
    first_name = parts[0] if len(parts) > 0 else "Unknown"
    last_name = " ".join(parts[1:]) if len(parts) > 1 else "Unknown"
    
    return first_name, last_name

def google_xray_search(company_name, target_role):
    """
    Executes a Google X-Ray search to find LinkedIn profiles matching the company and role.
    Returns a list of dictionaries ready to be mapped to the LeadModel.
    """
    # Construct the X-Ray query (assuming California focus as per initial criteria)
    query = f'site:linkedin.com/in/ "{company_name}" "{target_role}" "California"'
    escaped_query = urllib.parse.quote_plus(query)
    
    url = f"https://www.google.com/search?q={escaped_query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error during X-Ray search: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    leads = []
    
    # Parse standard Google search result blocks ('g' class)
    for g in soup.find_all('div', class_='g'):
        anchors = g.find_all('a')
        if anchors:
            link = anchors[0]['href']
            title_text = g.find('h3').text if g.find('h3') else ""
            
            if "linkedin.com/in/" in link:
                first_name, last_name = extract_name_from_title(title_text)
                
                leads.append({
                    "first_name": first_name,
                    "last_name": last_name,
                    "profile_url": link,
                    # These would ideally be populated by an email discovery API later, 
                    # but we initialize them as empty lists for the LeadModel to handle.
                    "found_emails": [], 
                    "found_phones": []
                })
                
    # Be polite to Google to avoid IP bans
    time.sleep(2) 
    
    return leads

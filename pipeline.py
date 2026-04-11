import os
import requests
import json

# 1. Pull the secret from the Codespace environment
JOOBLE_KEY = os.getenv("JOOBLE_API_KEY")

if not JOOBLE_KEY:
    raise ValueError("Missing JOOBLE_API_KEY! Check your Codespace Secrets.")

# 2. Set up the Jooble API request
url = f"https://jooble.org/api/{JOOBLE_KEY}"
headers = {"Content-Type": "application/json"}

# You can change the location to your specific country/city
payload = {
    "keywords": "Data Scientist",
    "location": "Remote", 
    "page": 1
}

def fetch_jobs():
    print("Fetching jobs from Jooble...")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        jobs = data.get('jobs', [])
        print(f"✅ Successfully found {len(jobs)} jobs!")
        
        # Let's peek at the first job's snippet
        if jobs:
            print("\n--- First Job Snippet ---")
            print(f"Title: {jobs[0]['title']}")
            print(f"Snippet: {jobs[0]['snippet']}")
            print("-------------------------\n")
            
        return jobs
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return []

if __name__ == "__main__":
    # Run the test
    raw_jobs = fetch_jobs()
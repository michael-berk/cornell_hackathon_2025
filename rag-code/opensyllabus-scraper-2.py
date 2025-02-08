import requests
import json
import pandas as pd

# API URL with Query Parameters
API_URL = "https://api.opensyllabus.org/api/titles/"
PARAMS = {
    "format": "json",
    "size": 100,
    "syllabus_query": "economics",
    "work_publication_types": "article",
    "work_query": "Economics",
    "institution_ids": [
        19400, 18810, 20148, 19397, 19233, 20220, 19304, 20912
    ]
}

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_data():
    """
    Fetches article data from the Open Syllabus API.
    """
    try:
        response = requests.get(API_URL, params=PARAMS, headers=HEADERS)

        # Check for HTTP errors
        if response.status_code != 200:
            print(f"❌ Error: API request failed with status {response.status_code}")
            print(f"Response text: {response.text}")
            return []

        # Try parsing JSON response
        data = response.json()

        # Extract 'works' from response
        return data.get("works", [])

    except json.JSONDecodeError:
        print("❌ Error: Failed to decode JSON response.")
        return []
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return []

def extract_data(articles):
    """
    Extracts relevant information from the fetched API data.
    """
    extracted_data = []
    for article in articles:
        extracted_data.append({
            "Title": article.get("title", "Unknown"),
            "Authors": [author.get("display_name", "Unknown") for author in article.get("authors", [])],
            "Year": article.get("year", "N/A"),
            "Citation Count": article.get("citation_count", "N/A"),
            "Source URLs": article.get("urls", []),
        })
    return extracted_data

# Fetch data
raw_data = fetch_data()

# Extract useful details
structured_data = extract_data(raw_data)

# Save to JSON
json_filename = "open_syllabus_economics_articles.json"
with open(json_filename, "w") as f:
    json.dump(structured_data, f, indent=4)

# Save to CSV
csv_filename = "open_syllabus_economics_articles.csv"
df = pd.DataFrame(structured_data)
df.to_csv(csv_filename, index=False)

print(f"✅ Scraped {len(structured_data)} records.")
print(f"📂 Data saved as: {json_filename}, {csv_filename}")

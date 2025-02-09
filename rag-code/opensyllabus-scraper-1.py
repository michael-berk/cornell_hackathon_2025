import requests
import time
import json
import pandas as pd


# API Configuration
BASE_URL = "https://api.opensyllabus.org/api/titles/"
QUERY = "Economics"  # Change this to any subject you're interested in
PAGE_SIZE = 100  # Max results per request

def fetch_titles(query, page_size=100):
    """
    Fetch titles from Open Syllabus API based on the given query.
    """
    all_results = []

    params = {
        "format": "json",
        "size": page_size,
        "work_query": query  # Corrected: Removed 'from'
    }

    headers = {
        "User-Agent": "Mozilla/5.0"  # Mimic a browser request
    }

    # Construct full URL for debugging
    full_url = f"{BASE_URL}?format=json&size={page_size}&work_query={query}"
    print(f"Requesting URL: {full_url}")

    response = requests.get(BASE_URL, params=params, headers=headers)

    if response.status_code == 400:
        print("Error 400: Bad Request")
        print("Response:", response.text)
        return []

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []

    data = response.json()

    # Extract and store the results
    results = data.get("works", [])
    all_results.extend(results)

    print(f"Fetched {len(results)} records.")

    return all_results

def extract_data(books):
    """
    Extracts relevant information from the fetched API data.
    """
    extracted_data = []
    for book in books:
        extracted_data.append({
            "Title": book.get("title", "Unknown"),
            "Subtitle": book.get("subtitle", ""),
            "Authors": [author.get("display_name", "Unknown") for author in book.get("authors", [])],
            "Year": book.get("year", "N/A"),
            "ISBNs": book.get("isbns", []),
            "Publication Type": book.get("publication_type", ""),
            "Rank": book.get("rank", "N/A"),
            "Citation Count": book.get("citation_count", "N/A"),
            "Image URLs": book.get("image_urls", []),
            "Source URLs": book.get("urls", []),
        })

    return extracted_data

# Fetch all titles for the given query
raw_data = fetch_titles(QUERY)

# Extract useful details
structured_data = extract_data(raw_data)

# Save to a JSON file
output_file = "open_syllabus_economics.json"
with open(output_file, "w") as f:
    json.dump(structured_data, f, indent=4)

print(f"Scraped {len(structured_data)} records and saved to '{output_file}'.")

# Display the extracted data in a structured table
df = pd.DataFrame(structured_data)


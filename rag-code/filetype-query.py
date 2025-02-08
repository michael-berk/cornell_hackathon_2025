import requests
import json
import time

# Path to the JSON file
json_filename = "open_syllabus_economics_articles.json"

# Headers to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# Counters
pdf_count = 0
website_count = 0
unknown_count = 0
total_urls = 0

def check_url_type(url):
    """ Pings a URL to determine if it is a PDF or a website with a timeout and error handling. """
    global pdf_count, website_count, unknown_count, total_urls
    total_urls += 1

    try:
        response = requests.head(url, allow_redirects=True, headers=HEADERS, timeout=5)  # Timeout added
        content_type = response.headers.get("Content-Type", "")

        if "pdf" in content_type:
            pdf_count += 1
            return "PDF File"
        elif "html" in content_type or "text" in content_type:
            website_count += 1
            return "Website"
        else:
            unknown_count += 1
            return f"Unknown ({content_type})"
    except requests.Timeout:
        unknown_count += 1
        return "Timeout"
    except requests.RequestException:
        unknown_count += 1
        return "Unreachable"

def process_json():
    """ Reads the JSON file and checks URL types. """
    with open(json_filename, "r") as file:
        data = json.load(file)

    for entry in data:
        title = entry.get("Title", "Unknown Title")
        urls = entry.get("Source URLs")

        # Skip if URLs is null
        if urls is None:
            print("null URL, skipping")
            continue

        print(f"\n🔍 Checking: {title}")
        for url in urls:
            result = check_url_type(url)
            print(f"   - {url}: {result}")
            time.sleep(0.5)  # Rate limit to prevent hitting servers too fast

    # Summary Statistics
    print("\n📊 **Summary Statistics** 📊")
    print(f"Total URLs Processed: {total_urls}")
    print(f"PDFs Found: {pdf_count}")
    print(f"Websites Found: {website_count}")
    print(f"Unknown/Unreachable: {unknown_count}")
    
    # Calculate and print ratio
    if website_count > 0:
        ratio = pdf_count / website_count
        print(f"📈 PDF-to-Website Ratio: {ratio:.2f}")
    else:
        print("📈 No websites found, cannot calculate ratio.")

# Run the script
process_json()
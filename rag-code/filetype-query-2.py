import requests
import time

# Path to the input text file containing URLs
input_filename = "pdf-links-cleaned-1.txt"  # Update this with the actual file path

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
    """ Pings a URL to determine if it is a PDF file or a website. """
    global pdf_count, website_count, unknown_count, total_urls
    total_urls += 1

    try:
        response = requests.head(url.strip(), allow_redirects=True, headers=HEADERS, timeout=5)
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

def process_urls_from_file(input_file):
    """ Reads URLs from a text file and determines if each is a PDF file. """
    with open(input_file, "r") as file:
        urls = file.readlines()

    for url in urls:
        url = url.strip()
        if not url:
            continue  # Skip empty lines

        result = check_url_type(url)
        print(f"{url}: {result}")
        time.sleep(0.5)  # Rate limit to avoid overwhelming servers

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
process_urls_from_file(input_filename)

import requests
import fitz  # PyMuPDF
import json
import pandas as pd
import os

# Path to input file containing PDF URLs (one per line)
input_filename = "pdf-links-cleaned-1.txt"  # Replace with actual file path

# Output folders
output_text_dir = "pdf_text_output"
os.makedirs(output_text_dir, exist_ok=True)

# List to store extracted text for CSV/JSON
extracted_data = []

def download_pdf(url):
    """ Downloads a PDF from a URL and saves it temporarily. """
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        pdf_path = os.path.join(output_text_dir, os.path.basename(url).replace("/", "_") + ".pdf")
        with open(pdf_path, "wb") as pdf_file:
            pdf_file.write(response.content)

        return pdf_path
    except requests.RequestException as e:
        print(f"❌ Failed to download {url}: {e}")
        return None

def extract_text_from_pdf(pdf_path):
    """ Extracts text from a PDF using PyMuPDF. """
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text.strip()
    except Exception as e:
        print(f"❌ Failed to extract text from {pdf_path}: {e}")
        return None

def process_pdfs(input_file):
    """ Reads URLs from file, downloads PDFs, extracts text, and saves it. """
    with open(input_file, "r") as file:
        urls = [line.strip() for line in file if line.strip()]

    for url in urls:
        print(f"🔍 Processing: {url}")
        pdf_path = download_pdf(url)
        if not pdf_path:
            continue

        extracted_text = extract_text_from_pdf(pdf_path)
        if not extracted_text:
            continue

        # Save as .txt
        txt_filename = os.path.join(output_text_dir, os.path.basename(pdf_path).replace(".pdf", ".txt"))
        with open(txt_filename, "w", encoding="utf-8") as txt_file:
            txt_file.write(extracted_text)

        # Store for JSON/CSV output
        extracted_data.append({"url": url, "text": extracted_text})

    # Save JSON Output
    # json_filename = os.path.join(output_text_dir, "pdf_text_output.json")
    # with open(json_filename, "w", encoding="utf-8") as json_file:
    #     json.dump(extracted_data, json_file, indent=4)

    # # Save CSV Output
    # csv_filename = os.path.join(output_text_dir, "pdf_text_output.csv")
    # df = pd.DataFrame(extracted_data)
    # df.to_csv(csv_filename, index=False)

    print(f"\n✅ Extraction Complete! Data saved in '{output_text_dir}'")

# Run the script
process_pdfs(input_filename)

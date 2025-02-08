import re

# Path to input and output files
input_filename = "pdf-results-input.txt"  # Replace with actual file path if needed
output_filename = "pdf_links_extracted.txt"

def extract_pdf_lines(input_file, output_file):
    """ Extracts lines ending with ': PDF File' and writes them to a new file. """
    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            if re.search(r": PDF File\s*$", line):  # Match lines ending with ': PDF File'
                outfile.write(line)

# Run the extraction
extract_pdf_lines(input_filename, output_filename)

print(f"✅ Extracted PDF links saved to: {output_filename}")

import os
import json
from utils import extract_outline  # Ensure this function is implemented correctly in utils.py

# Define input and output directory paths
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_pdfs():
    for index, filename in enumerate(os.listdir(INPUT_DIR), start=1):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, filename)
            output_filename = f"file{index:02}.json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)

            result = extract_outline(pdf_path)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"Processed {filename} → {output_filename}")

if __name__ == "__main__":
    process_pdfs()

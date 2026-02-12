import requests
import os

API_KEY = "069eafd5-a708-4de3-b8d6-1329c6b4ca25"
PDF_FILE = "ITC_2025.pdf"
OUTPUT_FILE = "output.md"

url = "https://api.pdfrest.com/markdown"

headers = {
    "Api-Key": API_KEY
}

with open(PDF_FILE, "rb") as f:
    files = {
        "file": (os.path.basename(PDF_FILE), f, "application/pdf")
    }

    print("Uploading PDF...")
    response = requests.post(url, headers=headers, files=files)

print("Status Code:", response.status_code)

if response.status_code != 200:
    print("Error Response:")
    print(response.text)
    exit()

result = response.json()

# pdfRest usually returns a download URL
download_url = result.get("file") or result.get("outputUrl")

if not download_url:
    print("Unexpected response:", result)
    exit()

print("Downloading Markdown file...")

md_response = requests.get(download_url)

with open(OUTPUT_FILE, "wb") as f:
    f.write(md_response.content)

print("✅ Done! Saved as", OUTPUT_FILE)

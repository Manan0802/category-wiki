import urllib.request
import os

url = "https://docs.google.com/spreadsheets/d/1pgWGX7_G18RF2NXSm0EwrzlHnIam6mNiubSZJVT0qUU/export?format=csv"
output_file = "calls_data.csv"

try:
    print(f"Downloading CSV from {url}...")
    urllib.request.urlretrieve(url, output_file)
    print(f"Successfully downloaded to {output_file}")
    print(f"File size: {os.path.getsize(output_file)} bytes")
except Exception as e:
    print(f"Error downloading file: {e}")

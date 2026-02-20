import requests
import json

url = "http://127.0.0.1:16666/food-analysis/recognize"
file_path = "backend/data/test_salad.jpg"

print(f"Uploading {file_path} to {url}...")

with open(file_path, "rb") as f:
    files = {"file": ("test_salad.jpg", f, "image/jpeg")}
    response = requests.post(url, files=files)

if response.status_code == 200:
    print("Test successful!")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
else:
    print(f"Test failed with status {response.status_code}")
    print(response.text)

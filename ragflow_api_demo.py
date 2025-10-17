import requests

API_URL = "http://localhost:5000"
API_KEY = "<your-api-key>"  # If required

headers = {
    "Content-Type": "application/json",
    # "X-API-KEY": API_KEY,  # Uncomment if needed
}

def completion(prompt, model="default"):
    resp = requests.post(f"{API_URL}/completion", headers=headers, json={"prompt": prompt, "model": model})
    print("Completion Response:", resp.json())

def ingest(file_path):
    with open(file_path, "rb") as f:
        files = {"file": f}
        resp = requests.post(f"{API_URL}/ingest", files=files)
        print("Ingest Response:", resp.json())

def retrieval(query, top_k=3, metadata=None):
    payload = {"query": query, "top_k": top_k, "metadata": metadata or {}}
    resp = requests.post(f"{API_URL}/retrieval", headers=headers, json=payload)
    print("Retrieval Response:", resp.json())

if __name__ == "__main__":
    completion("Hello, world!")
    # ingest("/path/to/your/document.pdf")
    # retrieval("example", top_k=3)

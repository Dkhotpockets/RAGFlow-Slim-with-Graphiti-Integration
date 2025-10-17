"""
Ragflow Slim CLI Wrapper
Contributor-safe, modular CLI for document ingestion and retrieval
"""
import argparse
import requests
import os

def ingest_file(file_path, api_url):
    ext = file_path.lower().rsplit('.', 1)[-1]
    if ext not in ('txt', 'pdf'):
        print(f"Unsupported file type: {ext}")
        return
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        resp = requests.post(f"{api_url}/ingest", files=files)
    print(resp.json())

def retrieve(query, api_url, top_k=3):
    payload = {'query': query, 'top_k': top_k}
    resp = requests.post(f"{api_url}/retrieval", json=payload)
    print(resp.json())

def main():
    parser = argparse.ArgumentParser(description="Ragflow Slim CLI")
    subparsers = parser.add_subparsers(dest='command')

    ingest_parser = subparsers.add_parser('ingest', help='Ingest a document')
    ingest_parser.add_argument('file', help='Path to txt or pdf file')
    ingest_parser.add_argument('--api', default='http://localhost:5000', help='API base URL')

    retrieve_parser = subparsers.add_parser('retrieve', help='Retrieve relevant docs')
    retrieve_parser.add_argument('query', help='Query string')
    retrieve_parser.add_argument('--top_k', type=int, default=3, help='Number of results')
    retrieve_parser.add_argument('--api', default='http://localhost:5000', help='API base URL')

    args = parser.parse_args()
    if args.command == 'ingest':
        ingest_file(args.file, args.api)
    elif args.command == 'retrieve':
        retrieve(args.query, args.api, args.top_k)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

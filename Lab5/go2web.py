import argparse
import requests
from bs4 import BeautifulSoup
import json

# File to store cache data
CACHE_FILE = "cache.json"

# Load cache from file
try:
    with open(CACHE_FILE, 'r') as f:
        cache = json.load(f)
except FileNotFoundError:
    cache = {}

def save_cache():
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def print_cache():
    print("Cache Contents:")
    for url, data in cache.items():
        print(f"URL: {url}")
        print(f"Data: {data}")
        print("---------------------------------------")

def make_request(url, content_type='html'):
    if url in cache:
        return cache[url]

    response = requests.get(url)
    try:
        if content_type == 'json':
            data = response.json()
        else:
            soup = BeautifulSoup(response.text, 'html.parser')
            data = soup.get_text()
    except ValueError:
        # If JSON decoding fails, treat the response as HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        data = soup.get_text()
    cache[url] = data
    save_cache()
    return data

def search(term):
    search_url = f"https://www.google.md/search?q={term}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print("\nTop 10 Responses\n---------------------------------------------------------------------")
    # Extract top 10 results and print them
    for i, result in enumerate(soup.find_all('a')[16:26], start=1):
        print(f"{i}. {result.text} - {result['href']}")
        print("---------------------------------------------------------------------")
        
def main():
    parser = argparse.ArgumentParser(description="CLI program for making HTTP requests and displaying responses")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--url", help="Make an HTTP request to the specified URL")
    group.add_argument("-s", "--search", help="Make an HTTP request to search the term using your favorite search engine")
    group.add_argument("-p", "--print-cache", action="store_true", help="Print the contents of the cache")
    parser.add_argument("-j", "--json", action="store_true", help="Request JSON content instead of HTML")

    args = parser.parse_args()

    content_type = 'json' if args.json else 'html'

    if args.print_cache:
        print_cache()
    elif args.url:
        response = make_request(args.url, content_type)
        print(response)
    elif args.search:
        search(args.search)

if __name__ == "__main__":
    main()

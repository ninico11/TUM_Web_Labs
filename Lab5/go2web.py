import argparse
import requests
from bs4 import BeautifulSoup

def make_request(url):
    response = requests.get(url)
    return response.text

def search(term):
    search_url = f"https://www.google.md/search?q={term}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Extract top 10 results and print them
    for i, result in enumerate(soup.find_all('a')[16:26], start=1):
        print(f"{i}. {result.text} - {result['href']}")

def main():
    parser = argparse.ArgumentParser(description="CLI program for making HTTP requests and displaying responses")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", "--url", help="Make an HTTP request to the specified URL")
    group.add_argument("-s", "--search", help="Make an HTTP request to search the term using your favorite search engine")

    args = parser.parse_args()

    if args.url:
        response = make_request(args.url)
        print(response)
    elif args.search:
        search(args.search)

if __name__ == "__main__":
    main()

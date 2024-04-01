import argparse
import socket
from bs4 import BeautifulSoup
import json
import ssl


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

def make_request(url, content_type='html', depth=0):
    if url in cache:
        return cache[url]
    # Extract host and path from URL
    url_parts = url.split('/')
    host, path = url_parts[2], '/' + '/'.join(url_parts[3:])

    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Wrap the socket with SSL/TLS context
        context = ssl.create_default_context()
        with context.wrap_socket(s, server_hostname=host) as ssl_socket:
            # Connect to the server
            ssl_socket.connect((host, 443))

            # Construct HTTP request
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"

            # Send the request
            ssl_socket.sendall(request.encode())

            # Receive response
            response = b""
            while True:
                data = ssl_socket.recv(4096)
                if not data:
                    break
                response += data

    # Decode response
    response_text = response.decode("latin-1")

    # Extract content based on content type
    if content_type == 'json':
        # Assuming JSON content is returned directly
        data = json.loads(response_text.split('\r\n\r\n', 1)[1])
    else:
        # Extracting HTML content
        soup = BeautifulSoup(response_text.split('\r\n\r\n', 1)[1], 'html.parser')
        data = soup.get_text()
    cache[url] = data
    save_cache()
    return data


def search(term):
    # Prepare the search query
    query = f"GET /search?q={term} HTTP/1.1\r\nHost: www.google.com\r\n\r\n"

    # Create a TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("www.google.com", 80))

        # Send the request
        s.sendall(query.encode())

        # Receive response
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data

    # Decode response
    response_text = response.decode("latin-1")

    # Extract relevant information from the response
    soup = BeautifulSoup(response_text.split('\r\n\r\n', 1)[1], 'html.parser')
    print("\nTop 10 Responses\n---------------------------------------------------------------------")
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

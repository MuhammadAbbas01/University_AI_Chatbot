import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import re

# Set the base URL and the directory to save the data
base_url = 'https://uom.edu.pk'
# The output directory will be created inside your Codespace
output_dir = 'university_data'

# A set to store visited URLs to avoid infinite loops and duplicate scraping
visited_urls = set()

# A list to store the URLs of PDF files
pdf_links = []

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

def is_valid(url):
    """
    Check if a URL is valid and belongs to the same domain.
    """
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https'] and parsed.netloc == urlparse(base_url).netloc

def get_all_links(url):
    """
    Fetch a page and get all valid links from it.
    """
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status() # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')
        links = set()
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            full_url = urljoin(url, href)
            # Remove anchor part of URL
            if '#' in full_url:
                full_url = full_url.split('#')[0]

            if is_valid(full_url) and full_url not in visited_urls:
                links.add(full_url)
        
        # Add the current URL to visited set before returning
        visited_urls.add(url)
        return list(links), soup
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return [], None

def save_content(url, content):
    """
    Save the extracted text content of a page to a file.
    """
    path = urlparse(url).path
    filename = path.strip('/').replace('/', '_') or 'index'
    filepath = os.path.join(output_dir, f"{filename}.txt")
    
    # Simple check to avoid overwriting files, can be more robust
    if not os.path.exists(filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved content from {url} to {filepath}")
    else:
        print(f"File already exists, skipping: {filepath}")

def find_pdfs(soup, url):
    """
    Find and store links to PDF files.
    """
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(url, href)
        if full_url.lower().endswith('.pdf'):
            if full_url not in pdf_links:
                pdf_links.append(full_url)
                print(f"Found PDF link: {full_url}")

def crawl(start_url):
    """
    Main crawling function to start the process.
    """
    queue = [start_url]
    visited_urls.add(start_url)
    
    while queue:
        current_url = queue.pop(0)
        print(f"Crawling: {current_url}")
        
        links, soup = get_all_links(current_url)
        if soup:
            # Extract text from the page
            page_text = ' '.join([p.text for p in soup.find_all('p')])
            # Clean up extra whitespace and newlines
            page_text = re.sub(r'\s+', ' ', page_text).strip()
            
            if page_text:
                save_content(current_url, page_text)
            
            # Find PDFs
            find_pdfs(soup, current_url)

            # Add new links to the queue
            for link in links:
                if link not in visited_urls:
                    visited_urls.add(link)
                    queue.append(link)

# Start the crawling process
print("Starting the web scraper...")
crawl(base_url)
print("\nScraping complete!")
print(f"Found {len(visited_urls)} total pages.")
print(f"Found {len(pdf_links)} PDF links.")

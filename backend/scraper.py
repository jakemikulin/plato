import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm import tqdm

# Define website URL & output directory
BASE_URL = "https://www.sortedmentalhealth.app/"  # Replace with your target website
OUTPUT_DIR = "docs/"  # Where to save text files
MAX_DEPTH = 2  # Set depth limit for crawling

visited_urls = set()

def save_text(content, title):
    """Save extracted text to a .txt file"""
    filename = os.path.join(OUTPUT_DIR, f"{title}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

def extract_text(url, depth=0):
    """Extract text from a webpage & save it"""
    if depth > MAX_DEPTH or url in visited_urls:
        return
    visited_urls.add(url)

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract visible text
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text() for p in paragraphs if p.get_text().strip()])
        
        if text:
            title = soup.title.string if soup.title else url.split("/")[-1]
            save_text(text, title)
            print(f"✅ Saved: {title}")
        
        # Find internal links & crawl deeper
        for link in soup.find_all("a", href=True):
            next_url = urljoin(url, link["href"])
            if BASE_URL in next_url:
                extract_text(next_url, depth + 1)

    except Exception as e:
        print(f"⚠️ Failed to process {url}: {e}")

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    extract_text(BASE_URL)
    print("✅ All pages scraped & saved as text.")
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
import json
import time
import re


def clean_text(text):
    """Remove non-breaking spaces and extra whitespace."""
    return re.sub(r'\s+', ' ', text.replace('\xa0', ' ')).strip()


def scrape_agnos_forum(max_pages=5):
    """
    Scrape forum posts from Agnos Health Forum.
    Returns a list of documents: {title, content, url}
    """
    base_url = "https://www.agnoshealth.com/forums"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    documents = []
    visited = set()

    try:
        # Scrape the main forum listing
        for page in range(1, max_pages + 1):
            url = base_url if page == 1 else f"{base_url}?page={page}"
            print(f"Scraping page {page}: {url}")

            try:
                resp = requests.get(url, headers=headers, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                print(f"  Failed to fetch page {page}: {e}")
                break

            soup = BeautifulSoup(resp.text, 'html.parser')

            # Find all links that look like forum topic posts
            links = soup.find_all('a', href=True)
            topic_links = []
            for link in links:
                href = link['href']
                full_url = urljoin(base_url, href)
                text = clean_text(link.get_text())
                # Filter for topic-like URLs (contain path segments after /forums/)
                if (
                    '/forums/' in full_url
                    and full_url not in visited
                    and len(full_url) > len(base_url) + 5
                    and text and len(text) > 5
                ):
                    topic_links.append((full_url, text))
                    visited.add(full_url)

            print(f"  Found {len(topic_links)} topic links")

            for topic_url, title in topic_links:
                try:
                    time.sleep(0.3)  # Be polite
                    topic_resp = requests.get(topic_url, headers=headers, timeout=10)
                    topic_soup = BeautifulSoup(topic_resp.text, 'html.parser')

                    # Try to get main content text
                    content_tag = (
                        topic_soup.find('article')
                        or topic_soup.find('div', class_=re.compile(r'content|post|body', re.I))
                        or topic_soup.find('main')
                    )
                    content = clean_text(content_tag.get_text()) if content_tag else ""

                    # Fallback: paragraph text
                    if not content:
                        paragraphs = topic_soup.find_all('p')
                        content = ' '.join(clean_text(p.get_text()) for p in paragraphs if len(p.get_text()) > 20)

                    documents.append({
                        "title": clean_text(title),
                        "content": content[:1000],  # Cap at 1000 chars
                        "url": topic_url
                    })
                except Exception as e:
                    # Still add with title only
                    documents.append({
                        "title": clean_text(title),
                        "content": "",
                        "url": topic_url
                    })

            if not topic_links:
                break  # No more pages

    except Exception as e:
        print(f"Scraping error: {e}")

    # Deduplicate by URL
    seen_urls = set()
    unique_docs = []
    for doc in documents:
        if doc['url'] not in seen_urls and doc['title']:
            seen_urls.add(doc['url'])
            unique_docs.append(doc)

    return unique_docs


if __name__ == "__main__":
    print("Starting Agnos Forum scraper...")
    forum_data = scrape_agnos_forum(max_pages=3)
    print(f"\nScraped {len(forum_data)} unique items from forum.")

    # Save to file
    with open('forum_data.json', 'w', encoding='utf-8') as f:
        json.dump(forum_data, f, ensure_ascii=False, indent=2)
    print("Saved to forum_data.json")

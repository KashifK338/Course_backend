#blog_service.py
from googleapiclient.discovery import build
from config import GOOGLE_CSE_API_KEY, GOOGLE_CSE_CX
from readability import Document
import requests
from requests.exceptions import Timeout, HTTPError


def fetch_reading_content(query):
    """
    Search for online reading content (e.g., articles, tutorials, guides, research papers) relevant to the query.
    This function uses the Google Custom Search API and can handle articles and research papers.
    """
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_CSE_API_KEY)

        # Adjust the search query to bias results towards articles, tutorials, guides, or research papers.
        search_query = f"{query} article tutorial research paper"
        
        response = service.cse().list(q=search_query, cx=GOOGLE_CSE_CX, num=5).execute()

        reading_data = []
        for item in response.get("items", []):
            url = item.get("link")
            title = item.get("title", "").lower()
            snippet = item.get("snippet", "").lower()

            # Filter out irrelevant results based on title or snippet
            if not any(keyword in title or keyword in snippet for keyword in ['tutorial', 'guide', 'research', 'paper']):
                continue  # Skip irrelevant content

            try:
                content_response = requests.get(url, timeout=10)
                content_response.raise_for_status()
                
                # Extract the main content using readability
                doc = Document(content_response.text)
                content = doc.summary()
                title = doc.title() or item.get("title")

                # Check if the content is relevant (if it's empty or too short, discard it)
                if len(content.strip()) < 100 or 'error' in content.lower():
                    continue  # Skip empty or non-relevant content
                
                reading_data.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "content": content,
                })

            except Exception as inner_e:
                print(f"Error processing reading content from {url}: {inner_e}")

        if not reading_data:
            print(f"No relevant reading content found for query: {query}")

        return reading_data

    except Exception as e:
        print(f"Failed to fetch reading content for query {query}: {e}")
        return []

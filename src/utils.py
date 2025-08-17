import requests
from bs4 import BeautifulSoup


def get_uncyclopedia_page(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def helper(soup: BeautifulSoup, section_name: str, class_name: str) -> bool:
    h2_tag = None
    for h2 in soup.find_all('h2'):
        if section_name in h2.get_text():
            h2_tag = h2
            break
            
    if not h2_tag:
        print(f"Error: Could not find the '{section_name}' heading.")
        return []

    featured_article_content = h2_tag.find_next_sibling('div', class_=class_name)
    if not featured_article_content:
        print(f"Error: Could not find the content div for '{section_name}' section.")
        return []
    
    return featured_article_content
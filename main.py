from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

def get_uncyclopedia_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def get_featured_article_data(soup):
    featured_section = soup.select_one('.mp-panel.mp-green .mp-content')
    if not featured_section:
        return None

    title_element = featured_section.select_one('a')
    title = title_element.get('title', 'Title not found') if title_element else 'Title not found'

    image_element = featured_section.select_one('img')
    image_url = image_element.get('src') if image_element else None
    if image_url and image_url.startswith('//'):
        image_url = 'https:' + image_url

    paragraphs = featured_section.find_all('p')
    description_parts = []

    for p in paragraphs:
        text = p.get_text(separator=' ', strip=True)
        description_parts.append(text)

    description = '\n'.join(description_parts)
    description = description.replace(" .", ".").replace(" ,", ",").replace(" !", "!").replace(" ?", "?")

    other_text_container = featured_section.find('div', class_='mw-body') or featured_section.find('div', class_='mp-content')
    if other_text_container:
        for child in other_text_container.children:
            if child.name not in ['p', 'div']:
                text = child.get_text(strip=True)
                if text and text not in description:
                    if description.strip():
                        description += '\n' + text
                    else:
                        description += text
    print(description)        
    
    return {
        "title": title,
        "image_url": image_url,
        "description": description
    }

@app.get("/")
def read_root():
    return {"message": "Uncyclopedia API is running. Check /docs for endpoints."}

@app.get("/featured-article")
def get_featured_article():
    soup = get_uncyclopedia_page("https://en.uncyclopedia.co/wiki/Main_Page")
    if soup:
        article_data = get_featured_article_data(soup)
        if article_data:
            return article_data
    return {"error": "Could not retrieve featured article data."}
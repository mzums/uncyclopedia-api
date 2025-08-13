from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

app = FastAPI()

def get_uncyclopedia_page(url: str):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def get_featured_article_data(soup: BeautifulSoup) -> Dict:
    featured_section = soup.select_one('.mp-panel.mp-green .mp-content')
    if not featured_section:
        return {}

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
    
    other_text_container = featured_section.find('div', class_='mw-body') or featured_section
    if other_text_container:
        for child in other_text_container.children:
            if child.name not in ['p', 'div', 'ul']:
                text = child.get_text(strip=True)
                if text and text not in description:
                    if description.strip():
                        description += '\n' + text
                    else:
                        description += text
    
    description = description.replace('\n\n', '\n')

    return {
        "title": title,
        "image_url": image_url,
        "description": description
    }

def get_did_you_know_facts(soup: BeautifulSoup) -> List[str]:
    h2_tag = None
    for h2 in soup.find_all('h2'):
        if 'Did you know...' in h2.get_text():
            h2_tag = h2
            break
            
    if not h2_tag:
        print("Error: Could not find the 'Did you know...' heading.")
        return []

    did_you_know_content = h2_tag.find_next_sibling('div', class_='mp-content')
    if not did_you_know_content:
        print("Error: Could not find the content div for 'Did you know...' section.")
        return []

    list_items = did_you_know_content.find_all('li')

    extracted_facts = []
    for item in list_items:
        fact_text = item.get_text(strip=False)
        extracted_facts.append(fact_text)

    return extracted_facts

def get_news_data(soup: BeautifulSoup) -> List[List[str]]:
    h2_tag = None
    for h2 in soup.find_all('h2'):
        if 'In the news' in h2.get_text():
            h2_tag = h2
            break
            
    if not h2_tag:
        print("Error: Could not find the 'In the news' heading.")
        return []
    

    news_content = h2_tag.find_next_sibling('div', class_='mp-content')
    if not news_content:
        print("Error: Could not find the content div for 'Did you know...' section.")
        return []
    
    list_items = news_content.find_all('li')

    extracted_facts = []
    news = []
    for item in list_items:
        fact_text = item.get_text(strip=False)
        news.append(fact_text)

    extracted_facts.append(news)

    rest = news_content.find_all('p')

    paragraphs = []
    for item in rest:
        rest_text = item.get_text(strip=False)
        paragraphs.append(rest_text)
    extracted_facts.append(paragraphs)
    print(extracted_facts)

    return extracted_facts

def get_picture_data(soup: BeautifulSoup) -> Dict:
    h2_tag = None
    for h2 in soup.find_all('h2'):
        if 'Picture of the day' in h2.get_text():
            h2_tag = h2
            break

    if not h2_tag:
        print("Error: Could not find the 'Picture of the day' heading.")
        return {}
    
    picture_content = h2_tag.find_next_sibling('div', class_='mp-content')
    
    all_td_elements = picture_content.find_all('td')

    second_td_element = None
    if len(all_td_elements) > 1:
        second_td_element = all_td_elements[1]

    picture_data = {}
    
    if second_td_element:
        title = second_td_element.find(text=True, recursive=False).strip()
        picture_data["title"] = title
        
        credit_element = second_td_element.find('p')
        if credit_element:
            credit_link = credit_element.find('a', title=lambda x: 'User:' in x)
            if credit_link:
                credit_text = credit_link.get_text(strip=True)
                picture_data["image_credit"] = credit_text
            else:
                picture_data["image_credit"] = "Credit not found"
        else:
            picture_data["image_credit"] = "Credit not found"

    image_element = picture_content.select_one('img')
    image_url = image_element.get('src') if image_element else None
    if image_url and image_url.startswith('//'):
        image_url = 'https:' + image_url
    picture_data["image_url"] = image_url

    return picture_data

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

@app.get("/did-you-know")
def get_did_you_know():
    soup = get_uncyclopedia_page("https://en.uncyclopedia.co/wiki/Main_Page")
    if soup:
        facts = get_did_you_know_facts(soup)
        if facts:
            return facts
    return {"error": "Could not retrieve 'Did you know...' facts."}

@app.get("/news")
def get_news():
    soup = get_uncyclopedia_page("https://en.uncyclopedia.co/wiki/Main_Page")
    if soup:
        news = get_news_data(soup)
        if news:
            return news

@app.get("/picture")
def get_picture():
    soup = get_uncyclopedia_page("https://en.uncyclopedia.co/wiki/Main_Page")
    if soup:
        picture_data = get_picture_data(soup)
        if picture_data:
            return picture_data
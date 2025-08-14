from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime

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
    description = description.replace(" .", ".").replace(" ,", ",").replace(" !", "!").replace(" ?", "?").replace("( ", "(").replace(" )", ")")
    
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

def get_did_you_know_facts(soup: BeautifulSoup) -> Dict[str, List[List[str]]]:
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
        fact_text = item.get_text(strip=True)
        extracted_facts.append(fact_text)

    image_element = did_you_know_content.select_one('img')
    image_url = image_element.get('src') if image_element else None
    if image_url and image_url.startswith('//'):
        image_url = 'https:' + image_url

    return {
        "content": extracted_facts,
        "image_url": image_url
    }

def get_news_data(soup: BeautifulSoup) -> Dict[str, List[List[str]]]:
    h2_tag = None
    for h2 in soup.find_all('h2'):
        if 'In the news' in h2.get_text():
            h2_tag = h2
            break
            
    if not h2_tag:
        print("Error: Could not find the 'In the news' heading.")
        return {}
    
    news_content = h2_tag.find_next_sibling('div', class_='mp-content')
    if not news_content:
        print("Error: Could not find the content div for 'In the news' section.")
        return {}
    
    content_items = news_content.find_all(['li', 'p'])
    extracted_content = [item.get_text(strip=True) for item in content_items]

    image_element = news_content.select_one('img')
    image_url = image_element.get('src') if image_element else None
    if image_url and image_url.startswith('//'):
        image_url = 'https:' + image_url
        
    return {
        "content": extracted_content,
        "image_url": image_url
    }

def get_picture_data(soup: BeautifulSoup) -> Dict:
    h2_tag = None
    for h2 in soup.find_all('h2'):
        if 'Picture of the day' in h2.get_text():
            h2_tag = h2
            break

    if not h2_tag:
        return {}
    
    picture_content = h2_tag.find_next_sibling('div', class_='mp-content')
    if not picture_content:
        return {}
    
    all_td_elements = picture_content.find_all('td')

    second_td_element = None
    if len(all_td_elements) > 1:
        second_td_element = all_td_elements[1]

    picture_data = {}
    
    if second_td_element:
        credit_element = second_td_element.find('p')
        
        if credit_element:            
            credit_element.extract()
            title = second_td_element.get_text().rstrip()
            picture_data["title"] = title
            
            credit_link = credit_element.find('a', title=lambda x: x and 'User:' in x)
            if credit_link:
                picture_data["image_credit"] = credit_link.get_text(strip=True)
            else:
                picture_data["image_credit"] = "Credit not found"
        else:
            picture_data["title"] = second_td_element.get_text(strip=True)
            picture_data["image_credit"] = "Credit not found"

    image_element = picture_content.select_one('img')
    image_url = image_element.get('src') if image_element else None
    if image_url and image_url.startswith('//'):
        image_url = 'https:' + image_url
    picture_data["image_url"] = image_url

    return picture_data

def get_anniversary_data(soup: BeautifulSoup) -> Dict:
    h2_tag = None
    for h2 in soup.find_all('h2'):
        if "On this day" in h2.get_text():
            h2_tag = h2
            break

    if not h2_tag:
        return {"error": "Could not find the 'On this day' heading."}
    
    content_div = h2_tag.find_next_sibling('div', class_='mp-content')
    if not content_div:
        return {"error": "Could not find the content div for 'On this day' section."}

    date_line_b = content_div.find('b')
    date_info = date_line_b.get_text() if date_line_b else None
    
    description_parts = []
    if date_line_b:
        for sibling in date_line_b.next_siblings:
            if sibling.name == 'ul':
                break
            if isinstance(sibling, str):
                description_parts.append(sibling.strip())
            else:
                description_parts.append(sibling.get_text(strip=True))
                
    description = ''.join(description_parts).strip()
    if description[0] == ':':
        description = description[2:]
    
    anniversary_list = content_div.find_all('li')
    anniversaries = [li.get_text(separator=' ', strip=True) for li in anniversary_list]

    image_element = content_div.select_one('img')
    image_url = image_element.get('src') if image_element else None
    if image_url and image_url.startswith('//'):
        image_url = 'https:' + image_url

    return {
        "date_info": date_info,
        "description": description,
        "anniversaries": anniversaries,
        "image_url": image_url
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
        
@app.get("/anniversaries")
def get_anniversaries():
    soup = get_uncyclopedia_page("https://en.uncyclopedia.co/wiki/Main_Page")
    if soup:
        anniversaries = get_anniversary_data(soup)
        if anniversaries:
            return anniversaries

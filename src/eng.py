from bs4 import BeautifulSoup
from typing import List, Dict
from src.utils import helper

def get_featured_article_data(soup: BeautifulSoup) -> Dict:
    featured_article_content = helper(soup, 'featured article', 'mp-content')
    if not featured_article_content:
        return {"error": "Could not find the featured article content."}

    title_element = featured_article_content.select_one('a')
    title = title_element.get('title', 'Title not found') if title_element else 'Title not found'

    image_element = featured_article_content.select_one('img')
    image_url = image_element.get('src') if image_element else None
    if image_url and image_url.startswith('//'):
        image_url = 'https:' + image_url

    paragraphs = featured_article_content.find_all('p')
    description_parts = []

    for p in paragraphs:
        text = p.get_text(separator=' ', strip=True)
        description_parts.append(text)

    description = '\n'.join(description_parts)
    description = description.replace(" .", ".").replace(" ,", ",").replace(" !", "!").replace(" ?", "?").replace("( ", "(").replace(" )", ")")
    
    other_text_container = featured_article_content.find('div', class_='mw-body') or featured_article_content
    if other_text_container:
        for child in other_text_container.children:
            if child.name not in ['p', 'div', 'ul']:
                text = child.get_text(strip=True)
                if text and text not in description:
                    if description.strip():
                        description += '\n' + text
                    else:
                        description += text
    
    if description.endswith(" (Full article...)"):
        description = description.removesuffix(" (Full article...)").strip()
    
    description = description.replace('\n\n', '\n')

    return {
        "title": title,
        "image_url": image_url,
        "description": description
    }

def get_did_you_know_facts(soup: BeautifulSoup) -> Dict[str, List[List[str]]]:
    did_you_know_content = helper(soup, 'Did you know', 'mp-content')
    if not did_you_know_content:
        return {"error": "Could not find the 'Did you know...' section."}

    list_items = did_you_know_content.find_all('li')

    extracted_facts = []
    for item in list_items:
        fact_text = item.get_text()
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
    news_content = helper(soup, 'In the news', 'mp-content')
    if not news_content:
        return {"error": "Could not find the 'In the news' section."}

    news = news_content.find_all('li')
    news = [item.get_text().split('\n')[0] for item in news]

    ongoing = None
    recent_deaths = None
    upcoming_deaths = None
    for i in news_content.find_all('p'):
        text = i.get_text()
        text_list = text.split(sep=" ")
        if text_list[0] == "Ongoing:":
            text_list1 = text_list[1:]
        else:
            text_list1 = text_list[2:]
        text = " ".join(text_list1)
        text_list2 = text.split(sep=" • ")
        stripped = list(map(str.strip, text_list2))
        if text_list[0] == "Ongoing:":
            ongoing = stripped
        elif text_list[0] == "Recent":
            recent_deaths = stripped
        else:
            upcoming_deaths = stripped

    image_element = news_content.select_one('img')
    image_url = image_element.get('src') if image_element else None
    if image_url and image_url.startswith('//'):
        image_url = 'https:' + image_url

    image_desc_div = news_content.find('div', style=lambda s: s and 'font-size:94%' in s)
    image_description = image_desc_div.get_text(strip=True) if image_desc_div else None
    
    return {
        "content": news,
        "ongoing": ongoing,
        "recent_deaths": recent_deaths,
        "upcomming_deaths": upcoming_deaths,
        "image_url": image_url,
        "image_description": image_description
    }


def get_picture_data(soup: BeautifulSoup) -> Dict:
    picture_content = helper(soup, 'Picture of the day', 'mp-content')
    if not picture_content:
        return {"error": "Could not find the content div for 'Picture of the day' section."}

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

def get_on_this_day_data(soup: BeautifulSoup) -> Dict:
    content_div = helper(soup, 'On this day', 'mp-content')
    if not content_div:
        return {"error": "Could not find the content div for 'On this day' section."}

    date_line_b = content_div.find('b')
    date_info = date_line_b.get_text().removesuffix(':') if date_line_b else None
    
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
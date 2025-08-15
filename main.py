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

def get_featured_article_data(soup: BeautifulSoup) -> Dict:
    featured_article_content = helper(soup, 'Featured article', 'mp-content')
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

def get_anniversary_data(soup: BeautifulSoup) -> Dict:
    content_div = helper(soup, 'On this day', 'mp-content')
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

def get_madrosc_data(soup: BeautifulSoup) -> Dict:
    madrosc_content = helper(soup, 'Mądrość ze słownika', 'panelcss-content')
    if not madrosc_content:
        return {"error": "Could not find the content div for 'Mądrość ze słownika' section."}

    word_element = madrosc_content.find('b')
    word = word_element.get_text(strip=True)

    definition = ""
    for child in madrosc_content.children:
        if child.name not in ['p', 'div', 'ul']:
            text = child.get_text()
            if text and text not in definition:
                if definition.strip():
                    definition += '\n' + text
                else:
                    definition += text

    definition = definition.replace("Zobacz inne hasła", "").replace(f"{word} – ", "").strip()

    return {
        "word": word,
        "definition": definition
    }

def get_grafika_data(soup: BeautifulSoup) -> Dict:
    grafika_content = helper(soup, 'Losowa grafika', 'panelcss-content')
    if not grafika_content:
        return {"error": "Could not find the content div for 'Losowa grafika' section."}

    grafika_element = grafika_content.select_one('img')
    image_url = grafika_element.get('src') if grafika_element else None
    if not "nonsa.pl" in image_url and not "wikimedia" in image_url:
        image_url = "https://nonsa.pl" + image_url if image_url else None

    if image_url and image_url.startswith('//'):
        image_url = 'https:' + image_url

    image_alt = grafika_element.get('alt') if grafika_element else None

    author_div = grafika_content.find('div', style=lambda s: s and 'margin-top' in s)
    if author_div:
        if author_div.find('a', title=lambda t: t and ('User:' in t or 'commons:User' in t or 'Użytkownik:' in t)):
            author_link = author_div.find('a', title=lambda t: t and 'User:' in t or 'commons:User' in t or 'Użytkownik:' in t) if author_div else None
            author = author_link.get_text(strip=True)
        else:
            print(grafika_content)
            author_link = author_div.find('i')
            author = author_link.get_text(strip=True).removeprefix("Autor:")
    else:
        author_link = None
        author = "Autor unknown"

    return {
        "image_url": image_url,
        "image_alt": image_alt,
        "author": author
    }

def get_czy_nie_wiesz_data(soup: BeautifulSoup) -> Dict:
    content = helper(soup, 'Czy nie wiesz', 'panelcss-content')
    if not content:
        return {"error": "Could not find the content div for 'Czy nie wiesz' section."}

    res = {
        "najnowsze": [],
        "archiwa": []
    }

    najnowsze_header = content.find(string=lambda s: s and "Z najnowszych artykułów:" in s)
    if najnowsze_header:
        najnowsze_list = najnowsze_header.find_next('ul')
        if najnowsze_list:
            for li in najnowsze_list.find_all('li'):
                res["najnowsze"].append(li.get_text())

    archiwa_header = content.find(string=lambda s: s and "…i z naszych przepastnych archiwów:" in s)
    if archiwa_header:
        archiwa_list = archiwa_header.find_next('ul')
        if archiwa_list:
            for li in archiwa_list.find_all('li'):
                res["archiwa"].append(li.get_text())

    return res

def get_swieto_data(soup: BeautifulSoup) -> Dict:
    content = helper(soup, 'Święto na dziś', 'panelcss-content')
    if not content:
        return {"error": "Could not find the content div for 'Święto na dziś' section."}
    
    title_content = content.select_one('p').get_text()

    subtitle_p = content.find_all('p')[1] if len(content.find_all('p')) > 1 else None
    subtitle_content = subtitle_p.get_text() if subtitle_p else ""

    picture = content.select_one('img')
    image_url = picture.get('src') if picture else None
    if not "nonsa.pl" in image_url and not "wikimedia" in image_url:
        image_url = "https://nonsa.pl" + image_url if image_url else None

    dates = {}
    for i in content.find_all('li'):
        date_text = i.get_text()
        date = date_text.split(' – ')[0]
        event = "".join(date_text.split(' – ')[1:])
        dates[date] = event

    return {
        "title": title_content,
        "subtitle": subtitle_content,
        "events": dates,
        "image_url": image_url
    }

def get_non_news_data(soup: BeautifulSoup) -> Dict:
    content = helper(soup, 'NonNews', 'panelcss-content')
    if not content:
        return {"error": "Could not find the content div for 'NonNews' section."}
    
    non_news = {}
    non_news["najnowsze"] = []
    non_news["archiwum"] = []
    current = "najnowsze"
    last_date = None
    last_date_content = []
    for item in content.children:
        if item.name == 'p':
            if item.select_one('b'):
                current = "najnowsze" if "Najnowsze" in item.select_one('b').get_text() else "archiwum"
            if item:
                a_tag = item.select_one('a')
                last_date_content = []
                if a_tag:
                    date = a_tag.get_text()
                else:
                    continue
                last_date = date
        elif item.name == 'ul':
            print("ul")
            if last_date:
                for item2 in item.find_all('li'):
                    text = item2.select_one('a').get_text()
                    if text:
                        if current == "najnowsze" and len(non_news[current]) > 0 and non_news[current][-1]["date"] == last_date:
                            non_news[current][-1]["content"].append(text)
                        else:
                            last_date_content.append(text)
                            if current == "najnowsze":
                                non_news[current].append({
                                    "date": last_date,
                                    "content": last_date_content
                                })

    non_news[current].append(last_date_content)

    return non_news

def get_artykul_na_medal_data(soup: BeautifulSoup) -> Dict:
    content = helper(soup, 'Artykuł na medal', 'panelcss-content')
    if not content:
        return {"error": "Could not find the content div for 'Artykuł na medal' section."}

    article_title = content.select_one('p').select_one('b').get_text(strip=True)
    
    paragraphs = content.find_all('p')
    description_parts = []
    
    for p in paragraphs:
        text = p.get_text(separator=' ')
        description_parts.append(text.replace(" .", ".").replace(" ,", ",").replace(" !", "!").replace(" ?", "?").replace("( ", "(").replace(" )", ")"))

    description = '\n'.join(description_parts).rstrip()
    
    image_element = content.select_one('img')
    image_url = image_element.get('src') if image_element else None
    if image_url and not "nonsa.pl" in image_url and not "wikimedia" in image_url:
        image_url = "https://nonsa.pl" + image_url if image_url else None
    if image_url and image_url.startswith('//'):
        image_url = 'https:' + image_url

    return {
        "title": article_title,
        "description": description,
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

@app.get("/madrosc")
def get_madrosc():
    soup = get_uncyclopedia_page("https://nonsa.pl/wiki/Strona_g%C5%82%C3%B3wna")
    if soup:
        madrosc = get_madrosc_data(soup)
        if madrosc:
            return madrosc
        
@app.get("/losowa-grafika")
def get_grafika():
    soup = get_uncyclopedia_page("https://nonsa.pl/wiki/Strona_g%C5%82%C3%B3wna")
    if soup:
        grafika = get_grafika_data(soup)
        if grafika:
            return grafika
        
@app.get("/czy-nie-wiesz")
def get_czy_nie_wiesz():
    soup = get_uncyclopedia_page("https://nonsa.pl/wiki/Strona_g%C5%82%C3%B3wna")
    if soup:
        czy_nie_wiesz = get_czy_nie_wiesz_data(soup)
        if czy_nie_wiesz:
            return czy_nie_wiesz
        
@app.get("/swieto")
def get_swieto():
    soup = get_uncyclopedia_page("https://nonsa.pl/wiki/Strona_g%C5%82%C3%B3wna")
    if soup:
        swieto = get_swieto_data(soup)
        if swieto:
            return swieto

@app.get("/non-news")
def get_non_news():
    soup = get_uncyclopedia_page("https://nonsa.pl/wiki/Strona_g%C5%82%C3%B3wna")
    if soup:
        non_news = get_non_news_data(soup)
        if non_news:
            return non_news
        
@app.get("/artykul-na-medal")
def get_artykul_na_medal():
    soup = get_uncyclopedia_page("https://nonsa.pl/wiki/Strona_g%C5%82%C3%B3wna")
    if soup:
        artykul_na_medal = get_artykul_na_medal_data(soup)
        if artykul_na_medal:
            return artykul_na_medal
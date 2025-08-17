from bs4 import BeautifulSoup
from typing import Dict
from src.utils import helper


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
        "newest": [],
        "archive": []
    }

    najnowsze_header = content.find(string=lambda s: s and "Z najnowszych artykułów:" in s)
    if najnowsze_header:
        najnowsze_list = najnowsze_header.find_next('ul')
        if najnowsze_list:
            for li in najnowsze_list.find_all('li'):
                res["newest"].append(li.get_text())

    archiwa_header = content.find(string=lambda s: s and "…i z naszych przepastnych archiwów:" in s)
    if archiwa_header:
        archiwa_list = archiwa_header.find_next('ul')
        if archiwa_list:
            for li in archiwa_list.find_all('li'):
                res["archive"].append(li.get_text())

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
    non_news["newest"] = []
    non_news["archive"] = []
    current = "newest"
    last_date = None
    last_date_content = []
    for item in content.children:
        if item.name == 'p':
            if item.select_one('b'):
                current = "newest" if "Najnowsze" in item.select_one('b').get_text() else "archive"
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
                        if current == "newest" and len(non_news[current]) > 0 and non_news[current][-1]["date"] == last_date:
                            non_news[current][-1]["content"].append(text)
                        else:
                            last_date_content.append(text)
                            if current == "newest":
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
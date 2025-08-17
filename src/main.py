from fastapi import FastAPI
from src.eng import get_featured_article_data, get_did_you_know_facts, get_news_data, get_picture_data, get_on_this_day_data
from src.pl import get_madrosc_data, get_grafika_data, get_czy_nie_wiesz_data, get_swieto_data, get_non_news_data, get_artykul_na_medal_data
from src.utils import get_uncyclopedia_page

app = FastAPI()


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
        
@app.get("/on-this-day")
def get_on_this_day():
    soup = get_uncyclopedia_page("https://en.uncyclopedia.co/wiki/Main_Page")
    if soup:
        on_this_day = get_on_this_day_data(soup)
        if on_this_day:
            return on_this_day

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
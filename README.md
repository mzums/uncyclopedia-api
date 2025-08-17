# uncyclopedia-api
Fastapi API for Uncyclopedia and it's Polish alternative - Nonsensopedia

## [Uncyclopedia](https://en.uncyclopedia.co/wiki/Main_Page)
- **From today's featured article** (`/featured-article`)
    - title
    - content
    - image url
- **Did you know...** (`/did-you-know`)
    - content
    - image url
- **In the news** (`/news`)
    - content
    - ongoing
    - recent deaths
    - upcomming deaths
    - image url
    - image description
- **On this day** (`/on-this-day`)
    - date info
    - description
    - anniversaries
    - image url
- **Picture of the day** (`/picture`)
    - title
    - image credit
    - image url

## [Nonsensopedia](https://nonsa.pl/wiki/Strona_g%C5%82%C3%B3wna)
- **Artykuł na medal** (`/artykul-na-medal`)
    - title
    - description
    - image url
- **Święto na dziś** (`/swieto`)
    - title
    - subtitle
    - events
    - image url
- **NonNews** (`/non-news`)
    - newest
    - archive
- **Czy nie wiesz…** (`/czy-nie-wiesz`)
    - newest
    - archive
- **Losowa grafika** (`/losowa-grafika`)
    - image url
    - image alt
    - author
- **Mądrość ze słownika** (`/madrosc`)
    - word
    - definition

## Structure
- `src`:
    - `main.py` – main logic with endpoints
    - `eng.py` – function for getting data from Uncyclopedia
    - `pl.py` - function for getting data from Nonsensopedia
    - `utils.py` - helping functions
- `requirements.py` - required python libraries

---

## Local development
1. **clone** the repository  
    `git clone https://github.com/mzums/uncyclopedia-api.git`
2. **go to the project** directory  
    `cd uncyclopedia-api`
3. **install** requirements  
    `pip install -r requirements.txt`
4. **run** the app with uvicorn  
    ``uvicorn main:app --reload``
5. **use** the api on `http://127.0.0.1:8000`
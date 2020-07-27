import requests
import re
import json
from bs4 import BeautifulSoup
from data import load_disney, load_pixar
import pandas as pd
import time


def get_urls(movies, search_term):
    """ Get all rottentomatoes urls that match the movie's name """
    urls = []
    for movie in movies:
        print(movie)
        movie = movie.replace(" ", "%20")
        r = requests.get(f"https://www.rottentomatoes.com/search?search={movie}%20{search_term}")
        soup = BeautifulSoup(r.text, "html.parser")
        result = soup.find_all("script", id="movies-json")[0]
        result = json.loads(str(result).split('type="application/json">')[1].split("</script>")[0])

        if result["items"]:
            for item in result["items"][:4]:
                urls.append(item['url'])

        else:
            print("Empty...")
            r = requests.get(f"https://www.rottentomatoes.com/search?search={movie}")
            soup = BeautifulSoup(r.text, "html.parser")
            result = soup.find_all("script", id="movies-json")[0]
            result = json.loads(str(result).split('type="application/json">')[1].split("</script>")[0])

            if result["items"]:
                for item in result["items"][:4]:
                    urls.append(item['url'])
                    
    return urls


def get_movie_data(urls):
    """ Get movie data based on a RottenTomatoes url """
    df = pd.DataFrame(columns=["Title", "Audience_Score", "Audience_Rating", "Audience_Count", 
                           "Critic_Score", "Critic_Rating", "Release_Date"])
    
    for url in urls:
        print(url)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        result = soup.find_all("script", type="text/javascript")
        result = json.loads(str(result[0]).split("root.RottenTomatoes.context.scoreBoardViewModel = ")[1].split("\n")[0].replace(";", ""))

        # Get Data
        title = result.get("critics").get("title")
        audience_score = result.get("audience").get("score")
        audience_rating = result.get("audience").get("averageRating")
        audience_count = result.get("audience").get("ratingCount")

        critic_score = result.get("critics").get("score")
        critic_rating = result.get("critics").get("avgScore")

        release_date = result.get("releaseDate")

        df.loc[len(df)] = [title, audience_score, audience_rating, audience_count,
                           critic_score, critic_rating, release_date]
        time.sleep(1)
        
    return df


def scrape(save=True):
    """ Scrape Pixar and Disney movies from RottenTomatoes """
    disney, pixar = load_disney(), load_pixar()
    disney_urls = get_urls(disney, "disney")
    pixar_urls = get_urls(pixar, "disney")
    pixar_data = get_movie_data(pixar_urls)
    disney_data = get_movie_data(disney_urls)

    if save:
        disney_data.to_csv("../data/RottenTomatoes/disney_raw_new.csv", index=False)
        pixar_data.to_csv("../data/RottenTomatoes/pixar_raw_new.csv", index=False)
        
    return disney_data, pixar_data
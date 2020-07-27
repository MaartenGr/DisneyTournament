from data import load_disney, load_pixar
from imdb import IMDb
import pandas as pd


def scrape(save=False):
    """ Scrape pixar and disney movies from IMDB """
    disney_movies = load_disney()
    pixar_movies = load_pixar()
    ia = IMDb()

    pixar = scrape_pixar(pixar_movies, ia)
    disney = scrape_disney(disney_movies, ia)

    if save:
        pixar.to_csv("imdb_pixar_raw.csv", index=False)
        disney.to_csv("imdb_disney_raw.csv", index=False)

    return pixar, disney


def scrape_pixar(pixar_movies, ia):
    """ Scrape Pixar movies """
    df = pd.DataFrame(columns=["Title", "Genres", "Runtimes", "Countries", "Color info", "Aspect ration",
                               "Box office", "Original air date", "Rating", "Votes", "Languages", "Year",
                               "Kind", "Companies", "ID"])
    for pixar_movie in pixar_movies:

        # The movies from the search results
        movies = ia.search_movie(pixar_movie, results=7)

        for movie in movies:
            result = ia.get_movie(movie.movieID)

            # Check if any company contains Pixar in their name
            try:
                companies = [name['name'] for name in result["production companies"]]
                is_pixar = [True for company in companies if "Pixar" in company]

                if any(is_pixar):
                    print(result["title"])
                    df.loc[len(df)] = [result.get("title"),
                                       result.get("genres"),
                                       result.get("runtimes"),
                                       result.get("countries"),
                                       result.get("color info"),
                                       result.get("aspect ratio"),
                                       result.get("box office"),
                                       result.get("original air date"),
                                       result.get("rating"),
                                       result.get("votes"),
                                       result.get("languages"),
                                       result.get("year"),
                                       result.get("kind"),
                                       companies,
                                       movie.movieID]

            except KeyError:
                continue

    return df


def scrape_disney(disney_movies, ia):
    """ Scrape disney movies """
    df = pd.DataFrame(columns=["Title", "Genres", "Runtimes", "Countries", "Color info", "Aspect ration",
                               "Box office", "Original air date", "Rating", "Votes", "Languages", "Year",
                               "Kind", "Companies", "ID"])
    for disney_movie in disney_movies:

        # The movies from the search results
        movies = ia.search_movie(disney_movie, results=7)

        for movie in movies:
            result = ia.get_movie(movie.movieID)

            # Check if any company contains Disney in their name
            try:
                companies = [name['name'] for name in result["production companies"]]
                is_disney = [True for company in companies if "Disney" in company]

                if any(is_disney):
                    print(result["title"])
                    df.loc[len(df)] = [result.get("title"),
                                       result.get("genres"),
                                       result.get("runtimes"),
                                       result.get("countries"),
                                       result.get("color info"),
                                       result.get("aspect ratio"),
                                       result.get("box office"),
                                       result.get("original air date"),
                                       result.get("rating"),
                                       result.get("votes"),
                                       result.get("languages"),
                                       result.get("year"),
                                       result.get("kind"),
                                       companies,
                                       movie.movieID]

            except KeyError:
                continue

    return df

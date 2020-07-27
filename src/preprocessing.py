import pandas as pd
import json
import re 
import numpy as np
from sklearn import preprocessing
from scipy.stats import boxcox
from data import load_disney, load_pixar


def combine_rotten_and_imdb():
    """ Combine and return RottenTomatoes and IMDB datasets 
    
    Preprocessing steps:
        * Adjusts the Opening Weekend USA Box Office for inflation using CPI
        * Scale variables between 0 and 1 for comparison of values
        * Based on scaled variables, create a seed score
    """
    
    # Load rotten and imdb
    pixar, disney, total = preprocess_imdb_data()
    pixar_rotten, disney_rotten, total_rotten = preprocess_rotten_data()
    
    # combine rotten and imdb
    columns = ['Title', 'Rating', 'Votes', 'Year', 'Budget',
               'Cumulative Worldwide Gross', 'Opening_Weekend_USA', 'Yearly_Votes']
    total = total.loc[:, columns]
    total = total.rename(columns={'Rating':'I_Audience_Rating',
                                  'Votes': 'I_Audience_Votes'})

    total_rotten = total_rotten.rename(columns={'Audience_Score':'R_Audience_Score',
                                                'Audience_Rating': 'R_Audience_Rating',
                                                'Audience_Count': 'R_Audience_Count',
                                                'Audience_Rating': 'R_Audience_Rating',
                                                'Critic_Score': 'R_Critic_Score',
                                                'Critic_Rating': 'R_Critic_Rating'})
    total = total.merge(total_rotten, on=['Title']).copy()
    disney = total.loc[total.Company == "Disney", :].copy()
    pixar = total.loc[total.Company == "Pixar", :].copy()
    
    # Adjust for inflation
    cpi = pd.read_excel("../data/cpi.xlsx", names=["Year", "CPI"])
    pixar.loc[:, 'Opening_Weekend_USA_Adjusted'] = pixar.apply(lambda row: 
                                                               adjust_for_inflation(row, cpi,
                                                                                    column="Opening_Weekend_USA"), 1)
    disney.loc[:, 'Opening_Weekend_USA_Adjusted'] = disney.apply(lambda row: 
                                                                 adjust_for_inflation(row, cpi,
                                                                                      column="Opening_Weekend_USA"), 1)
    total.loc[:, 'Opening_Weekend_USA_Adjusted'] = total.apply(lambda row: 
                                                               adjust_for_inflation(row, cpi,
                                                                                    column="Opening_Weekend_USA"), 1)

    # Scale variables
    pixar, disney, total = scale_variables([pixar, disney, total],
                                           ["I_Audience_Rating", "R_Audience_Score", "R_Audience_Rating",
                                            "R_Critic_Score", "R_Critic_Rating",
                                            "Cumulative Worldwide Gross", "Opening_Weekend_USA",
                                            "Opening_Weekend_USA_Adjusted", "Yearly_Votes"])
    
    # Extract seed score
    pixar["Seed_Score"] = create_seed_score(pixar)
    disney["Seed_Score"] = create_seed_score(disney)
    total["Seed_Score"] = create_seed_score(total)
    
    return pixar, disney, total


def preprocess_imdb_data():
    """ Preprocess IMDB data
    
    Steps:
        * Manually add missing/incorrect Opening Weekend USA Box Office figures 
            * Some opening weekends were limited to a selected number of theaters
            * Thus, the weekend afterwards needed to be manually added 
        * Clean data
        * Merge disney and pixar together
    
    """
    
    # Titles
    disney_movies, pixar_movies = load_disney(), load_pixar()

    # Clean raw imdb data
    disney_df = clean_raw_data("disney", disney_movies)
    pixar_df = clean_raw_data("pixar", pixar_movies)

    # Extract features from json columns
    pixar_df, disney_df, total_df = extract_features(disney_df, pixar_df)
    
    # Some opening weekends were limited to a selected number of theaters
    # Thus, the weekend afterwards needed to be manually added
    disney_df.loc[disney_df.Title == "Frozen II", "Opening_Weekend_USA"] = 130_263_358
    total_df.loc[total_df.Title == "Frozen II", "Opening_Weekend_USA"] = 130_263_358
    
    disney_df.loc[disney_df.Title == "Aladdin", "Opening_Weekend_USA"] = 19_200_000
    total_df.loc[total_df.Title == "Aladdin", "Opening_Weekend_USA"] = 19_200_000
    
    disney_df.loc[disney_df.Title == "The Princess and the Frog", "Opening_Weekend_USA"] = 24_208_916
    total_df.loc[total_df.Title == "The Princess and the Frog", "Opening_Weekend_USA"] = 24_208_916
    
    disney_df.loc[disney_df.Title == "Brother Bear", "Opening_Weekend_USA"] = 24_208_916
    total_df.loc[total_df.Title == "Brother Bear", "Opening_Weekend_USA"] = 24_208_916
    
    disney_df.loc[disney_df.Title == "Atlantis: The Lost Empire", "Opening_Weekend_USA"] = 20_342_105
    total_df.loc[total_df.Title == "Atlantis: The Lost Empire", "Opening_Weekend_USA"] = 20_342_105
    
    disney_df.loc[disney_df.Title == "The Hunchback of Notre Dame", "Opening_Weekend_USA"] = 21_037_414
    total_df.loc[total_df.Title == "The Hunchback of Notre Dame", "Opening_Weekend_USA"] = 21_037_414
    
    pixar_df.loc[pixar_df.Title == "Monsters, Inc.", "Opening_Weekend_USA"] = 62_577_067
    total_df.loc[total_df.Title == "Monsters, Inc.", "Opening_Weekend_USA"] = 62_577_067
    
    pixar_df.loc[pixar_df.Title == "Toy Story", "Opening_Weekend_USA"] = 29_000_000
    total_df.loc[total_df.Title == "Toy Story", "Opening_Weekend_USA"] = 29_000_000
    
    pixar_df.loc[pixar_df.Title == "Finding Nemo", "Opening_Weekend_USA"] = 70_251_710
    total_df.loc[total_df.Title == "Finding Nemo", "Opening_Weekend_USA"] = 70_251_710
    
    pixar_df.loc[pixar_df.Title == "Onward", "Opening_Weekend_USA"] = 39_119_861
    total_df.loc[total_df.Title == "Onward", "Opening_Weekend_USA"] = 39_119_861
    
    return pixar_df, disney_df, total_df


def preprocess_rotten_data():
    """ Preprocess RottenTomatoes data
    
    Steps:
    * Change some titles to match the titles retrieved from Wikipedia
    * Extract release date
    * Combine pixar and disney data
    
    """
    
    # Load raw data
    disney_movies, pixar_movies = load_disney(), load_pixar()
    disney = pd.read_csv("../data/RottenTomatoes/disney_raw.csv")
    pixar = pd.read_csv("../data/RottenTomatoes/pixar_raw.csv")
    
    # Preprocess pixar
    titles_to_keep = []
    for pixar_movie in pixar_movies:
        if pixar_movie in pixar.Title.values:
            titles_to_keep.append(pixar_movie)
        
    pixar_mapping = {"WALL-E": "WALL·E"}
    for title in titles_to_keep:
        pixar_mapping[title] = title
        
    pixar.Title = pixar.Title.map(pixar_mapping)
    pixar = pixar.dropna(subset=['Title']).drop_duplicates(subset=["Title"])
    pixar['Company'] = "Pixar"
    
    # Preprocess disney
    titles_to_keep = []
    for disney_movie in disney_movies:
        if disney_movie in disney.Title.values:
            titles_to_keep.append(disney_movie)

    disney_mapping = {"Atlantis - The Lost Empire": "Atlantis: The Lost Empire",
                      "Fun & Fancy Free":  "Fun and Fancy Free",
                      "101 Dalmatians": "One Hundred and One Dalmatians",
                      "Many Adventures of Winnie the Pooh": "The Many Adventures of Winnie the Pooh",
                      "Wreck-it Ralph": "Wreck-It Ralph"}
    for title in titles_to_keep:
        disney_mapping[title] = title
        
    disney.Title = disney.Title.map(disney_mapping)
    disney.Release_Date = disney.apply(lambda row: str(row.Release_Date).split(", ")[-1] if isinstance(row.Release_Date, str)
                                       else None, 1)
    disney = disney.dropna(subset=['Release_Date'])
    disney.Release_Date = disney.Release_Date.astype(int)
    disney = disney.sort_values("Release_Date")
    disney = disney.dropna(subset=['Title']).drop_duplicates(subset=["Title"])
    disney['Company'] = "Disney"
    
    # combine datasets
    total = disney.append(pixar[:])

    return pixar, disney, total
    

def clean_raw_data(studio, movies):
    df = pd.read_csv(f"../data/IMDB/imdb_{studio}_raw.csv")
    df_clean = df.copy()
    df_clean = df_clean.loc[df_clean.Kind == "movie", :]
    df_clean = df_clean[df_clean['Genres'].apply(lambda x: 'Animation' in x)]
    df_clean = df_clean[df_clean.Title.isin(movies)]
    df_clean = df_clean.sort_values("Year").drop_duplicates("Title")

    return df_clean


def extract_budget(row):
    """ Extract budget from json string """
    
    box_office = row["Box office"]
    if isinstance(box_office, str):
        box_office = box_office.replace("\'", "\"")
        box_office = json.loads(box_office)
        
        if box_office.get("Budget"):
            return int(re.sub("[^0-9]", "", box_office.get("Budget")))
        
    return None


def extract_gross(row):
    """ Extract Cumulative Worldwide Gross from json string """
    
    box_office = row["Box office"]
    if isinstance(box_office, str):
        box_office = box_office.replace("\'", "\"")
        box_office = json.loads(box_office)
        
        if box_office.get("Cumulative Worldwide Gross"):
            return int(re.sub("[^0-9]", "", box_office.get("Cumulative Worldwide Gross").split(" ")[0]))
        
    return None


def extract_opening_weekend(row):
    """ Extract Opening Weekend United States from json string """
    
    box_office = row["Box office"]
    if isinstance(box_office, str):
        box_office = box_office.replace("\'", "\"")
        box_office = json.loads(box_office)
        
        if box_office.get("Opening Weekend United States"):
            return int(re.sub("[^0-9]", "", box_office.get("Opening Weekend United States").split(" ")[0]))
        
    return None


def normalize(df: pd.DataFrame, column: str):
    """ Normalize between 0 and 1"""
    
    # Fill the empty columns with the lowest value found in the respective column
    values = df[column].fillna(min(df[column])).values.reshape(-1, 1)
    values[values == np.inf] = min(df[column])
    
    # Give the lowest 3 values the same value
    # To create a nicer distribution which enhances nuances between ratings
    ind = np.argpartition(np.array(values).flatten(), -3)[-3:]
    values[ind] = max(values[ind])

    box = boxcox(values)
    values = box[0]
    
    min_max_scaler = preprocessing.MinMaxScaler()
    values_scaled = min_max_scaler.fit_transform(values)
    values_scaled = values_scaled.reshape(1, -1).flatten()
    values_scaled = [round(val, 2) for val in values_scaled]
    return values_scaled


def scale_variables(dfs: list, columns: list):
    """ Normalize multiple columns in multiple dataframes """
    new_dfs = []
    
    for df in dfs:
        for column in columns:
            df.loc[:, f"{column}_Scaled"] = normalize(df, column)
        new_dfs.append(df)
    
    return tuple(new_dfs)


def extract_features(disney, pixar):
    """ Extract and create features from disney and pixar data """
    disney["Budget"] = disney.apply(lambda row: extract_budget(row), 1)
    disney["Cumulative Worldwide Gross"] = disney.apply(lambda row: extract_gross(row), 1)
    disney["Opening_Weekend_USA"] = disney.apply(lambda row: extract_opening_weekend(row), 1)
    disney["Company"] = "Disney"
    disney["Yearly_Gross"] = disney.apply(lambda row: row["Cumulative Worldwide Gross"] / (2021 - row["Year"]) if row["Year"] >= 2010
                                          else row["Cumulative Worldwide Gross"] / (2021 - 2010), 1)
    disney["Yearly_Votes"] = disney.apply(lambda row: row["Votes"] / (2021 - row["Year"]) if row["Year"] >= 2010 
                                          else row["Votes"] / (2021 - 2010), 1)

    pixar["Budget"] = pixar.apply(lambda row: extract_budget(row), 1)
    pixar["Cumulative Worldwide Gross"] = pixar.apply(lambda row: extract_gross(row), 1)
    pixar["Opening_Weekend_USA"] = pixar.apply(lambda row: extract_opening_weekend(row), 1)
    pixar["Company"] = "Pixar"
    pixar["Yearly_Gross"] = pixar.apply(lambda row: row["Cumulative Worldwide Gross"] / (2021 - row["Year"]) if row["Year"] >= 2010
                                        else row["Cumulative Worldwide Gross"] / (2021 - 2010), 1)
    pixar["Yearly_Votes"] = pixar.apply(lambda row: row["Votes"] / (2021 - row["Year"]) if row["Year"] >= 2010 
                                        else row["Votes"] / (2021 - 2010), 1)

    total = disney.append(pixar)
    
    return pixar, disney, total


def create_seed_score(df):
    """ Create Seed Score by:

    Score_i = (IR_i) + ( (RAR_i + RAS_i + RCR_i + RCS_i) / 4 ) + ( (OpeningWeekend_i + YearlyVotes_i) / 2 )

    """

    imdb_score = df["I_Audience_Rating_Scaled"]
    rotten_score = (df["R_Audience_Score_Scaled"] +
                    df["R_Audience_Rating_Scaled"] +
                    df["R_Critic_Score_Scaled"] +
                    df["R_Critic_Rating_Scaled"])/4
    popular_score = (df["Opening_Weekend_USA_Adjusted_Scaled"]/2) + (df["Yearly_Votes_Scaled"]/2)

    return (imdb_score + rotten_score + popular_score) / 3


def adjust_for_inflation(row, cpi, column=""):
    """ Adjust a monetary value for inflation
    https://www.usinflationcalculator.com/inflation/consumer-price-index-and-annual-percent-changes-from-1913-to-2008/
    """
    value = row[column]
    year = row["Year"]
    cpi_movie = cpi.loc[cpi.Year == year, "CPI"].values[0]
    cpi_2020 = cpi.CPI.iloc[-1]
    
    adjusted_value = (value * cpi_2020) / cpi_movie
    
    return adjusted_value

# %%
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
from time import *
from random import randint
import time
import configparser

# %%
user_rating = 6.5, 10.0
num_votes = 35000
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'}
imdbId = []

def get_imdbId(user_rating, num_votes):
    url = f"https://www.imdb.com/search/title/?title_type=feature&user_rating={user_rating}&num_votes={num_votes},&view=simple&sort=user_rating,desc&count=250"
    while True:
        url = url
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        titles = soup.find_all('div', {'class': 'lister-item mode-simple'})
        for item in titles:
            title = item.find('img')['data-tconst']
            imdbId.append(title)
        print(len(imdbId))
        time.sleep(2)   

        if (soup.find('a', {'class': 'lister-page-next next-page'})):
            url = 'https://www.imdb.com/' + soup.find('a', {'class': 'lister-page-next next-page'})['href']
        else:
            break

# %%
get_imdbId(user_rating, num_votes)

# %%
pd.Series(imdbId).to_csv('ImdbId_top_movies_24_10_2022.csv', index=False, header=['id'])

# %%
ids = pd.read_csv('ImdbId_top_movies_24_10_2022.csv')
ids

# %%
id_list = ids['id'].tolist()
id_list

# %%
def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.py')
    return config['api_key']

# %%
config = configparser.ConfigParser()
config.read('config.ini')
config['tmdb']['api_key']
#print(config.)

# %%
movies = {}

def get_tmdb_movie_data(imdbId_file):

    ids = pd.read_csv(imdbId_file)
    id_list = ids['id'].tolist()
    api_key = get_api_key()

    for movie_id in id_list:  
        url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        movies.append(soup)
        time.sleep(2)   


# %%
get_tmdb_movie_data('data/ImdbId_top_movies_24_10_2022.csv')

# %%




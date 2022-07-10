from asyncio.windows_events import NULL
from operator import index
from turtle import distance
from urllib import response
from django.shortcuts import redirect, render
import pandas as pd
import requests
import pickle

movies_dict = pickle.load(open('./models/movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('./models/similarity.pkl', 'rb'))


def fetch_poster(movie_id):
    res = requests.get('https://api.themoviedb.org/3/movie/' + movie_id +
                       '?api_key=21b0789c9c14a260fe8c9c453d17d44d&language=en-US')
    if(res.status_code == 200):
        data = res.json()
        if(data['poster_path'] != NULL):
            return 'https://image.tmdb.org/t/p/original{}'.format(data['poster_path']), data['id']
    return 'https://image.tmdb.org/t/p/original/jRXYjXNq0Cs2TcJjLkki24MLp7u.jpg', data['id']


movies_title = movies['title']
sorted(movies_title)


def home(req):
    if(req.method == 'POST'):
        name = req.POST.get('movie_name')
        index = movies[movies['title'] == name].index
        if(len(index) > 1):
            index = index[0]
        movie_id = movies.iloc[index[0]].movie_id
        print(movie_id, "/////")
        return redirect('/{}'.format(movie_id))
    else:
        params = {'movie_titles': movies['title']}
        return render(req, 'home.html', params)


def fetch_detail(movie):
    res = requests.get('https://api.themoviedb.org/3/movie/' + movie +
                       '?api_key=21b0789c9c14a260fe8c9c453d17d44d&language=en-US')
    if(res.status_code == 200):
        data = res.json()
    title = data['original_title']
    image = 'https://image.tmdb.org/t/p/original{}'.format(data['poster_path'])
    genres = data['genres']
    overview = data['overview']
    p_c = data['production_companies']
    if(len(p_c) > 5):
        p_c = p_c[:5]
    release = data['release_date']
    adult = data['adult']

    return title, image, genres, overview, p_c, release, adult


def movie(req, movie):
    index = movies[movies['movie_id'] == int(movie)].index
    if(len(index) == 1):
        index = index[0]
    else:
        return []
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    L = []
    for i in distances[0:15]:
        movie_id = movies.iloc[i[0]].movie_id
        x, z = fetch_poster(str(movie_id))
        y = movies.iloc[i[0]].title
        L.append({'image': x, 'name': y, 'id': z})

    a, b, c, d, e, f, g = fetch_detail(movie)

    params = {'dict': L, 'name': a, 'image': b, 'genres': c,
              'overview': d, 'p_c': e, 'release': f, 'adult': g}
    return render(req, 'movie.html', params)

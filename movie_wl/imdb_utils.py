from imdb import Cinemagoer


ia = Cinemagoer()

def get_top_10_movies():
    try:
        top_movies = ia.get_top250_movies()
        if top_movies:
            # Extract relevant information (title and year) for the top 10 movies
            return [{'title': movie['title'], 'year': movie['year']} for movie in top_movies[:10]]
        else:
            return []
    except Exception as e:
        print(f"An error occurred while fetching the top 10 movies: {e}")
        return []

def get_bottom_10_movies():
    try:
        bottom_movies = ia.get_bottom100_movies()
        if bottom_movies:
            # Extract relevant information (title and year) for the bottom 10 movies
            return [{'title': movie['title'], 'year': movie['year']} for movie in bottom_movies[:10]]
        else:
            return []
    except Exception as e:
        print(f"An error occurred while fetching the bottom 10 movies: {e}")
        return []

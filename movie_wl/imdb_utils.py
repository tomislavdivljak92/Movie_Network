import imdb
ia = imdb.Cinemagoer()
def get_top_10_movies(num_movies=10):
    """Retrieve the top movies."""
    print("Fetching top 10 movies...")
    try:
        top_movies = ia.get_top250_movies()  # Get top 250 movies
        print(f"Retrieved {len(top_movies)} top movies.")
        if top_movies:
            return top_movies[:num_movies]  # Return only the first 10
        else:
            print("No top movies found.")
            return []
    except Exception as e:
        print(f"Error fetching top movies: {e}")
        return []

def get_bottom_10_movies(num_movies=10):
    """Retrieve the bottom movies."""
    print("Fetching bottom 10 movies...")
    try:
        bottom_movies = ia.get_bottom100_movies()  # Get bottom 100 movies
        print(f"Retrieved {len(bottom_movies)} bottom movies.")
        if bottom_movies:
            return bottom_movies[:num_movies]  # Return the first 10
        else:
            print("No bottom movies found.")
            return []
    except Exception as e:
        print(f"Error fetching bottom movies: {e}")
        return []

# Test the functions
top_movies = get_top_10_movies()
print("\nTop 10 Movies:")
for movie in top_movies:
    print(movie['title'])  # Display only the title of the movie

bottom_movies = get_bottom_10_movies()
print("\nBottom 10 Movies:")
for movie in bottom_movies:
    print(movie['title'])  # Display only the title of the movie

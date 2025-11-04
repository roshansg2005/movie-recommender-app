from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import pandas as pd
import requests

# --- Initialize the Flask App ---
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# --- Load the saved data ---
try:
    movie_dict = pickle.load(open('movie_dict.pkl', 'rb'))
    movies = pd.DataFrame(movie_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
except FileNotFoundError:
    print("ERROR: Model files not found. Run create_model.py first.")
    exit()

# --- Helper Function: Fetch Poster (OMDb) ---
def fetch_poster(movie_title):
    # !!!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!!
    # ADD YOUR OMDb API KEY HERE
    api_key = "8f84ebcc"
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    url = "http://www.omdbapi.com/"
    params = {'t': movie_title, 'apikey': api_key}

    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data['Response'] == 'True' and 'Poster' in data and data['Poster'] != 'N/A':
            return data['Poster']
    except Exception as e:
        print(f"Error fetching poster: {e}")

    # Return a placeholder if not found
    return "https://via.placeholder.com/500x750.png?text=Poster+Not+Found"

# --- Helper Function: Recommend Movies ---
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies_data = []
    for i in movies_list:
        title = movies.iloc[i[0]].title
        poster = fetch_poster(title)
        recommended_movies_data.append({
            "title": title,
            "poster": poster
        })
    return recommended_movies_data

# --- API Endpoint: Get Full Movie List ---
# This endpoint sends all movie titles to React for the dropdown
@app.route('/movies', methods=['GET'])
def get_movies():
    return jsonify(movies['title'].tolist())

# --- API Endpoint: Get Recommendations ---
# This endpoint takes a movie title and returns 5 recommendations
@app.route('/recommend', methods=['GET'])
def get_recommendations():
    # Get the movie title from the query parameter (e.g., /recommend?movie=Avatar)
    movie_title = request.args.get('movie')

    if not movie_title:
        return jsonify({"error": "No movie title provided"}), 400

    try:
        recommendations = recommend(movie_title)
        return jsonify(recommendations)
    except Exception as e:
        # Handle cases where the movie might not be in the list
        return jsonify({"error": f"An error occurred: {e}"}), 500

# --- Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=5000) # Runs on http://localhost:5000
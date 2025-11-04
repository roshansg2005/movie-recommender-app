import pandas as pd
import numpy as np
import ast  # For converting string-lists to lists
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
import pickle

print("Script started...")

# --- 1. Load Data ---
movies = pd.read_csv('tmdb_5000_movies.csv')
credits = pd.read_csv('tmdb_5000_credits.csv')

print("Data loaded...")

# --- 2. Merge and Clean Data ---
movies = movies.merge(credits, on='title')
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)

print("Data merged and cleaned...")

# --- 3. Helper Functions for Preprocessing ---

def convert(obj):
    """Converts string-list of genres/keywords to a clean list."""
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

def convert3(obj):
    """Gets the top 3 actors from the cast list."""
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            L.append(i['name'])
            counter += 1
        else:
            break
    return L

def fetch_director(obj):
    """Gets the director's name from the crew list."""
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L

# --- 4. Apply Preprocessing ---
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['crew'] = movies['crew'].apply(fetch_director)
movies['overview'] = movies['overview'].apply(lambda x: x.split())

# Remove spaces to create single tags (e.g., "Sam Mendes" -> "SamMendes")
movies['genres'] = movies['genres'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['cast'] = movies['cast'].apply(lambda x: [i.replace(" ", "") for i in x])
movies['crew'] = movies['crew'].apply(lambda x: [i.replace(" ", "") for i in x])

print("Helper functions applied...")

# --- 5. Create 'tags' Column ---
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

# Create the final DataFrame
new_df = movies[['movie_id', 'title', 'tags']]
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())

# --- 6. Stemming (Text Preprocessing) ---
ps = PorterStemmer()

def stem(text):
    """Applies stemming to the text."""
    y = []
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)

new_df['tags'] = new_df['tags'].apply(stem)

print("Stemming complete...")

# --- 7. Vectorization ---
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()

print("Vectorization complete...")

# --- 8. Calculate Similarity ---
similarity = cosine_similarity(vectors)

print("Similarity matrix calculated...")

# --- 9. Save Model Files ---
# We save the movie list (as a dictionary) and the similarity matrix
pickle.dump(new_df.to_dict(), open('movie_dict.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print("Model files (movie_dict.pkl and similarity.pkl) saved successfully!")
print("Script finished.")
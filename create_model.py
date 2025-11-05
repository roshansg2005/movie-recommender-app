import pandas as pd
import numpy as np
import ast
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
import pickle
import requests
import os
import zipfile  # <-- Added this
import io       # <-- Added this

# --- PASTE THE DIRECT DOWNLOAD URL TO YOUR ZIP FILE HERE ---
zip_file_url = "https://github.com/roshansg2005/movie-recommender-app/raw/main/archive.zip" 
zip_filename = "data.zip" # The name we'll save it as
# --- These must match the file names INSIDE your zip file ---
movies_file = "tmdb_5000_movies.csv"
credits_file = "tmdb_5000_credits.csv"

# --- 1. Download and Unzip Function ---
def download_and_unzip(url, zip_name):
    # Check if files already exist
    if os.path.exists(movies_file) and os.path.exists(credits_file):
        print("CSV files already exist. Skipping download and unzip.")
        return
    
    print(f"Downloading {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        
        print("Download successful. Unzipping files...")
        # Use io.BytesIO to treat the downloaded content as a file
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall() # Extracts all files to the current directory
            
        print(f"Successfully unzipped. Found: {z.namelist()}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading zip file: {e}")
        exit()
    except zipfile.BadZipFile:
        print("Error: Downloaded file is not a valid zip file.")
        exit()

print("Build script started...")

# --- Download and unzip the data files ---
download_and_unzip(zip_file_url, zip_filename)

# --- 2. Load Data ---
try:
    movies = pd.read_csv(movies_file)
    credits = pd.read_csv(credits_file)
    print("Data loaded...")
except FileNotFoundError as e:
    print(f"Error: Could not read CSV files after unzipping. Missing: {e.filename}")
    exit()

# --- 3. Merge and Clean Data ---
movies = movies.merge(credits, on='title')
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]
movies.dropna(inplace=True)
print("Data merged and cleaned...")

# --- 4. Helper Functions for Preprocessing ---
def convert(obj):
    L = []
    try:
        for i in ast.literal_eval(obj):
            L.append(i['name'])
    except Exception as e:
        pass
    return L

def convert3(obj):
    L = []
    counter = 0
    try:
        for i in ast.literal_eval(obj):
            if counter != 3:
                L.append(i['name'])
                counter += 1
            else:
                break
    except Exception as e:
        pass
    return L

def fetch_director(obj):
    L = []
    try:
        for i in ast.literal_eval(obj):
            if i['job'] == 'Director':
                L.append(i['name'])
                break
    except Exception as e:
        pass
    return L

# --- 5. Apply Preprocessing ---
movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)
movies['cast'] = movies['cast'].apply(convert3)
movies['crew'] = movies['crew'].apply(fetch_director)
movies['overview'] = movies['overview'].apply(lambda x: x.split() if isinstance(x, str) else [])

def remove_spaces(L):
    return [i.replace(" ", "") for i in L]

movies['genres'] = movies['genres'].apply(remove_spaces)
movies['keywords'] = movies['keywords'].apply(remove_spaces)
movies['cast'] = movies['cast'].apply(remove_spaces)
movies['crew'] = movies['crew'].apply(remove_spaces)
print("Helper functions applied...")

# --- 6. Create 'tags' Column ---
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
new_df = movies[['movie_id', 'title', 'tags']]
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))
new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())

# --- 7. Stemming (Text Preprocessing) ---
ps = PorterStemmer()
def stem(text):
    y = []
    if isinstance(text, str):
        for i in text.split():
            y.append(ps.stem(i))
    return " ".join(y)

new_df['tags'] = new_df['tags'].apply(stem)
print("Stemming complete...")

# --- 8. Vectorization ---
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()
print("Vectorization complete...")

# --- 9. Calculate Similarity ---
similarity = cosine_similarity(vectors)
print("Similarity matrix calculated...")

# --- 10. Save Model Files ---
pickle.dump(new_df.to_dict(), open('movie_dict.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

print("Model files (movie_dict.pkl and similarity.pkl) saved successfully!")
print("Build script finished.")

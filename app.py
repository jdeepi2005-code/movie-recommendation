import streamlit as st
import pickle
import pandas as pd
import requests
import random

# =========================
# API KEYS
# =========================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Movie Recommender", layout="wide")

# =========================
# BACKGROUND & STYLE
# =========================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
.movie-card {
    background-color: #020617;
    padding: 10px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
movies = pickle.load(open("movies.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# =========================
# SESSION STATE
# =========================
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# =========================
# FUNCTIONS
# =========================
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    poster_path = data.get("poster_path")
    if poster_path:
        return "https://image.tmdb.org/t/p/w500" + poster_path
    return None

def fetch_omdb_details(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    return requests.get(url).json()

def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    rec_movies = []
    for i in movie_list:
        rec_movies.append(movies.iloc[i[0]])
    return rec_movies

# =========================
# SIDEBAR FEATURES
# =========================
st.sidebar.title("🎛 Personalization")

mood = st.sidebar.selectbox(
    "Your Mood",
    ["Normal", "Happy", "Sad", "Excited", "Relaxed"]
)

if st.sidebar.button("🎲 Surprise Me"):
    random_movie = random.choice(movies["title"].values)
    st.session_state["selected_movie"] = random_movie

st.sidebar.subheader("❤️ Favorites")
for fav in st.session_state.favorites:
    st.sidebar.write("•", fav)

# =========================
# MAIN UI
# =========================
st.title("🎬 Movie Recommendation System")

movie_list = movies["title"].values
selected_movie = st.selectbox(
    "Select a movie",
    movie_list,
    index=0
)

if "selected_movie" in st.session_state:
    selected_movie = st.session_state["selected_movie"]

# =========================
# RECOMMEND BUTTON
# =========================
if st.button("Recommend"):
    recommendations = recommend(selected_movie)

    st.subheader("Recommended Movies")

    cols = st.columns(5)

    for idx, movie in enumerate(recommendations):
        with cols[idx]:
            poster = fetch_poster(movie.movie_id)
            omdb = fetch_omdb_details(movie.title)

            st.markdown('<div class="movie-card">', unsafe_allow_html=True)

            if poster:
                st.image(poster, use_container_width=True)

            st.markdown(f"**{movie.title}**")

            # IMDb Rating
            imdb = omdb.get("imdbRating", "N/A")
            awards = omdb.get("Awards", "N/A")
            runtime = omdb.get("Runtime", "N/A")

            st.write("⭐ IMDb:", imdb)
            st.write("🏆 Awards:", awards)
            st.write("⏱ Runtime:", runtime)

            # Why this movie
            st.caption("🧠 Recommended because it is similar in genre and storyline.")

            # Add to favorites
            if st.button("❤️ Add", key=movie.title):
                if movie.title not in st.session_state.favorites:
                    st.session_state.favorites.append(movie.title)

            st.markdown('</div>', unsafe_allow_html=True)
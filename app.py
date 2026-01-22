import streamlit as st
import pickle
import pandas as pd
import requests
import random

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# Page configuration
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
}
.movie-card {
    background-color: #020617;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.title("🎬 Movie Recommendation System")
st.write("Find movies similar to your favorite one")

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= SESSION STATE =================
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Settings")

num_recommendations = st.sidebar.slider(
    "Number of recommendations",
    min_value=3,
    max_value=10,
    value=5
)

mood = st.sidebar.selectbox(
    "Your Mood",
    ["Normal", "Happy", "Sad", "Excited", "Relaxed"]
)

if st.sidebar.button("🎲 Surprise Me"):
    st.session_state["surprise"] = random.choice(movies["title"].values)

st.sidebar.subheader("❤️ Favorites")
for fav in st.session_state.favorites:
    st.sidebar.write("•", fav)

# ================= FUNCTIONS =================
def recommend(movie, n):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:n+1]
    return movie_list

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
        data = requests.get(url).json()
        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    except:
        pass
    return None

def fetch_omdb(title):
    try:
        url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
        return requests.get(url).json()
    except:
        return {}

# ================= SEARCH =================
st.subheader("🔍 Search Movie")
movie_input = st.text_input("Type a movie name")

st.subheader("🎞️ Or select from the list")
selected_movie = st.selectbox(
    "Movie list",
    movies['title'].values
)

final_movie = movie_input if movie_input in movies['title'].values else selected_movie

if "surprise" in st.session_state:
    final_movie = st.session_state["surprise"]

st.success(f"You selected: **{final_movie}**")

# ================= RECOMMEND =================
if st.button("Recommend 🎯"):
    try:
        with st.spinner("Finding similar movies..."):
            recommendations = recommend(final_movie, num_recommendations)

        st.subheader("📌 Recommended Movies")

        cols = st.columns(5)
        for idx, rec in enumerate(recommendations):
            movie_data = movies.iloc[rec[0]]
            with cols[idx % 5]:
                poster = fetch_poster(movie_data.movie_id)
                omdb = fetch_omdb(movie_data.title)

                st.markdown('<div class="movie-card">', unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(f"**{movie_data.title}**")
                st.write("⭐ IMDb:", omdb.get("imdbRating", "N/A"))
                st.write("🏆 Awards:", omdb.get("Awards", "N/A"))

                st.caption("🧠 Recommended due to similarity in content and user preference.")

                if st.button("❤️ Add", key=movie_data.title):
                    if movie_data.title not in st.session_state.favorites:
                        st.session_state.favorites.append(movie_data.title)

                st.markdown('</div>', unsafe_allow_html=True)
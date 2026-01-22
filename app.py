import streamlit as st
import pickle
import pandas as pd
import requests
import random

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ================= ADVANCED UI STYLE =================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top, #141e30, #243b55);
        color: white;
    }

    .movie-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 18px;
        text-align: center;
        transition: all 0.3s ease-in-out;
        box-shadow: 0 8px 25px rgba(0,0,0,0.4);
    }

    .movie-card:hover {
        transform: scale(1.05);
        box-shadow: 0 12px 35px rgba(0,0,0,0.6);
    }

    .rating-badge {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        color: black;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
        display: inline-block;
        margin-top: 6px;
    }

    .fav-btn button {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027, #203a43);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================= TITLE =================
st.markdown("## 🎬 Movie Recommendation System")
st.caption("Discover movies similar to your favorites with smart recommendations")

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= SESSION STATE =================
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ================= SIDEBAR =================
st.sidebar.markdown("## ⚙️ Personalization")

num_recommendations = st.sidebar.slider(
    "🎯 Number of recommendations",
    3, 10, 5
)

mood = st.sidebar.selectbox(
    "😊 Select your mood",
    ["Normal", "Happy", "Sad", "Excited", "Relaxed"]
)

if st.sidebar.button("🎲 Surprise Me"):
    st.session_state["surprise"] = random.choice(movies["title"].values)

st.sidebar.markdown("### ❤️ Your Favorites")
for fav in st.session_state.favorites:
    st.sidebar.write("•", fav)

# ================= FUNCTIONS =================
def recommend(movie, n):
    index = movies[movies["title"] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1 : n + 1]
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
st.markdown("### 🔍 Search Movie")
movie_input = st.text_input("Type a movie name")

st.markdown("### 🎞️ Or choose from list")
selected_movie = st.selectbox(
    "Movies",
    movies["title"].values
)

final_movie = movie_input if movie_input in movies["title"].values else selected_movie

if "surprise" in st.session_state:
    final_movie = st.session_state["surprise"]

st.success(f"🎥 Selected movie: **{final_movie}**")

# ================= RECOMMEND =================
if st.button("🚀 Recommend"):
    with st.spinner("Analyzing similarities..."):
        recommendations = recommend(final_movie, num_recommendations)

    st.markdown("## 🌟 Recommended Movies")

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

            imdb = omdb.get("imdbRating", "N/A")
            st.markdown(
                f'<div class="rating-badge">⭐ IMDb {imdb}</div>',
                unsafe_allow_html=True
            )

            st.caption("🧠 Recommended due to similar storyline & genre")

            if st.button("❤️ Add to Favorites", key=movie_data.title):
                if movie_data.title not in st.session_state.favorites:
                    st.session_state.favorites.append(movie_data.title)

            st.markdown("</div>", unsafe_allow_html=True)
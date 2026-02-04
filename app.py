import streamlit as st
import pickle
import requests
import random

TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"

st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# ---------------- STYLES ----------------
st.markdown("""
<style>
.stApp { background-color:#0f172a; color:white; }
.card {
    background:#020617;
    padding:15px;
    border-radius:10px;
    margin-bottom:15px;
}
h1,h2,h3 { color:white; }
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if "@" in email and password:
            st.session_state.logged_in = True
            st.experimental_rerun()
        else:
            st.error("Enter valid email and password")

    st.stop()

# ---------------- LOAD DATA ----------------
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- FUNCTIONS ----------------
def recommend(movie, n=5):
    idx = movies[movies['title'] == movie].index[0]
    scores = similarity[idx]
    movies_list = sorted(list(enumerate(scores)), reverse=True, key=lambda x: x[1])[1:n+1]
    return movies_list

def poster(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    ).json()
    return "https://image.tmdb.org/t/p/w500" + data["poster_path"]

def trailer(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    ).json()
    for v in data.get("results", []):
        if v["site"] == "YouTube" and v["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Recommended", "Surprise Me", "Recommend by Mood", "Watchlist"]
)

# ---------------- HOME ----------------
if page == "Home":
    st.title("Movie Recommendation System")
    st.write("Personalized movie discovery using machine learning.")

# ---------------- RECOMMENDED ----------------
elif page == "Recommended":
    st.title("Recommended Movies")

    selected_movie = st.selectbox("Select a movie", movies["title"].values)

    if selected_movie:
        movie_row = movies[movies["title"] == selected_movie].iloc[0]

        col1, col2 = st.columns([1,2])

        with col1:
            st.image(poster(movie_row.movie_id), use_container_width=True)

            if st.button("Add to Watchlist"):
                if selected_movie not in st.session_state.watchlist:
                    st.session_state.watchlist.append(selected_movie)
                    st.success("Added to watchlist")

        with col2:
            t = trailer(movie_row.movie_id)
            if t:
                st.video(t)

        st.subheader("Similar Movies")
        cols = st.columns(5)

        recs = recommend(selected_movie)
        for i, rec in enumerate(recs):
            m = movies.iloc[rec[0]]
            with cols[i]:
                st.image(poster(m.movie_id), use_container_width=True)
                st.caption(m.title)

# ---------------- SURPRISE ME ----------------
elif page == "Surprise Me":
    st.title("Surprise Me")

    movie = movies.sample(1).iloc[0]

    col1, col2 = st.columns([1,2])
    with col1:
        st.image(poster(movie.movie_id), use_container_width=True)
    with col2:
        st.subheader(movie.title)
        t = trailer(movie.movie_id)
        if t:
            st.video(t)

# ---------------- MOOD ----------------
elif page == "Recommend by Mood":
    st.title("Mood Based Recommendation")

    mood_map = {
        "Happy": ["comedy"],
        "Sad": ["drama"],
        "Excited": ["action", "thriller"],
        "Relaxed": ["family"],
        "Romantic": ["romance"]
    }

    mood = st.selectbox("Select Mood", mood_map.keys())
    keywords = mood_map[mood]

    filtered = movies[movies["tags"].str.contains("|".join(keywords), case=False, na=False)]
    sample = filtered.sample(min(5, len(filtered)))

    cols = st.columns(5)
    for i, (_, m) in enumerate(sample.iterrows()):
        with cols[i]:
            st.image(poster(m.movie_id), use_container_width=True)
            st.caption(m.title)

# ---------------- WATCHLIST ----------------
elif page == "Watchlist":
    st.title("My Watchlist")

    if not st.session_state.watchlist:
        st.info("Watchlist is empty")
    else:
        cols = st.columns(4)
        for i, title in enumerate(st.session_state.watchlist):
            m = movies[movies["title"] == title].iloc[0]
            with cols[i % 4]:
                st.image(poster(m.movie_id), use_container_width=True)
                st.caption(title)
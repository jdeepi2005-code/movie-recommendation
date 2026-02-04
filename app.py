import streamlit as st
import pickle
import requests
import random

# ---------------- CONFIG ----------------
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "email" not in st.session_state:
    st.session_state.email = ""

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {
    color: #111;
}
h1, h2, h3 {
    text-align: center;
}
.card {
    background-color: #ffffff;
    padding: 16px;
    border-radius: 10px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.title("User Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if email and password:
            st.session_state.logged_in = True
            st.session_state.email = email
            st.rerun()
        else:
            st.error("Please enter email and password")

    st.stop()

# ---------------- DATA ----------------
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

def recommend(movie, n=5):
    idx = movies[movies["title"] == movie].index[0]
    scores = similarity[idx]
    return sorted(list(enumerate(scores)), reverse=True, key=lambda x: x[1])[1:n+1]

def fetch_poster(movie_id):
    res = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    ).json()
    if res.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + res["poster_path"]
    return None

def fetch_trailer(movie_id):
    res = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    ).json()
    for v in res.get("results", []):
        if v["site"] == "YouTube" and v["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

# ---------------- SIDEBAR ----------------
st.sidebar.title("Navigation")
st.sidebar.write(st.session_state.email)

page = st.sidebar.radio(
    "Menu",
    ["Home", "Recommended", "Surprise Me", "Recommend by Mood", "Watchlist"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.watchlist = []
    st.rerun()

# ---------------- HOME ----------------
if page == "Home":
    st.title("Movie Recommendation System")
    st.write("""
    This system uses content-based filtering to recommend movies based on similarity.
    Users can explore recommendations, discover movies by mood, and maintain a watchlist.
    """)

# ---------------- RECOMMENDED ----------------
elif page == "Recommended":
    st.title("Recommended Movies")

    movie_name = st.selectbox("Select a movie", movies["title"].values)

    if st.button("Recommend"):
        results = recommend(movie_name)

        for rec in results:
            movie = movies.iloc[rec[0]]
            poster = fetch_poster(movie.movie_id)
            trailer = fetch_trailer(movie.movie_id)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            col1, col2 = st.columns([1, 2])

            with col1:
                if poster:
                    st.image(poster, width=180)

            with col2:
                st.subheader(movie.title)

                if movie.title not in st.session_state.watchlist:
                    if st.button("Add to Watchlist", key=f"add_{movie.movie_id}"):
                        st.session_state.watchlist.append(movie.title)
                        st.success("Added to watchlist")

            if trailer:
                st.video(trailer)

            st.markdown("</div>", unsafe_allow_html=True)

# ---------------- SURPRISE ME ----------------
elif page == "Surprise Me":
    st.title("Surprise Me")

    movie = movies.sample(1).iloc[0]
    poster = fetch_poster(movie.movie_id)
    trailer = fetch_trailer(movie.movie_id)

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    if poster:
        st.image(poster, width=200)

    st.subheader(movie.title)

    if trailer:
        st.video(trailer)

    if movie.title not in st.session_state.watchlist:
        if st.button("Add to Watchlist"):
            st.session_state.watchlist.append(movie.title)
            st.success("Added to watchlist")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- MOOD BASED ----------------
elif page == "Recommend by Mood":
    st.title("Recommend by Mood")

    mood_map = {
        "Happy": ["comedy"],
        "Sad": ["drama"],
        "Romantic": ["romance"],
        "Excited": ["action", "thriller"],
        "Relaxed": ["family", "animation"]
    }

    mood = st.selectbox("Select mood", mood_map.keys())

    keywords = mood_map[mood]
    filtered = movies[movies["tags"].str.contains("|".join(keywords), case=False, na=False)]

    for _, movie in filtered.sample(min(5, len(filtered))).iterrows():
        poster = fetch_poster(movie.movie_id)
        trailer = fetch_trailer(movie.movie_id)

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        if poster:
            st.image(poster, width=180)

        st.subheader(movie.title)

        if trailer:
            st.video(trailer)

        if movie.title not in st.session_state.watchlist:
            if st.button("Add to Watchlist", key=f"m_{movie.movie_id}"):
                st.session_state.watchlist.append(movie.title)
                st.success("Added to watchlist")

        st.markdown("</div>", unsafe_allow_html=True)

# ---------------- WATCHLIST ----------------
elif page == "Watchlist":
    st.title("My Watchlist")

    if not st.session_state.watchlist:
        st.info("Your watchlist is empty")
    else:
        for title in st.session_state.watchlist:
            movie = movies[movies["title"] == title].iloc[0]
            poster = fetch_poster(movie.movie_id)

            st.markdown("<div class='card'>", unsafe_allow_html=True)

            if poster:
                st.image(poster, width=150)

            st.subheader(title)

            if st.button("Remove", key=f"r_{movie.movie_id}"):
                st.session_state.watchlist.remove(title)
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
import streamlit as st
import pickle
import requests
import random

TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "current_trailer" not in st.session_state:
    st.session_state.current_trailer = None

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp {
    background-color: #f5f6fa;
    color: #111;
}
.card {
    background: white;
    padding: 14px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
h1, h2 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.title("User Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if "@" in email and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("Enter a valid email and password")

    st.stop()

# ---------------- LOAD DATA ----------------
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- FUNCTIONS ----------------
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    distances = similarity[index]
    return sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

def fetch_poster(movie_id):
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    )
    data = r.json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_trailer(movie_id):
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    )
    for v in r.json().get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

# ---------------- NAV ----------------
st.sidebar.title("Navigation")
st.sidebar.write(st.session_state.user_email)

page = st.sidebar.radio(
    "Menu",
    ["Home", "Recommended", "Surprise Me", "Watchlist"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.watchlist = []
    st.rerun()

# ---------------- HOME ----------------
if page == "Home":
    st.title("Movie Recommendation System")
    st.write("Content-based movie recommendation with trailers and watchlist support.")

# ---------------- RECOMMENDED ----------------
elif page == "Recommended":
    st.title("Recommended Movies")

    selected_movie = st.selectbox(
        "Choose a movie",
        movies["title"].values
    )

    if st.button("Recommend"):
        st.session_state.current_trailer = None
        results = recommend(selected_movie)
        cols = st.columns(5)

        for i, rec in enumerate(results):
            movie = movies.iloc[rec[0]]
            poster = fetch_poster(movie.movie_id)
            trailer = fetch_trailer(movie.movie_id)

            with cols[i]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_container_width=True)

                st.write(movie.title)

                if st.button("Watch Trailer", key=f"t{movie.movie_id}"):
                    st.session_state.current_trailer = trailer

                if st.button("Add to Watchlist", key=f"w{movie.movie_id}"):
                    if movie.title not in st.session_state.watchlist:
                        st.session_state.watchlist.append(movie.title)
                        st.success("Added")

                st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.current_trailer:
        st.subheader("Trailer")
        st.video(st.session_state.current_trailer)

# ---------------- SURPRISE ----------------
elif page == "Surprise Me":
    st.title("Random Movie")

    if st.button("Generate"):
        movie = movies.sample(1).iloc[0]
        poster = fetch_poster(movie.movie_id)
        trailer = fetch_trailer(movie.movie_id)

        if poster:
            st.image(poster, width=300)

        st.write(movie.title)

        if trailer:
            st.video(trailer)

# ---------------- WATCHLIST ----------------
elif page == "Watchlist":
    st.title("My Watchlist")

    if not st.session_state.watchlist:
        st.info("Watchlist is empty")
    else:
        for title in st.session_state.watchlist:
            st.write("- ", title)
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
if "current_trailer" not in st.session_state:
    st.session_state.current_trailer = None
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.title("User Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if "@" in email and "." in email and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("Enter valid email & password")

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
    if r.status_code == 200 and r.json().get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + r.json()["poster_path"]
    return None

def fetch_trailer(movie_id):
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    )
    if r.status_code == 200:
        for v in r.json()["results"]:
            if v["type"] == "Trailer" and v["site"] == "YouTube":
                return v["key"]
    return None

# ---------------- SIDEBAR ----------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Recommended", "Surprise Me", "Watchlist"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.watchlist = []
    st.session_state.current_trailer = None
    st.rerun()

# ---------------- HOME ----------------
if page == "Home":
    st.title("Movie Recommendation System")
    st.write("Personalized recommendations using Machine Learning")

# ---------------- RECOMMENDED ----------------
elif page == "Recommended":
    st.title("Recommended Movies")

    selected_movie = st.selectbox("Choose a movie", movies["title"].values)

    if st.button("Recommend"):
        recs = recommend(selected_movie)

        cols = st.columns(5)
        for i, rec in enumerate(recs):
            movie = movies.iloc[rec[0]]
            poster = fetch_poster(movie.movie_id)
            trailer = fetch_trailer(movie.movie_id)

            with cols[i]:
                if poster:
                    st.image(poster, use_container_width=True)

                st.write(movie.title)

                if st.button("Add to Watchlist", key=f"w_{movie.movie_id}"):
                    if movie.title not in st.session_state.watchlist:
                        st.session_state.watchlist.append(movie.title)
                        st.success("Added")

                if st.button("Watch Trailer", key=f"t_{movie.movie_id}"):
                    st.session_state.current_trailer = trailer

        # -------- GLOBAL TRAILER PLAYER --------
        if st.session_state.current_trailer:
            st.markdown("---")
            st.subheader("Trailer")
            st.markdown(
                f"""
                <iframe width="100%" height="400"
                src="https://www.youtube.com/embed/{st.session_state.current_trailer}"
                frameborder="0"
                allowfullscreen>
                </iframe>
                """,
                unsafe_allow_html=True
            )

# ---------------- SURPRISE ME ----------------
elif page == "Surprise Me":
    st.title("Surprise Me")

    if st.button("Generate"):
        movie = movies.sample(1).iloc[0]
        poster = fetch_poster(movie.movie_id)
        trailer = fetch_trailer(movie.movie_id)

        if poster:
            st.image(poster, width=300)

        st.write(movie.title)

        if st.button("Watch Trailer"):
            st.session_state.current_trailer = trailer

    if st.session_state.current_trailer:
        st.markdown("---")
        st.markdown(
            f"""
            <iframe width="100%" height="400"
            src="https://www.youtube.com/embed/{st.session_state.current_trailer}"
            frameborder="0"
            allowfullscreen>
            </iframe>
            """,
            unsafe_allow_html=True
        )

# ---------------- WATCHLIST ----------------
elif page == "Watchlist":
    st.title("My Watchlist")

    if not st.session_state.watchlist:
        st.info("No movies added")
    else:
        for movie in st.session_state.watchlist:
            st.write("•", movie)
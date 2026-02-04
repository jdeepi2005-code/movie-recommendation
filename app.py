import streamlit as st
import pickle
import requests
import random

# ------------------ CONFIG ------------------
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ------------------ SESSION STATE ------------------
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "popup" not in st.session_state:
    st.session_state.popup = ""

# ------------------ DARK UI ------------------
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
    color: #e5e7eb;
}
h1,h2,h3,h4,label {
    color: #e5e7eb;
}
.sidebar-content {
    color: #e5e7eb;
}
.movie-card {
    background-color: #020617;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.stButton>button {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ------------------ LOAD DATA ------------------
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ------------------ FUNCTIONS ------------------
def recommend(movie, n=5):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    return sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:n+1]

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

# ------------------ SIDEBAR ------------------
st.sidebar.title("Movie App")
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Recommended", "Surprise Me", "Mood Based", "Watchlist"]
)

# ------------------ POPUP ------------------
if st.session_state.popup:
    st.success(st.session_state.popup)
    st.session_state.popup = ""

# ------------------ HOME ------------------
if page == "Home":
    st.title("Movie Recommendation System")
    st.write("A content-based movie recommendation application.")

# ------------------ RECOMMENDED ------------------
elif page == "Recommended":
    st.title("Recommended Movies")

    selected_movie = st.selectbox(
        "Choose a movie",
        movies['title'].values
    )

    if st.button("Recommend"):
        results = recommend(selected_movie)

        cols = st.columns(5)
        for i, rec in enumerate(results):
            movie = movies.iloc[rec[0]]
            poster = fetch_poster(movie.movie_id)
            trailer = fetch_trailer(movie.movie_id)

            trailer_key = f"trailer_{movie.movie_id}"
            if trailer_key not in st.session_state:
                st.session_state[trailer_key] = False

            with cols[i]:
                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.subheader(movie.title)

                if st.button("Add to Watchlist", key=f"add_{movie.movie_id}"):
                    if movie.title not in st.session_state.watchlist:
                        st.session_state.watchlist.append(movie.title)
                        st.session_state.popup = "Movie added to watchlist"

                if trailer and st.button("Watch Trailer", key=f"btn_{movie.movie_id}"):
                    st.session_state[trailer_key] = True

                if st.session_state[trailer_key]:
                    st.video(trailer)

                st.markdown("</div>", unsafe_allow_html=True)

# ------------------ SURPRISE ME ------------------
elif page == "Surprise Me":
    st.title("Surprise Movie")

    if st.button("Generate"):
        movie = movies.sample(1).iloc[0]
        poster = fetch_poster(movie.movie_id)
        trailer = fetch_trailer(movie.movie_id)

        st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
        if poster:
            st.image(poster, width=300)

        st.subheader(movie.title)

        if trailer:
            st.video(trailer)

        st.markdown("</div>", unsafe_allow_html=True)

# ------------------ MOOD BASED ------------------
elif page == "Mood Based":
    st.title("Mood Based Recommendation")

    mood_map = {
        "Happy": ["comedy"],
        "Sad": ["drama"],
        "Excited": ["action", "thriller"],
        "Relaxed": ["family", "animation"],
        "Romantic": ["romance"]
    }

    mood = st.selectbox("Select mood", list(mood_map.keys()))

    if st.button("Recommend by Mood"):
        keywords = mood_map[mood]

        filtered = movies[
            movies['tags'].str.contains("|".join(keywords), case=False, na=False)
        ]

        cols = st.columns(5)
        for i, (_, movie) in enumerate(filtered.sample(min(5, len(filtered))).iterrows()):
            poster = fetch_poster(movie.movie_id)
            trailer = fetch_trailer(movie.movie_id)

            with cols[i]:
                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.subheader(movie.title)

                if trailer:
                    st.video(trailer)

                st.markdown("</div>", unsafe_allow_html=True)

# ------------------ WATCHLIST ------------------
elif page == "Watchlist":
    st.title("My Watchlist")

    if not st.session_state.watchlist:
        st.info("Your watchlist is empty")
    else:
        cols = st.columns(4)
        for i, title in enumerate(st.session_state.watchlist):
            movie = movies[movies['title'] == title].iloc[0]
            poster = fetch_poster(movie.movie_id)

            with cols[i % 4]:
                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.subheader(title)

                if st.button("Remove", key=f"remove_{movie.movie_id}"):
                    st.session_state.watchlist.remove(title)
                    st.experimental_rerun()

                st.markdown("</div>", unsafe_allow_html=True)
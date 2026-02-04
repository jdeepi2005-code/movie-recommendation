import streamlit as st
import pickle
import requests
import random

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# ================= SESSION STATE =================
if "show_trailer" not in st.session_state:
    st.session_state.show_trailer = {}

# ================= CUSTOM CSS =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#141e30,#243b55);
    color: white;
}
.card {
    background: #111827;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0 10px 25px rgba(0,0,0,.6);
    margin-bottom: 15px;
}
h1, h2, h3 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= FUNCTIONS =================
def recommend(movie, n=5):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    return sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:n+1]

def fetch_poster(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    ).json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_trailer(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    ).json()
    for v in data.get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            return v["key"]
    return None

# ================= SIDEBAR =================
st.sidebar.title("🎬 Movie App")
page = st.sidebar.radio(
    "Navigate",
    ["🏠 Home", "🎥 Recommended", "🎲 Surprise Me", "😊 Recommend by Mood"]
)

# ================= HOME =================
if page == "🏠 Home":
    st.markdown("<h1>🎬 Movie Recommendation System</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Discover movies you’ll love ❤️</h3>", unsafe_allow_html=True)

# ================= RECOMMENDED =================
elif page == "🎥 Recommended":
    st.markdown("<h2>🎥 Movie Recommendations</h2>", unsafe_allow_html=True)

    selected_movie = st.selectbox("Choose a movie", movies['title'].values)

    if st.button("🚀 Recommend"):
        recs = recommend(selected_movie, 5)
        cols = st.columns(5)

        for i, rec in enumerate(recs):
            movie = movies.iloc[rec[0]]
            poster = fetch_poster(movie.movie_id)
            trailer = fetch_trailer(movie.movie_id)
            movie_id = movie.movie_id

            with cols[i]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(f"**{movie.title}**")

                if trailer:
                    if st.button("🎬 Watch Trailer", key=f"btn_{movie_id}"):
                        st.session_state.show_trailer[movie_id] = True

                if st.session_state.show_trailer.get(movie_id):
                    st.markdown(
                        f"""
                        <iframe width="100%" height="215"
                        src="https://www.youtube.com/embed/{trailer}"
                        frameborder="0" allowfullscreen>
                        </iframe>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)

# ================= SURPRISE ME =================
elif page == "🎲 Surprise Me":
    st.markdown("<h2>🎲 Surprise Me!</h2>", unsafe_allow_html=True)

    if st.button("🎁 Surprise Me"):
        movie = movies.sample(1).iloc[0]
        poster = fetch_poster(movie.movie_id)
        trailer = fetch_trailer(movie.movie_id)
        movie_id = movie.movie_id

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        if poster:
            st.image(poster, width=300)

        st.markdown(f"### 🍿 {movie.title}")

        if trailer:
            if st.button("🎬 Watch Trailer", key=f"sur_{movie_id}"):
                st.session_state.show_trailer[movie_id] = True

        if st.session_state.show_trailer.get(movie_id):
            st.markdown(
                f"""
                <iframe width="100%" height="300"
                src="https://www.youtube.com/embed/{trailer}"
                frameborder="0" allowfullscreen>
                </iframe>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

# ================= MOOD BASED =================
elif page == "😊 Recommend by Mood":
    st.markdown("<h2>😊 Mood-Based Recommendation</h2>", unsafe_allow_html=True)

    mood_map = {
        "Romantic ❤️": ["romance"],
        "Happy 😄": ["comedy"],
        "Sad 😢": ["drama"],
        "Excited 🤩": ["action", "thriller"],
        "Relaxed 😌": ["family", "animation"]
    }

    mood = st.selectbox("Select your mood", list(mood_map.keys()))

    if st.button("😊 Recommend"):
        keywords = mood_map[mood]
        mood_movies = movies[
            movies['tags'].str.contains("|".join(keywords), case=False, na=False)
        ]

        cols = st.columns(5)
        for i, (_, movie) in enumerate(mood_movies.sample(min(5, len(mood_movies))).iterrows()):
            poster = fetch_poster(movie.movie_id)
            trailer = fetch_trailer(movie.movie_id)
            movie_id = movie.movie_id

            with cols[i]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(f"**{movie.title}**")

                if trailer:
                    if st.button("🎬 Watch Trailer", key=f"mood_{movie_id}"):
                        st.session_state.show_trailer[movie_id] = True

                if st.session_state.show_trailer.get(movie_id):
                    st.markdown(
                        f"""
                        <iframe width="100%" height="215"
                        src="https://www.youtube.com/embed/{trailer}"
                        frameborder="0" allowfullscreen>
                        </iframe>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)
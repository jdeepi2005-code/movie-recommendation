import streamlit as st
import pickle
import requests
import random

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

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
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    )
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_trailer(movie_id):
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    )
    if r.status_code != 200:
        return None
    for v in r.json().get("results", []):
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

    st.markdown("""
    <div class="card">
    <h4>✨ Features</h4>
    <ul>
        <li>Content-based movie recommendations</li>
        <li>Watch trailers inside the app</li>
        <li>Surprise Me – random movie discovery</li>
        <li>Mood-based recommendations</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ================= RECOMMENDED =================
elif page == "🎥 Recommended":
    st.markdown("<h2>🎥 Movie Recommendations</h2>", unsafe_allow_html=True)

    selected_movie = st.selectbox(
        "Choose a movie",
        movies['title'].values
    )

    if st.button("🚀 Recommend"):
        recs = recommend(selected_movie, 5)
        cols = st.columns(5)

        for i, rec in enumerate(recs):
            movie_data = movies.iloc[rec[0]]
            poster = fetch_poster(movie_data.movie_id)
            trailer_key = fetch_trailer(movie_data.movie_id)

            with cols[i]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(f"**{movie_data.title}**")

                if trailer_key:
                    if st.button("🎬 Watch Trailer", key=f"rec_{movie_data.movie_id}"):
                        st.markdown(
                            f"""
                            <iframe width="100%" height="215"
                            src="https://www.youtube.com/embed/{trailer_key}"
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
        trailer_key = fetch_trailer(movie.movie_id)

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        if poster:
            st.image(poster, width=300)

        st.markdown(f"### 🍿 {movie.title}")

        if trailer_key:
            if st.button("🎬 Watch Trailer", key=f"surprise_{movie.movie_id}"):
                st.markdown(
                    f"""
                    <iframe width="100%" height="300"
                    src="https://www.youtube.com/embed/{trailer_key}"
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
        "Romantic ❤️": ["romance", "love"],
        "Happy 😄": ["comedy", "fun"],
        "Sad 😢": ["drama"],
        "Excited 🤩": ["action", "thriller"],
        "Relaxed 😌": ["family", "animation"]
    }

    mood = st.selectbox("Select your mood", list(mood_map.keys()))

    if st.button("😊 Recommend by Mood"):
        keywords = mood_map[mood]

        mood_movies = movies[
            movies['tags'].str.contains("|".join(keywords), case=False, na=False)
        ]

        if mood_movies.empty:
            st.warning("No movies found for this mood.")
        else:
            sample_movies = mood_movies.sample(min(5, len(mood_movies)))
            cols = st.columns(5)

            for i, (_, movie) in enumerate(sample_movies.iterrows()):
                poster = fetch_poster(movie.movie_id)
                trailer_key = fetch_trailer(movie.movie_id)

                with cols[i]:
                    st.markdown("<div class='card'>", unsafe_allow_html=True)

                    if poster:
                        st.image(poster, use_container_width=True)

                    st.markdown(f"**{movie.title}**")

                    if trailer_key:
                        if st.button("🎬 Watch Trailer", key=f"mood_{movie.movie_id}"):
                            st.markdown(
                                f"""
                                <iframe width="100%" height="215"
                                src="https://www.youtube.com/embed/{trailer_key}"
                                frameborder="0" allowfullscreen>
                                </iframe>
                                """,
                                unsafe_allow_html=True
                            )

                    st.markdown("</div>", unsafe_allow_html=True)
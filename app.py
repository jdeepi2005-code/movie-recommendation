import streamlit as st
import requests
import random

# ================= CONFIG =================
TMDB_API_KEY = "YOUR_TMDB_API_KEY"
BASE_URL = "https://api.themoviedb.org/3"

st.set_page_config(
    page_title="Movie Recommendation App",
    page_icon="🎬",
    layout="wide"
)

# ================= SESSION STATE =================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# ================= CUSTOM CSS =================
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #1c0f2f, #3a1c71);
}
.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: white;
    margin-bottom: 20px;
}
.movie-card {
    background: #1e1e2f;
    padding: 15px;
    border-radius: 18px;
    margin-bottom: 25px;
}
.movie-title {
    color: #ffffff;
    font-size: 22px;
    font-weight: bold;
}
.movie-text {
    color: #d1d1d1;
}
.stButton>button {
    border-radius: 25px;
    background: linear-gradient(90deg, #ff4b2b, #ff416c);
    color: white;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ================= FUNCTIONS =================
def get_movies(endpoint):
    url = f"{BASE_URL}/{endpoint}?api_key={TMDB_API_KEY}"
    return requests.get(url).json()["results"]

def get_trailer(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()["results"]
    for v in data:
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

def movie_card(movie, reason=None):
    st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.image(
            f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
            use_container_width=True
        )

    with col2:
        st.markdown(f"<div class='movie-title'>{movie['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='movie-text'>⭐ IMDb {movie['vote_average']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='movie-text'>{movie['overview'][:180]}...</div>", unsafe_allow_html=True)

        if reason:
            st.success(f"🎯 Recommended because you liked **{reason}**")

        trailer = get_trailer(movie["id"])
        if trailer:
            st.markdown(f"[▶ Watch Trailer]({trailer})")

        if st.button("❤️ Add to Watchlist", key=f"wl_{movie['id']}"):
            if movie not in st.session_state.watchlist:
                st.session_state.watchlist.append(movie)
                st.success("Added to Watchlist!")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("<div class='main-title'>🎬 Movie Recommendation System</div>", unsafe_allow_html=True)

# ================= TOP NAVIGATION =================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Home",
    "🤖 Recommend",
    "🎲 Surprise Me",
    "❤️ Watchlist"
])

# ================= HOME =================
with tab1:
    st.subheader("🔥 Now Playing")
    movies = get_movies("movie/now_playing")

    for m in movies[:6]:
        movie_card(m)

# ================= RECOMMEND =================
with tab2:
    st.subheader("🤖 Smart Recommendations")

    movies = get_movies("movie/popular")
    titles = [m["title"] for m in movies]

    selected = st.selectbox("Select a movie", titles)

    if st.button("🚀 Get Recommendations"):
        chosen = next(m for m in movies if m["title"] == selected)
        similar = get_movies(f"movie/{chosen['id']}/similar")

        for sm in similar[:5]:
            movie_card(sm, reason=selected)

# ================= SURPRISE ME =================
with tab3:
    st.subheader("🎁 Surprise Movie Pick")

    if st.button("🎲 Surprise Me!"):
        movie = random.choice(get_movies("movie/popular"))
        movie_card(movie)

# ================= WATCHLIST =================
with tab4:
    st.subheader("❤️ My Watchlist")

    if not st.session_state.watchlist:
        st.info("Your watchlist is empty")
    else:
        for m in st.session_state.watchlist:
            movie_card(m)
            if st.button("❌ Remove", key=f"rm_{m['id']}"):
                st.session_state.watchlist.remove(m)
                st.experimental_rerun()
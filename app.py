import streamlit as st
import pickle
import requests
import random

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# ================= SESSION STATE =================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ================= UI STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #8e2de2, #4a00e0); /* Purple gradient */
}

.top-nav {
    display: flex;
    justify-content: space-around;
    background: #4b0082; /* Dark purple nav */
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 25px;
}

.top-nav button {
    background: none;
    border: none;
    color: white;
    font-size: 18px;
    cursor: pointer;
    font-weight: bold;
}

.movie-card {
    background: white;
    border-radius: 16px;
    padding: 12px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    text-align: center;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= FUNCTIONS =================
def recommend(movie, n=5):
    idx = movies[movies["title"] == movie].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:n+1]
    return scores

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    for v in r.json().get("results", []):
        if v["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

def fetch_omdb(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    return requests.get(url).json()

# ================= TOP NAV =================
st.markdown('<div class="top-nav">', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

if c1.button("🏠 Home"):
    st.session_state.page = "Home"
if c2.button("🎯 Recommend"):
    st.session_state.page = "Recommend"
if c3.button("❤️ Watchlist"):
    st.session_state.page = "Watchlist"
if c4.button("🎲 Surprise Me"):
    st.session_state.page = "Surprise"

st.markdown('</div>', unsafe_allow_html=True)

# ================= HOME =================
if st.session_state.page == "Home":
    st.title("🎬 Movie Recommendation System")
    st.write("Discover movies you'll love using Machine Learning")

# ================= RECOMMEND =================
elif st.session_state.page == "Recommend":
    st.header("🎯 Choose a Movie")

    movie_name = st.selectbox("Select a movie", movies["title"].values)
    num = st.slider("Number of recommendations", 3, 10, 5)

    if st.button("Recommend 🚀"):
        recs = recommend(movie_name, num)
        st.subheader("✨ Recommended Movies")

        cols = st.columns(5)
        for i, r in enumerate(recs):
            m = movies.iloc[r[0]]
            poster = fetch_poster(m.movie_id)
            trailer = fetch_trailer(m.movie_id)
            omdb = fetch_omdb(m.title)

            with cols[i % 5]:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                if poster:
                    st.image(poster)
                st.write(f"**{m.title}**")
                st.caption(f"Because you liked **{movie_name}**")
                st.caption(f"⭐ IMDb: {omdb.get('imdbRating','N/A')}")
                if st.button("❤️ Add", key=m.title):
                    st.session_state.watchlist.append(m.title)
                if trailer:
                    st.markdown(f"[▶ Watch Trailer]({trailer})")
                st.markdown('</div>', unsafe_allow_html=True)

# ================= WATCHLIST =================
elif st.session_state.page == "Watchlist":
    st.header("❤️ Your Watchlist")
    if not st.session_state.watchlist:
        st.info("No movies added yet")
    else:
        for m in set(st.session_state.watchlist):
            st.write("🎬", m)

# ================= SURPRISE =================
elif st.session_state.page == "Surprise":
    st.header("🎲 Surprise Movie")
    m = movies.sample(1).iloc[0]
    poster = fetch_poster(m.movie_id)
    trailer = fetch_trailer(m.movie_id)

    if poster:
        st.image(poster, width=300)
    st.subheader(m.title)
    if trailer:
        st.markdown(f"[▶ Watch Trailer]({trailer})")
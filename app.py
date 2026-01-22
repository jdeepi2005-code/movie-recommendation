import streamlit as st
import pickle
import requests

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ================= MODERN UI =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
}

.hero {
    background: linear-gradient(135deg, #ff512f, #dd2476);
    padding: 30px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 30px;
    box-shadow: 0px 15px 40px rgba(0,0,0,0.6);
}

.hero h1 {
    font-size: 46px;
    font-weight: 700;
    color: white;
}

.hero p {
    font-size: 18px;
    opacity: 0.9;
}

.movie-card {
    background: rgba(0,0,0,0.55);
    border-radius: 18px;
    padding: 14px;
    text-align: center;
    transition: all 0.35s ease;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.6);
}

.movie-card:hover {
    transform: translateY(-10px) scale(1.05);
}

.movie-card img {
    border-radius: 14px;
}

.imdb {
    background: #f5c518;
    color: black;
    font-weight: 700;
    padding: 6px 14px;
    border-radius: 20px;
    display: inline-block;
    margin-top: 10px;
}

.add-btn button {
    background: linear-gradient(135deg, #ff512f, #dd2476);
    border-radius: 20px;
    font-weight: bold;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #000428, #004e92);
}
</style>
""", unsafe_allow_html=True)

# ================= HERO =================
st.markdown("""
<div class="hero">
    <h1>🎬 Movie Recommendation System</h1>
    <p>Discover movies you’ll love — powered by Machine Learning</p>
</div>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= SESSION =================
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ================= SIDEBAR =================
st.sidebar.title("🎛 Personalize")
num_recommendations = st.sidebar.slider("🎯 Recommendations", 3, 10, 5)

st.sidebar.markdown("---")
st.sidebar.subheader("❤️ Favorites")
for f in st.session_state.favorites:
    st.sidebar.write("•", f)

# ================= FUNCTIONS =================
def recommend(movie, n):
    index = movies[movies["title"] == movie].index[0]
    distances = similarity[index]
    return sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:n+1]

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_omdb(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    return requests.get(url).json()

# ================= INPUT =================
st.subheader("🔍 Choose a Movie")

movie_input = st.text_input("Search movie name")
selected_movie = st.selectbox("Or select", movies["title"].values)

final_movie = movie_input if movie_input in movies["title"].values else selected_movie
st.success(f"🎥 Selected: {final_movie}")

# ================= RECOMMEND =================
if st.button("🚀 Recommend Movies"):
    with st.spinner("Finding best matches..."):
        recs = recommend(final_movie, num_recommendations)

    st.subheader("🌟 Recommended For You")

    cols = st.columns(5)
    for idx, rec in enumerate(recs):
        movie = movies.iloc[rec[0]]
        poster = fetch_poster(movie.movie_id)
        omdb = fetch_omdb(movie.title)

        with cols[idx % 5]:
            st.markdown('<div class="movie-card">', unsafe_allow_html=True)

            if poster:
                st.image(poster, use_container_width=True)

            st.markdown(f"**{movie.title}**")

            st.markdown(
                f'<div class="imdb">⭐ IMDb {omdb.get("imdbRating", "N/A")}</div>',
                unsafe_allow_html=True
            )

            if st.button("❤️ Add to Favorites", key=movie.title):
                st.session_state.favorites.append(movie.title)

            st.markdown("</div>", unsafe_allow_html=True)
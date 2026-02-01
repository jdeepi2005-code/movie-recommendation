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

# ================= THEME TOGGLE =================
theme = st.sidebar.radio("🎨 Theme", ["Light", "Dark"])

if theme == "Dark":
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: white;
    }
    .movie-card {
        background-color: #111827;
        border-radius: 16px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.7);
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {
        background: #f5f7fb;
        color: black;
    }
    .movie-card {
        background-color: white;
        border-radius: 16px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<h1 style='text-align:center;'>🎬 Movie Recommendation System</h1>
<p style='text-align:center;'>Machine Learning Based Movie Suggestions</p>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Settings")
num_recommendations = st.sidebar.slider("Number of Recommendations", 3, 10, 5)

# ================= FUNCTIONS =================
def recommend(movie, n):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:n+1]
    return movie_list

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_omdb(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    return requests.get(url).json()

# ================= MOVIE SELECTION =================
st.subheader("🎞️ Select a Movie")
selected_movie = st.selectbox("Movie List", movies['title'].values)

st.success(f"🎥 Selected Movie: **{selected_movie}**")

# ================= RECOMMEND =================
if st.button("🚀 Recommend Movies"):
    with st.spinner("Finding similar movies..."):
        recommendations = recommend(selected_movie, num_recommendations)

    st.subheader("🌟 Recommended Movies")

    cols = st.columns(5)
    for idx, rec in enumerate(recommendations):
        movie = movies.iloc[rec[0]]
        poster = fetch_poster(movie.movie_id)
        omdb = fetch_omdb(movie.title)

        with cols[idx % 5]:
            st.markdown("<div class='movie-card'>", unsafe_allow_html=True)

            if poster:
                st.image(poster, use_container_width=True)

            st.markdown(f"**{movie.title}**")
            st.caption(f"⭐ IMDb: {omdb.get('imdbRating', 'N/A')}")
            st.caption(f"🎭 Genre: {omdb.get('Genre', 'N/A')}")
            st.caption(f"📅 Year: {omdb.get('Year', 'N/A')}")

            st.markdown("</div>", unsafe_allow_html=True)
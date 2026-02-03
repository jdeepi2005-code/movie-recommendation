import streamlit as st
import pickle
import requests

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# ================= SIDEBAR NAV =================
st.sidebar.title("🎬 Movie App")
page = st.sidebar.radio("Navigate", ["🏠 Home", "🎥 Recommend", "ℹ️ About"])

theme = st.sidebar.radio("🎨 Theme", ["Light", "Dark"])

# ================= THEME =================
if theme == "Dark":
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg,#0f2027,#203a43,#2c5364); color:white; }
    .card { background:#111827; padding:15px; border-radius:15px; box-shadow:0 10px 25px rgba(0,0,0,.7); }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp { background:#f5f7fb; color:black; }
    .card { background:white; padding:15px; border-radius:15px; box-shadow:0 8px 20px rgba(0,0,0,.15); }
    </style>
    """, unsafe_allow_html=True)

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= FUNCTIONS =================
def recommend(movie, n):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    return sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:n+1]

def fetch_poster(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    ).json()
    return "https://image.tmdb.org/t/p/w500"+data["poster_path"] if data.get("poster_path") else None

def fetch_omdb(title):
    return requests.get(
        f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    ).json()

def fetch_trailer(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    ).json()
    for v in data.get("results", []):
        if v["type"]=="Trailer" and v["site"]=="YouTube":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

# ================= HOME PAGE =================
if page == "🏠 Home":
    st.markdown("<h1 style='text-align:center;'>🎬 Movie Recommendation System</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Discover Movies You’ll Love ❤️</h3>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <h4>✨ Features</h4>
    <ul>
    <li>ML-based personalized recommendations</li>
    <li>Movie posters, ratings & trailers</li>
    <li>Light & Dark theme</li>
    <li>Fast & interactive UI</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ================= RECOMMEND PAGE =================
elif page == "🎥 Recommend":
    st.markdown("<h2>🎥 Movie Recommendations</h2>", unsafe_allow_html=True)

    movie = st.selectbox("Select a Movie", movies['title'].values)
    n = st.slider("Number of Recommendations", 3, 10, 5)

    if st.button("🚀 Recommend"):
        recs = recommend(movie, n)
        cols = st.columns(5)

        for idx, rec in enumerate(recs):
            m = movies.iloc[rec[0]]
            poster = fetch_poster(m.movie_id)
            omdb = fetch_omdb(m.title)
            trailer = fetch_trailer(m.movie_id)

            with cols[idx % 5]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(f"**{m.title}**")
                st.caption(f"⭐ IMDb: {omdb.get('imdbRating','N/A')}")
                st.caption(f"🎭 {omdb.get('Genre','N/A')}")

                if trailer:
                    if st.button("🎬 Watch Trailer", key=m.movie_id):
                        st.video(trailer)

                st.markdown("</div>", unsafe_allow_html=True)

# ================= ABOUT PAGE =================
elif page == "ℹ️ About":
    st.markdown("<h2>ℹ️ About This Project</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
    <p>This Movie Recommendation System uses <b>Content-Based Filtering</b>
    and <b>Cosine Similarity</b> to suggest movies similar to the selected one.</p>

    <p><b>Technologies Used:</b></p>
    <ul>
    <li>Python & Streamlit</li>
    <li>Machine Learning</li>
    <li>TMDB & OMDB APIs</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
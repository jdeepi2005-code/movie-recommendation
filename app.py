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

# ================= SIDEBAR NAV =================
st.sidebar.title("🎬 Movie App")
page = st.sidebar.radio("Navigate", ["🏠 Home", "🎥 Recommend", "📌 Watchlist", "ℹ️ About"])
theme = st.sidebar.radio("🎨 Theme", ["Light", "Dark"])

# ================= THEME =================
if theme == "Dark":
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg,#0f2027,#203a43,#2c5364); color:white; }
    .card {
        background:#111827;
        padding:15px;
        border-radius:15px;
        box-shadow:0 10px 25px rgba(0,0,0,.7);
        margin-bottom:15px;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp { background:#f5f7fb; color:black; }
    .card {
        background:white;
        padding:15px;
        border-radius:15px;
        box-shadow:0 8px 20px rgba(0,0,0,.15);
        margin-bottom:15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= FUNCTIONS =================
def recommend(movie, n):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    return sorted(list(enumerate(distances)),
                  reverse=True,
                  key=lambda x: x[1])[1:n+1]

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

def fetch_omdb(title):
    return requests.get(
        f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    ).json()

def fetch_trailer(movie_id):
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    )
    if r.status_code != 200:
        return None
    data = r.json()
    for v in data.get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            return v["key"]
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
        <li>Movie posters, IMDb ratings & trailers</li>
        <li>Surprise Me & Mood-based recommendations</li>
        <li>Personal Watchlist</li>
        <li>Clean & responsive UI</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ================= RECOMMEND PAGE =================
elif page == "🎥 Recommend":
    st.markdown("<h2>🎥 Movie Recommendations</h2>", unsafe_allow_html=True)

    movie = st.selectbox("Select a Movie", movies['title'].values)
    n = st.slider("Number of Recommendations", 3, 10, 5)

    # -------- Surprise Me --------
    if st.button("🎲 Surprise Me"):
        movie = random.choice(movies['title'].values)
        st.success(f"🎬 Surprise Pick: {movie}")

    # -------- Mood Based --------
    st.markdown("### 😊 Mood-Based Recommendation")
    mood = st.selectbox(
        "Select your mood",
        ["Happy 😄", "Romantic ❤️", "Thriller 😈", "Sad 😢", "Inspirational 🌟"]
    )

    mood_map = {
        "Happy 😄": ["Comedy", "Adventure"],
        "Romantic ❤️": ["Romance"],
        "Thriller 😈": ["Thriller", "Action"],
        "Sad 😢": ["Drama"],
        "Inspirational 🌟": ["Biography"]
    }

    if st.button("😊 Recommend by Mood"):
        genres = mood_map[mood]
        mood_movies = movies[
            movies['genres'].str.contains("|".join(genres), case=False, na=False)
        ]
        for title in mood_movies['title'].head(5):
            st.write("🎬", title)

    # -------- Main Recommendation --------
    if st.button("🚀 Recommend"):
        recs = recommend(movie, n)
        cols = st.columns(5)

        for idx, rec in enumerate(recs):
            m = movies.iloc[rec[0]]
            poster = fetch_poster(m.movie_id)
            omdb = fetch_omdb(m.title)
            trailer_key = fetch_trailer(m.movie_id)

            with cols[idx % 5]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(f"**{m.title}**")
                st.caption(f"⭐ IMDb: {omdb.get('imdbRating','N/A')}")
                st.caption(f"🎭 Genre: {omdb.get('Genre','N/A')}")

                if trailer_key:
                    if st.button("🎬 Watch Trailer", key=f"trailer_{m.movie_id}"):
                        st.markdown(
                            f"""
                            <iframe width="100%" height="215"
                            src="https://www.youtube.com/embed/{trailer_key}"
                            frameborder="0" allowfullscreen>
                            </iframe>
                            """,
                            unsafe_allow_html=True
                        )

                if st.button("❤️ Add to Watchlist", key=f"watch_{m.movie_id}"):
                    if m.title not in st.session_state.watchlist:
                        st.session_state.watchlist.append(m.title)
                        st.success("Added to Watchlist!")

                st.markdown("</div>", unsafe_allow_html=True)

# ================= WATCHLIST PAGE =================
elif page == "📌 Watchlist":
    st.markdown("<h2>📌 My Watchlist</h2>", unsafe_allow_html=True)

    if st.session_state.watchlist:
        for w in st.session_state.watchlist:
            st.write("🎬", w)
    else:
        st.info("Your watchlist is empty.")

# ================= ABOUT PAGE =================
elif page == "ℹ️ About":
    st.markdown("<h2>ℹ️ About This Project</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="card">
    <p>
    This Movie Recommendation System uses
    <b>Content-Based Filtering</b> and
    <b>Cosine Similarity</b> to suggest movies.
    </p>

    <p><b>Technologies Used:</b></p>
    <ul>
        <li>Python & Streamlit</li>
        <li>Machine Learning</li>
        <li>TMDB & OMDB APIs</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
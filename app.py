import streamlit as st
import pickle
import requests

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Movie Recommender", layout="wide")

# ================= THEME =================
theme = st.sidebar.radio("Theme", ["Light", "Dark"])

if theme == "Dark":
    bg = "#0b1020"
    text = "#e5e7eb"
    card = "#111827"
    shadow = "rgba(0,0,0,0.5)"
    nav = "#0b1020"
else:
    bg = "#f6f6f6"
    text = "#111827"
    card = "#ffffff"
    shadow = "rgba(0,0,0,0.15)"
    nav = "#ffffff"

st.markdown(f"""
<style>
/* ===== Global ===== */
body {{
    background: {bg};
    color: {text};
    font-family: 'Arial', sans-serif;
}}

a {{
    text-decoration: none;
    color: inherit;
}}

.container {{
    padding: 20px 40px;
}}

.navbar {{
    width: 100%;
    background: {nav};
    padding: 15px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 2px 10px {shadow};
}}

.nav-title {{
    font-size: 24px;
    font-weight: 900;
    letter-spacing: 2px;
}}

.nav-links {{
    display: flex;
    gap: 25px;
    font-weight: 700;
    color: #6b7280;
}}

.nav-links a:hover {{
    color: #ff3b6a;
}}

.row-title {{
    font-size: 20px;
    font-weight: 900;
    margin-top: 30px;
    margin-bottom: 10px;
}}

.movie-row {{
    display: flex;
    overflow-x: auto;
    gap: 12px;
    padding-bottom: 10px;
}}

.movie-card {{
    width: 170px;
    border-radius: 10px;
    background: {card};
    box-shadow: 0 8px 18px {shadow};
    transition: transform 0.2s;
    cursor: pointer;
}}

.movie-card:hover {{
    transform: translateY(-8px);
}}

.movie-card img {{
    width: 100%;
    height: 250px;
    object-fit: cover;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}}

.movie-card .title {{
    padding: 10px;
    font-weight: 800;
    font-size: 14px;
}}

.movie-card .meta {{
    padding: 0 10px 10px 10px;
    color: #6b7280;
    font-size: 12px;
}}

.details {{
    display: flex;
    gap: 25px;
    margin-top: 20px;
}}

.details img {{
    width: 300px;
    border-radius: 12px;
    box-shadow: 0 15px 35px {shadow};
}}

.details-body {{
    width: 100%;
}}

.btn {{
    padding: 10px 15px;
    border-radius: 8px;
    background: #ff3b6a;
    color: white;
    font-weight: 800;
    border: none;
    cursor: pointer;
    margin-right: 10px;
}

.btn:hover {{
    opacity: 0.9;
}}
</style>
""", unsafe_allow_html=True)

# ================= DATA LOAD =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= SESSION STATE =================
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = movies['title'].values[0]

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "ratings" not in st.session_state:
    st.session_state.ratings = {}

if "reviews" not in st.session_state:
    st.session_state.reviews = {}

# ================= FUNCTIONS =================
def recommend(movie, n):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:n+1]
    return movie_list

def fetch_poster(movie_id):
    data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}").json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_trailer(movie_id):
    data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}").json()
    for t in ["Trailer", "Teaser", "Clip"]:
        for video in data.get("results", []):
            if video["site"] == "YouTube" and video["type"] == t:
                return f"https://www.youtube.com/watch?v={video['key']}"
    return None

def fetch_watch_providers(movie_id, country_code):
    data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}").json()
    results = data.get("results", {})
    return results.get(country_code, {})

def fetch_omdb(title):
    data = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}").json()
    return data

def fetch_details(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits"
    ).json()
    return data

# ================= NAVBAR =================
st.markdown("""
<div class="navbar">
    <div class="nav-title">Movie Recommender</div>
    <div class="nav-links">
        <a href="#home" onclick="window.location.reload()">Home</a>
        <a href="#rec" onclick="window.location.reload()">Recommendations</a>
        <a href="#fav" onclick="window.location.reload()">Favorites</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ================= NAV MENU =================
page = st.sidebar.selectbox("Menu", ["Home", "Recommendations", "Movie Details", "Favorites"])
st.session_state.page = page

# ================= MOVIE SELECT =================
st.sidebar.markdown("## 🎞️ Select Movie")
st.session_state.selected_movie = st.sidebar.selectbox("Choose movie", movies['title'].values)

# ================= HOME PAGE =================
if page == "Home":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<h2 class="row-title">Trending Movies</h2>', unsafe_allow_html=True)

    show_movies = movies.head(12)
    st.markdown('<div class="movie-row">', unsafe_allow_html=True)

    for _, movie in show_movies.iterrows():
        poster = fetch_poster(movie.movie_id)
        if poster:
            st.markdown(f'''
                <div class="movie-card" onclick="window.location.href='?page=Movie%20Details'">
                    <img src="{poster}" />
                    <div class="title">{movie.title}</div>
                </div>
            ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ================= RECOMMENDATION PAGE =================
if page == "Recommendations":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<h2 class="row-title" id="rec">Recommended Movies</h2>', unsafe_allow_html=True)

    n = st.sidebar.slider("Number of recommendations", 8, 20, 12)
    country = st.sidebar.selectbox("Country", ["IN", "US", "UK", "CA", "AU"])

    if st.sidebar.button("🚀 Recommend"):
        st.session_state.recommendations = recommend(st.session_state.selected_movie, n)

    if st.session_state.recommendations:
        st.markdown('<div class="movie-row">', unsafe_allow_html=True)

        for idx, rec in enumerate(st.session_state.recommendations):
            movie = movies.iloc[rec[0]]
            poster = fetch_poster(movie.movie_id)
            omdb = fetch_omdb(movie.title)

            if poster:
                st.markdown(f'''
                    <div class="movie-card">
                        <img src="{poster}" />
                        <div class="title">{movie.title}</div>
                        <div class="meta">⭐ {omdb.get("imdbRating","N/A")}</div>
                    </div>
                ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ================= MOVIE DETAILS PAGE =================
if page == "Movie Details":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    movie_title = st.session_state.selected_movie
    movie_id = movies[movies['title'] == movie_title].iloc[0].movie_id

    details = fetch_details(movie_id)
    poster = "https://image.tmdb.org/t/p/w500" + details.get("poster_path", "")
    trailer = fetch_trailer(movie_id)

    st.markdown('<div class="details">', unsafe_allow_html=True)
    st.image(poster)

    st.markdown('<div class="details-body">', unsafe_allow_html=True)
    st.markdown(f"<h2>{details.get('title','')}</h2>", unsafe_allow_html=True)
    st.write(details.get("overview", "No overview available"))
    st.write("⭐ Rating:", details.get("vote_average", "N/A"))

    # Trailer button
    if trailer:
        st.markdown(f"[🎬 Watch Trailer]({trailer})", unsafe_allow_html=True)

    # Cast
    st.markdown("### 🎭 Cast")
    cast = details.get("credits", {}).get("cast", [])[:8]
    for c in cast:
        st.write(f"• {c.get('name')} as {c.get('character')}")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Reviews
    rating = st.slider("Rate this movie", 1, 5, 3)
    review = st.text_area("Write a review")

    if st.button("Submit Review"):
        st.session_state.ratings[movie_title] = rating
        st.session_state.reviews[movie_title] = review
        st.success("Review saved!")

    if movie_title in st.session_state.reviews:
        st.write("⭐ Rating:", st.session_state.ratings[movie_title])
        st.write("📝 Review:", st.session_state.reviews[movie_title])

    st.markdown('</div>', unsafe_allow_html=True)

# ================= FAVORITES PAGE =================
if page == "Favorites":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<h2 class="row-title" id="fav">Favorites</h2>', unsafe_allow_html=True)

    if st.session_state.favorites:
        for f in st.session_state.favorites:
            st.write("• " + f)
    else:
        st.write("No favorites yet.")
    st.markdown('</div>', unsafe_allow_html=True)
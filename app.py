import streamlit as st
import pickle
import requests

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Movie Recommender",
    layout="wide"
)

# ================= THEME TOGGLE =================
theme = st.sidebar.radio("🎨 Theme", ["Light", "Dark"])

# ================= CSS =================
if theme == "Dark":
    bg = "#0f172a"
    card = "#111827"
    text = "white"
    sidebar = "#0b1220"
else:
    bg = "#f8fafc"
    card = "#ffffff"
    text = "#111827"
    sidebar = "#f1f5f9"

st.markdown(f"""
<style>
body {{
    background: {bg};
    color: {text};
}}

.movie-card {{
    background-color: {card};
    border-radius: 15px;
    padding: 10px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    transition: transform 0.2s;
    min-height: 410px;
}}

.movie-card:hover {{
    transform: translateY(-5px);
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
}}

.btn-secondary {{
    padding: 10px 15px;
    border-radius: 8px;
    background: #3b82f6;
    color: white;
    font-weight: 800;
    border: none;
    cursor: pointer;
    margin-right: 10px;
}}

.navbar {{
    background: #111827;
    padding: 15px;
    border-radius: 10px;
    color: white;
    margin-bottom: 15px;
}}

.nav-title {{
    font-size: 22px;
    font-weight: 900;
}}
</style>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= SESSION STATE =================
if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "reviews" not in st.session_state:
    st.session_state.reviews = {}

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = movies['title'].values[0]

if "trailer_url" not in st.session_state:
    st.session_state.trailer_url = None

# ================= FUNCTIONS =================
def recommend(movie, n):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:n+1]
    return movie_list

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    return "https://image.tmdb.org/t/p/w500" + data["poster_path"] if data.get("poster_path") else None

def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    for t in ["Trailer", "Teaser", "Clip"]:
        for video in data.get("results", []):
            if video["site"] == "YouTube" and video["type"] == t:
                return f"https://www.youtube.com/watch?v={video['key']}"
    return None

def fetch_watch_providers(movie_id, country_code):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/watch/providers?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    results = data.get("results", {})
    return results.get(country_code, {})

def fetch_omdb(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    return requests.get(url).json()

def fetch_cast(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    cast = data.get("cast", [])[:6]
    return [c["name"] for c in cast]

# ================= NAVBAR =================
st.markdown("""
<div class="navbar">
    <div class="nav-title">Movie Recommender</div>
</div>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.header("🎬 Movie List")
st.session_state.selected_movie = st.sidebar.selectbox("Select Movie", movies['title'].values)

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Settings")
num_recommendations = st.sidebar.slider("Recommendations", 3, 12, 6)
country = st.sidebar.selectbox("Country", ["IN", "US", "UK", "CA", "AU"])
st.sidebar.markdown("---")

# ================= PAGE NAVIGATION =================
st.session_state.page = st.sidebar.radio("📌 Pages", ["Home", "Details", "Favorites"])

# ================= HOME PAGE =================
if st.session_state.page == "Home":
    st.subheader("Recommended Movies")

    if st.button("Recommend"):
        st.session_state.recommendations = recommend(st.session_state.selected_movie, num_recommendations)

    if st.session_state.recommendations:
        cols = st.columns(4)
        for idx, rec in enumerate(st.session_state.recommendations):
            movie = movies.iloc[rec[0]]
            poster = fetch_poster(movie.movie_id)
            omdb = fetch_omdb(movie.title)

            with cols[idx % 4]:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(f"**{movie.title}**")
                st.markdown(f'<div class="imdb">⭐ {omdb.get("imdbRating","N/A")}</div>', unsafe_allow_html=True)
                st.caption(f"📖 {omdb.get("Plot","N/A")[:120]}...")

                # Streaming Providers
                providers = fetch_watch_providers(movie.movie_id, country)
                flatrate = providers.get("flatrate", [])
                if flatrate:
                    logos = ""
                    for p in flatrate:
                        logo_url = "https://image.tmdb.org/t/p/original" + p["logo_path"]
                        logos += f'<img src="{logo_url}" width="35" style="margin-right:5px;" />'
                    st.markdown(logos, unsafe_allow_html=True)

                    watch_link = providers.get("link")
                    if watch_link:
                        st.markdown(f'<a class="btn" href="{watch_link}" target="_blank">Watch Now</a>', unsafe_allow_html=True)

                # Trailer
                trailer = fetch_trailer(movie.movie_id)
                if trailer:
                    st.markdown(f'<a class="btn-secondary" href="{trailer}" target="_blank">Watch Trailer</a>', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

# ================= DETAILS PAGE =================
elif st.session_state.page == "Details":
    st.subheader("Movie Details")
    movie_row = movies[movies['title'] == st.session_state.selected_movie].iloc[0]
    movie_id = movie_row.movie_id

    poster = fetch_poster(movie_id)
    omdb = fetch_omdb(st.session_state.selected_movie)
    cast = fetch_cast(movie_id)
    trailer = fetch_trailer(movie_id)
    providers = fetch_watch_providers(movie_id, country)

    cols = st.columns([1, 2])
    with cols[0]:
        if poster:
            st.image(poster, use_column_width=True)

    with cols[1]:
        st.markdown(f"## {st.session_state.selected_movie}")
        st.markdown(f"⭐ IMDb: {omdb.get('imdbRating','N/A')}")
        st.markdown(f"📅 Year: {omdb.get('Year','N/A')}")
        st.markdown(f"🎭 Genre: {omdb.get('Genre','N/A')}")
        st.markdown(f"📖 Synopsis: {omdb.get('Plot','N/A')}")

        st.markdown("### Cast")
        st.write(", ".join(cast))

        # Watch Providers
        flatrate = providers.get("flatrate", [])
        if flatrate:
            st.markdown("### Streaming Platforms")
            logos = ""
            for p in flatrate:
                logo_url = "https://image.tmdb.org/t/p/original" + p["logo_path"]
                logos += f'<img src="{logo_url}" width="40" style="margin-right:8px;" />'
            st.markdown(logos, unsafe_allow_html=True)

            watch_link = providers.get("link")
            if watch_link:
                st.markdown(f'<a class="btn" href="{watch_link}" target="_blank">Watch Now</a>', unsafe_allow_html=True)

        # Trailer
        if trailer:
            st.video(trailer)

# ================= FAVORITES PAGE =================
elif st.session_state.page == "Favorites":
    st.subheader("❤️ Favorites")

    if st.session_state.favorites:
        for m in st.session_state.favorites:
            st.write(m)
    else:
        st.write("No favorites yet.")
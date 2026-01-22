import streamlit as st
import pickle
import requests

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Movieflix - Recommender",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= LIGHT THEME ONLY =================
bg = "#f6f6f6"
text = "#111827"

st.markdown(f"""
<style>
/* ---------- Global ---------- */
body {{
    background: {bg};
    color: {text};
    font-family: 'Arial', sans-serif;
}}

a {{
    text-decoration: none;
    color: inherit;
}}

hr {{
    border: none;
    height: 1px;
    background: #e5e7eb;
}}

/* ---------- Navbar ---------- */
.navbar {{
    width: 100%;
    background: #ffffff;
    padding: 18px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    position: sticky;
    top: 0;
    z-index: 999;
}}

.nav-title {{
    font-weight: 800;
    font-size: 22px;
}}

.nav-links {{
    display: flex;
    gap: 20px;
    font-weight: 600;
    color: #374151;
}}

.nav-links a:hover {{
    color: #ff3b6a;
}}

.container {{
    padding: 30px 40px;
}}

.section-title {{
    font-size: 20px;
    font-weight: 800;
    margin-top: 20px;
    margin-bottom: 10px;
}}

.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    gap: 18px;
    margin-top: 20px;
}}

.card {{
    background: white;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 10px 25px rgba(0,0,0,0.12);
    transition: transform 0.2s, box-shadow 0.2s;
}}

.card:hover {{
    transform: translateY(-6px);
    box-shadow: 0 18px 40px rgba(0,0,0,0.2);
}}

.card img {{
    width: 100%;
    height: 320px;
    object-fit: cover;
}}

.card-body {{
    padding: 12px;
}}

.card-title {{
    font-weight: 800;
    font-size: 16px;
    margin: 8px 0 4px 0;
}}

.card-meta {{
    font-size: 13px;
    color: #6b7280;
    margin-bottom: 8px;
}}

.imdb {{
    background-color: #f5c518;
    color: black;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: bold;
    display: inline-block;
    font-size: 12px;
}}

.btn {{
    margin-top: 8px;
    width: 100%;
}}

.details {{
    display: flex;
    gap: 25px;
    align-items: flex-start;
    margin-top: 20px;
}}

.details img {{
    width: 260px;
    border-radius: 10px;
    box-shadow: 0 15px 35px rgba(0,0,0,0.18);
}}

.details-body {{
    width: 100%;
}}

.details-body h2 {{
    margin-top: 0;
}}

.details-body p {{
    line-height: 1.6;
    color: #4b5563;
}}

.provider-logo {{
    width: 40px;
    height: 40px;
    object-fit: contain;
    margin-right: 8px;
}}

.review-box {{
    background: #ffffff;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.12);
    margin-top: 15px;
}}
</style>
""", unsafe_allow_html=True)


# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= SESSION STATE =================
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "favorites" not in st.session_state:
    st.session_state.favorites = []

if "ratings" not in st.session_state:
    st.session_state.ratings = {}

if "reviews" not in st.session_state:
    st.session_state.reviews = {}

if "page_num" not in st.session_state:
    st.session_state.page_num = 0

if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = movies['title'].values[0]


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
    url = "https://image.tmdb.org/t/p/w500"
    data = requests.get(f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}").json()
    if data.get("poster_path"):
        return url + data["poster_path"]
    return None

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
    country_data = results.get(country_code, {})
    return country_data

def fetch_omdb(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    return requests.get(url).json()

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&append_to_response=credits"
    data = requests.get(url).json()
    return data


# ================= NAVBAR =================
st.markdown("""
<div class="navbar">
    <div class="nav-title">Movieflix</div>
    <div class="nav-links">
        <a href="#home">Home</a>
        <a href="#recommend">Recommendations</a>
        <a href="#favorites">Favorites</a>
        <a href="#about">About</a>
    </div>
</div>
""", unsafe_allow_html=True)


# ================= PAGE SELECTION =================
page = st.sidebar.selectbox("📌 Menu", ["Home", "Recommendations", "Movie Details", "Favorites", "About"])
st.session_state.page = page


# ================= SIDEBAR MOVIE SELECT =================
st.sidebar.markdown("## 🎞️ Select Movie")
st.session_state.selected_movie = st.sidebar.selectbox("Choose Movie", movies['title'].values)


# ================= HOME =================
if page == "Home":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title" id="home">Welcome to Movieflix</h2>', unsafe_allow_html=True)
    st.write("A Netflix-style movie recommendation system built with Streamlit.")
    st.markdown("</div>", unsafe_allow_html=True)


# ================= RECOMMENDATIONS =================
if page == "Recommendations":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title" id="recommend">Recommended Movies</h2>', unsafe_allow_html=True)

    num_recommendations = st.sidebar.slider("Number of recommendations", 8, 20, 12)
    country = st.sidebar.selectbox("Country", ["IN", "US", "UK", "CA", "AU"])

    if st.sidebar.button("🚀 Recommend"):
        st.session_state.recommendations = recommend(st.session_state.selected_movie, num_recommendations)
        st.session_state.page_num = 0

    per_page = 8
    start = st.session_state.page_num * per_page
    end = start + per_page

    if st.session_state.recommendations:
        rec_page = st.session_state.recommendations[start:end]

        st.markdown('<div class="grid">', unsafe_allow_html=True)

        for idx, rec in enumerate(rec_page):
            movie = movies.iloc[rec[0]]
            poster = fetch_poster(movie.movie_id)
            omdb = fetch_omdb(movie.title)
            providers = fetch_watch_providers(movie.movie_id, country)

            st.markdown('<div class="card">', unsafe_allow_html=True)

            if poster:
                st.image(poster)

            st.markdown('<div class="card-body">', unsafe_allow_html=True)
            st.markdown(f'<div class="card-title">{movie.title}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="imdb">⭐ {omdb.get("imdbRating","N/A")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-meta">{omdb.get("Genre","N/A")} • {omdb.get("Year","N/A")}</div>', unsafe_allow_html=True)

            # Streaming only + logos
            if providers:
                flatrate = providers.get("flatrate", [])
                if flatrate:
                    cols_logo = st.columns(len(flatrate))
                    for i, p in enumerate(flatrate):
                        logo_url = "https://image.tmdb.org/t/p/original" + p["logo_path"]
                        with cols_logo[i]:
                            st.image(logo_url, width=40)

                    watch_link = providers.get("link")
                    if watch_link:
                        st.markdown(f"[👉 Watch Now]({watch_link})", unsafe_allow_html=True)
                else:
                    st.write("📌 Streaming not available")

            if st.button("📝 Details", key=f"details_{idx}"):
                st.session_state.page = "Movie Details"
                st.session_state.selected_movie = movie.title
                st.experimental_rerun()

            if st.button("❤️ Favorite", key=f"fav_{idx}"):
                st.session_state.favorites.append(movie.title)

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅ Previous") and st.session_state.page_num > 0:
                st.session_state.page_num -= 1
                st.experimental_rerun()
        with col2:
            if st.button("Next ➡") and end < len(st.session_state.recommendations):
                st.session_state.page_num += 1
                st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ================= MOVIE DETAILS =================
if page == "Movie Details":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Movie Details</h2>', unsafe_allow_html=True)

    movie_title = st.session_state.selected_movie
    movie_id = movies[movies['title'] == movie_title].iloc[0].movie_id
    movie_data = fetch_movie_details(movie_id)

    poster = "https://image.tmdb.org/t/p/w500" + movie_data.get("poster_path", "")
    trailer = fetch_trailer(movie_id)

    st.markdown('<div class="details">', unsafe_allow_html=True)
    st.image(poster)
    st.markdown('<div class="details-body">', unsafe_allow_html=True)
    st.markdown(f"<h2>{movie_data.get('title', '')}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p><strong>⭐ Rating:</strong> {movie_data.get('vote_average','N/A')} / 10</p>", unsafe_allow_html=True)
    st.markdown(f"<p><strong>📅 Release Date:</strong> {movie_data.get('release_date','N/A')}</p>", unsafe_allow_html=True)
    st.markdown(f"<p><strong>⏳ Runtime:</strong> {movie_data.get('runtime','N/A')} mins</p>", unsafe_allow_html=True)
    st.markdown(f"<p><strong>📖 Overview:</strong> {movie_data.get('overview','N/A')}</p>", unsafe_allow_html=True)

    # Cast
    st.markdown("<h3>🎭 Cast</h3>", unsafe_allow_html=True)
    cast_list = movie_data.get("credits", {}).get("cast", [])[:8]
    for cast in cast_list:
        st.write(f"• {cast.get('name')} as {cast.get('character')}")

    # Trailer
    if trailer:
        st.markdown(f"[🎬 Watch Trailer]({trailer})", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Rating + Review
    st.markdown('<div class="review-box">', unsafe_allow_html=True)
    st.markdown("### ⭐ Rate & Review")
    rating = st.slider("Rate this movie", 1, 5, 3, key="rate_slider")
    review = st.text_area("Write your review", key="review_area")

    if st.button("Submit Review"):
        st.session_state.ratings[movie_title] = rating
        st.session_state.reviews[movie_title] = review
        st.success("Review added!")

    if movie_title in st.session_state.reviews:
        st.markdown("### 💬 Your Review")
        st.write(f"⭐ **Rating:** {st.session_state.ratings[movie_title]}")
        st.write(f"📝 **Review:** {st.session_state.reviews[movie_title]}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ================= FAVORITES =================
if page == "Favorites":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title" id="favorites">Favorites</h2>', unsafe_allow_html=True)

    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.write("• " + fav)
    else:
        st.write("No favorites yet.")
    st.markdown("</div>", unsafe_allow_html=True)


# ================= ABOUT =================
if page == "About":
    st.markdown('<div class="container">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title" id="about">About</h2>', unsafe_allow_html=True)
    st.write("This app recommends movies using TMDB and OMDB APIs.")
    st.write("Built using Streamlit with HTML/CSS styling to look like a website.")
    st.markdown("</div>", unsafe_allow_html=True)
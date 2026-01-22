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

# ================= LIGHT THEME ONLY =================
bg = "#f7f7f7"
card = "#ffffff"
sidebar = "#ffffff"
text = "#111827"

st.markdown(f"""
<style>
/* ---------- App Background ---------- */
.stApp {{
    background: {bg};
    color: {text};
}}

/* ---------- Header ---------- */
.header {{
    background: linear-gradient(90deg, #ff512f, #dd2476);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 20px;
}}

.header h1 {{
    font-size: 40px;
    color: white;
    margin-bottom: 0;
}}

.header p {{
    color: rgba(255,255,255,0.9);
    margin-top: 5px;
}}

/* ---------- Movie Card ---------- */
.movie-card {{
    background-color: {card};
    border-radius: 16px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.10);
    transition: transform 0.2s, box-shadow 0.2s;
    min-height: 520px;
}}

.movie-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.18);
}}

.movie-title {{
    font-weight: 800;
    font-size: 18px;
    margin-top: 10px;
}}

.imdb {{
    background-color: #f5c518;
    color: black;
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: bold;
    display: inline-block;
    margin-top: 6px;
}}

.meta {{
    font-size: 13px;
    color: #6b7280;
    margin-top: 6px;
}}

.btn {{
    margin-top: 8px;
}}

[data-testid="stSidebar"] {{
    background-color: {sidebar};
    padding: 20px;
    border-radius: 12px;
}}

/* ---------- Button Styles ---------- */
.stButton>button {{
    background: linear-gradient(90deg, #ff512f, #dd2476);
    color: white;
    border-radius: 10px;
    padding: 8px 12px;
    border: none;
}}

.stButton>button:hover {{
    opacity: 0.9;
}}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="header">
    <h1>🎬 Movie Recommendation System</h1>
    <p>Find movies similar to your favorite one</p>
</div>
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

if "trailer_url" not in st.session_state:
    st.session_state.trailer_url = None

if "ratings" not in st.session_state:
    st.session_state.ratings = {}

if "reviews" not in st.session_state:
    st.session_state.reviews = {}

if "page_num" not in st.session_state:
    st.session_state.page_num = 0

# ================= SIDEBAR MENU =================
menu = st.sidebar.selectbox(
    "📌 Navigate",
    ["Home", "Recommendations", "Movie Details", "Favorites", "About"]
)
st.session_state.page = menu

# ================= SIDEBAR MOVIE LIST =================
st.sidebar.markdown("## 🎞️ Movie List")
selected_movie = st.sidebar.selectbox("Select Movie", movies['title'].values)

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
    url = f"https://image.tmdb.org/t/p/w500"
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

# ================= HOME PAGE =================
if st.session_state.page == "Home":
    st.write("Welcome to the Movie Recommendation System!")
    st.write("Use the sidebar to navigate to Recommendations or Movie Details.")

# ================= RECOMMENDATIONS PAGE =================
if st.session_state.page == "Recommendations":
    st.sidebar.header("⚙️ Settings")
    num_recommendations = st.sidebar.slider("Number of recommendations", 4, 12, 8)
    country = st.sidebar.selectbox("🌍 Country", ["IN", "US", "UK", "CA", "AU"])

    st.subheader("🎞️ Selected Movie")
    st.success(f"🎥 {selected_movie}")

    if st.button("🚀 Recommend"):
        with st.spinner("Finding similar movies..."):
            st.session_state.recommendations = recommend(selected_movie, num_recommendations)
            st.session_state.page_num = 0

    # Pagination
    per_page = 4
    start = st.session_state.page_num * per_page
    end = start + per_page

    if st.session_state.recommendations:
        st.subheader("🌟 Recommended Movies")
        rec_page = st.session_state.recommendations[start:end]
        cols = st.columns(4)

        for idx, rec in enumerate(rec_page):
            movie = movies.iloc[rec[0]]
            poster = fetch_poster(movie.movie_id)
            trailer = fetch_trailer(movie.movie_id)
            providers = fetch_watch_providers(movie.movie_id, country)
            omdb = fetch_omdb(movie.title)

            with cols[idx]:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(f'<div class="movie-title">{movie.title}</div>', unsafe_allow_html=True)
                st.markdown(
                    f'<div class="imdb">⭐ IMDb {omdb.get("imdbRating", "N/A")}</div>',
                    unsafe_allow_html=True
                )

                st.markdown(f'<div class="meta">🎭 {omdb.get("Genre", "N/A")} • 📅 {omdb.get("Year", "N/A")}</div>', unsafe_allow_html=True)
                st.caption(f"📖 {omdb.get('Plot', 'N/A')}")

                # Streaming Only (with Logos)
                if providers:
                    flatrate = providers.get("flatrate", [])
                    if flatrate:
                        st.caption("📺 Streaming On:")
                        cols_logo = st.columns(len(flatrate))
                        for i, p in enumerate(flatrate):
                            logo_url = "https://image.tmdb.org/t/p/original" + p["logo_path"]
                            with cols_logo[i]:
                                st.image(logo_url, width=50)
                                st.caption(p["provider_name"])

                        watch_link = providers.get("link")
                        if watch_link:
                            st.markdown(f"[👉 Watch Now]({watch_link})", unsafe_allow_html=True)
                    else:
                        st.caption("📌 Streaming not available in this country")
                else:
                    st.caption("📌 Not available in this country")

                # Trailer
                if trailer:
                    if st.button(f"🎬 Watch Trailer", key=f"trailer_{idx}"):
                        st.session_state.trailer_url = trailer
                else:
                    st.caption("🎥 Trailer not available")

                # Favorites
                if st.button("❤️ Add to Favorites", key=f"fav_{idx}"):
                    st.session_state.favorites.append(movie.title)

                st.markdown('</div>', unsafe_allow_html=True)

        # Pagination Buttons
        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("⬅ Previous") and st.session_state.page_num > 0:
                st.session_state.page_num -= 1
        with col_next:
            if st.button("Next ➡") and end < len(st.session_state.recommendations):
                st.session_state.page_num += 1

# ================= MOVIE DETAILS PAGE =================
if st.session_state.page == "Movie Details":
    st.subheader("🎬 Movie Details")

    movie_data = fetch_movie_details(movies[movies['title'] == selected_movie].iloc[0].movie_id)

    poster = "https://image.tmdb.org/t/p/w500" + movie_data.get("poster_path", "")
    st.image(poster, width=250)

    st.markdown(f"## {movie_data.get('title', '')}")
    st.markdown(f"**⭐ Rating:** {movie_data.get('vote_average', 'N/A')} / 10")
    st.markdown(f"**📅 Release Date:** {movie_data.get('release_date', 'N/A')}")
    st.markdown(f"**⏳ Runtime:** {movie_data.get('runtime', 'N/A')} mins")
    st.markdown(f"**📖 Overview:** {movie_data.get('overview', 'N/A')}")

    # Cast
    st.markdown("### 🎭 Cast")
    cast_list = movie_data.get("credits", {}).get("cast", [])[:10]
    for cast in cast_list:
        st.write(f"• {cast.get('name')} as {cast.get('character')}")

    # Ratings & Reviews
    st.markdown("### ⭐ Rate & Review")
    rating = st.slider("Rate this movie", 1, 5, 3, key="rate_slider")
    review = st.text_area("Write your review", key="review_area")

    if st.button("Submit Review"):
        st.session_state.ratings[selected_movie] = rating
        st.session_state.reviews[selected_movie] = review
        st.success("Review added!")

    if selected_movie in st.session_state.reviews:
        st.markdown("### 💬 Your Review")
        st.write(f"⭐ **Rating:** {st.session_state.ratings[selected_movie]}")
        st.write(f"📝 **Review:** {st.session_state.reviews[selected_movie]}")

# ================= FAVORITES PAGE =================
if st.session_state.page == "Favorites":
    st.subheader("❤️ Your Favorites")
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.write("• " + fav)
    else:
        st.write("No favorites yet.")

# ================= ABOUT PAGE =================
if st.session_state.page == "About":
    st.write("This app recommends movies using TMDB and OMDB APIs.")
    st.write("Created using Streamlit.")
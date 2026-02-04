import streamlit as st
import pickle
import requests
import random

TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"

st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# ---------------- SESSION STATE ----------------
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# ---------------- RED NETFLIX THEME ----------------
st.markdown("""
<style>
.stApp { 
    background-color:#fff0f0;  /* light red background */
    color:#1f1f1f; 
    font-family: 'Arial', sans-serif; 
    font-size:16px; 
}

/* Card styling for movies */
.movie-card {
    background:#ffdddd;  /* pastel red card */
    padding:10px;
    border-radius:15px;
    margin-bottom:20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    transition: transform 0.2s, box-shadow 0.2s;
    text-align:center;
}
.movie-card:hover {
    transform: scale(1.05);
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
}
.movie-card img {
    border-radius:10px;
    width:100%;
    height:auto;
}
.movie-card p.title {
    font-weight:bold;
    margin-top:5px;
    font-size:14px;
}

/* Movie details box */
.movie-card .details {
    background-color: rgba(255, 255, 255, 0.85);
    border-radius: 8px;
    padding: 5px 8px;
    margin-top: 5px;
    font-size: 13px;
    line-height: 1.4;
    text-align: left;
}
.movie-card .details strong {
    color:#b30000;
}

/* Headings */
h1,h2,h3,h4,h5,h6 {
    color:#b30000;  /* dark red headings */
}

/* Sidebar */
.css-1d391kg { 
    background-color:#ffdddd !important;  /* red sidebar */
    color:#1f1f1f !important;
}

/* Buttons */
.stButton>button {
    background-color:#e50914;  /* Netflix red */
    color:white;
    border-radius:8px;
    padding:0.5em 1em;
    font-weight:bold;
    transition: background-color 0.2s;
}
.stButton>button:hover {
    background-color:#b00710;  /* darker red on hover */
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- FUNCTIONS ----------------
def recommend(movie, n=5):
    idx = movies[movies['title'] == movie].index[0]
    scores = similarity[idx]
    movies_list = sorted(list(enumerate(scores)), reverse=True, key=lambda x: x[1])[1:n+1]
    return movies_list

def poster(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    ).json()
    return "https://image.tmdb.org/t/p/w500" + data["poster_path"]

def trailer(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    ).json()
    for v in data.get("results", []):
        if v["site"] == "YouTube" and v["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

def trailer_url_to_embed(url):
    """Converts YouTube URL to embeddable video URL for st.video"""
    if "watch?v=" in url:
        return url.replace("watch?v=", "embed/")
    return url

def movie_details(movie_id):
    """Fetch movie details and format neatly for display"""
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    ).json()
    release = data.get("release_date", "N/A")
    rating = data.get("vote_average", "N/A")
    overview = data.get("overview", "No overview available")
    if len(overview) > 200:
        overview = overview[:200] + "..."
    details = f"""
    <div class="details">
        <strong>Release:</strong> {release}<br>
        <strong>Rating:</strong> {rating}<br>
        <strong>Overview:</strong> {overview}
    </div>
    """
    return details

# ---------------- DISPLAY MOVIES IN ROWS OF 4 ----------------
def display_movies_in_rows(movies_list, key_prefix=""):
    row_size = 4
    for i in range(0, len(movies_list), row_size):
        cols = st.columns(min(row_size, len(movies_list)-i))
        for j, movie in enumerate(movies_list[i:i+row_size]):
            # Convert dict to Series if needed
            if isinstance(movie, dict):
                movie = st.session_state.df_from_dict.get(movie['title'], movie)
            st.markdown(
                f'<div class="movie-card">'
                f'<img src="{poster(movie.movie_id)}">'
                f'<p class="title">{movie.title}</p>'
                f'{movie_details(movie.movie_id)}'
                f'</div>', unsafe_allow_html=True)
            t = trailer(movie.movie_id)
            if t:
                if st.button("Watch Trailer", key=f"{key_prefix}_trailer_{i+j}"):
                    st.video(trailer_url_to_embed(t), format="youtube")
            if st.button("Add to Watchlist", key=f"{key_prefix}_watchlist_{i+j}"):
                if movie.title not in st.session_state.watchlist:
                    st.session_state.watchlist.append(movie.title)
                    st.success(f"{movie.title} added to watchlist")

# ---------------- SIDEBAR ----------------
page = st.sidebar.radio(
    "Navigation",
    ["Home", "Recommended", "Surprise Me", "Recommend by Mood", "Theme", "Watchlist"]
)

# ---------------- HOME ----------------
if page == "Home":
    st.title("Movie Recommendation System")
    st.write("""
    Welcome to the **Movie Recommendation System**! 🎬

    - Discover movies based on your **favorite titles**, **mood**, or **surprise picks**.
    - Watch trailers **directly inside the app** when you click the **Watch Trailer** button.
    - Add movies to your **personal watchlist** and keep track of what you want to watch.
    - The system uses **machine learning** to recommend similar movies tailored to your taste.
    """)

# ---------------- RECOMMENDED ----------------
elif page == "Recommended":
    st.title("Recommended Movies")
    selected_movie = st.selectbox("Select a movie", movies["title"].values)
    n_recommend = st.number_input("Number of movies to recommend", min_value=1, max_value=20, value=5, step=1)

    if selected_movie:
        movie_row = movies[movies["title"] == selected_movie].iloc[0]
        col1, col2 = st.columns([1,2])
        with col1:
            st.markdown(
                f'<div class="movie-card">'
                f'<img src="{poster(movie_row.movie_id)}">'
                f'<p class="title">{selected_movie}</p>'
                f'{movie_details(movie_row.movie_id)}'
                f'</div>', unsafe_allow_html=True)
            if st.button("Add to Watchlist"):
                if selected_movie not in st.session_state.watchlist:
                    st.session_state.watchlist.append(selected_movie)
                    st.success("Added to watchlist")
        with col2:
            t = trailer(movie_row.movie_id)
            if t:
                if st.button(f"Watch Trailer: {selected_movie}", key="trailer_main"):
                    st.video(trailer_url_to_embed(t), format="youtube")

        st.subheader("Similar Movies")
        recs = recommend(selected_movie, n=int(n_recommend))
        display_movies_in_rows(recs, key_prefix="recommended")

# ---------------- SURPRISE ME ----------------
elif page == "Surprise Me":
    st.title("Surprise Me")
    movie = movies.sample(1).iloc[0]
    display_movies_in_rows([movie], key_prefix="surprise")

# ---------------- MOOD ----------------
elif page == "Recommend by Mood":
    st.title("Mood Based Recommendation")
    mood_map = {
        "Happy": ["comedy"],
        "Sad": ["drama"],
        "Excited": ["action", "thriller"],
        "Relaxed": ["family"],
        "Romantic": ["romance"]
    }
    mood = st.selectbox("Select Mood", mood_map.keys())
    keywords = mood_map[mood]
    filtered = movies[movies["tags"].str.contains("|".join(keywords), case=False, na=False)]
    sample = filtered.sample(min(8, len(filtered)))
    display_movies_in_rows(sample.to_dict('records'), key_prefix="mood")

# ---------------- THEME ----------------
elif page == "Theme":
    st.title("Theme Based Recommendations")
    theme_map = {
        "Action": ["action", "adventure", "thriller"],
        "Romance": ["romance", "drama", "comedy"],
        "Comedy": ["comedy", "family"],
        "Horror": ["horror", "thriller", "mystery"],
    }
    theme = st.selectbox("Select Theme", theme_map.keys())
    keywords = theme_map[theme]
    filtered = movies[movies["tags"].str.contains("|".join(keywords), case=False, na=False)]
    sample = filtered.sample(min(8, len(filtered)))
    display_movies_in_rows(sample.to_dict('records'), key_prefix="theme")

# ---------------- WATCHLIST ----------------
elif page == "Watchlist":
    st.title("My Watchlist")
    if not st.session_state.watchlist:
        st.info("Watchlist is empty")
    else:
        watchlist_movies = [movies[movies["title"] == t].iloc[0] for t in st.session_state.watchlist]
        display_movies_in_rows(watchlist_movies, key_prefix="watchlist")
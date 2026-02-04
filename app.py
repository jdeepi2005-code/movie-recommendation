import streamlit as st
import pickle
import requests
import random

TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"

st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# ---------------- SESSION STATE ----------------
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# ---------------- PURPLE NETFLIX THEME ----------------
st.markdown("""
<style>
.stApp { 
    background-color:#f3f0f8;  /* light purple background */
    color:#1f1f1f; 
    font-family: 'Arial', sans-serif; 
    font-size:16px; 
}

/* Card styling for movies */
.movie-card {
    background:#d9c9f0;  /* light purple card */
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
.movie-card p {
    font-weight:bold;
    margin-top:5px;
    font-size:14px;
}

/* Headings */
h1,h2,h3,h4,h5,h6 {
    color:#4b0082;  /* dark purple headings */
}

/* Sidebar */
.css-1d391kg { 
    background-color:#d9c9f0 !important;  /* purple sidebar */
    color:#1f1f1f !important;
}

/* Buttons */
.stButton>button {
    background-color:#7b2cbf;  /* purple buttons */
    color:white;
    border-radius:8px;
    padding:0.5em 1em;
    font-weight:bold;
    transition: background-color 0.2s;
}
.stButton>button:hover {
    background-color:#5c1a8c;  /* darker purple on hover */
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

    if selected_movie:
        movie_row = movies[movies["title"] == selected_movie].iloc[0]

        col1, col2 = st.columns([1,2])

        with col1:
            st.markdown(f'<div class="movie-card"><img src="{poster(movie_row.movie_id)}"><p>{selected_movie}</p></div>', unsafe_allow_html=True)

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
        recs = recommend(selected_movie)
        cols = st.columns(len(recs))
        for i, rec in enumerate(recs):
            m = movies.iloc[rec[0]]
            with cols[i]:
                st.markdown(f'<div class="movie-card"><img src="{poster(m.movie_id)}"><p>{m.title}</p></div>', unsafe_allow_html=True)

                # Trailer inside app with button
                t = trailer(m.movie_id)
                if t:
                    if st.button("Watch Trailer", key=f"trailer_rec_{i}"):
                        st.video(trailer_url_to_embed(t), format="youtube")

                # Add to watchlist button
                if st.button("Add to Watchlist", key=f"watchlist_rec_{i}"):
                    if m.title not in st.session_state.watchlist:
                        st.session_state.watchlist.append(m.title)
                        st.success(f"{m.title} added to watchlist")

# ---------------- SURPRISE ME ----------------
elif page == "Surprise Me":
    st.title("Surprise Me")

    movie = movies.sample(1).iloc[0]

    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown(f'<div class="movie-card"><img src="{poster(movie.movie_id)}"><p>{movie.title}</p></div>', unsafe_allow_html=True)
    with col2:
        st.subheader(movie.title)
        t = trailer(movie.movie_id)
        if t:
            if st.button("Watch Trailer", key="trailer_surprise"):
                st.video(trailer_url_to_embed(t), format="youtube")

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
    sample = filtered.sample(min(5, len(filtered)))

    cols = st.columns(5)
    for i, (_, m) in enumerate(sample.iterrows()):
        with cols[i]:
            st.markdown(f'<div class="movie-card"><img src="{poster(m.movie_id)}"><p>{m.title}</p></div>', unsafe_allow_html=True)
            t = trailer(m.movie_id)
            if t:
                if st.button("Watch Trailer", key=f"trailer_mood_{i}"):
                    st.video(trailer_url_to_embed(t), format="youtube")

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
    sample = filtered.sample(min(5, len(filtered)))

    cols = st.columns(5)
    for i, (_, m) in enumerate(sample.iterrows()):
        with cols[i]:
            st.markdown(f'<div class="movie-card"><img src="{poster(m.movie_id)}"><p>{m.title}</p></div>', unsafe_allow_html=True)
            
            t = trailer(m.movie_id)
            if t:
                if st.button("Watch Trailer", key=f"theme_trailer_{i}"):
                    st.video(trailer_url_to_embed(t), format="youtube")
            
            if st.button("Add to Watchlist", key=f"theme_watchlist_{i}"):
                if m.title not in st.session_state.watchlist:
                    st.session_state.watchlist.append(m.title)
                    st.success(f"{m.title} added to watchlist")

# ---------------- WATCHLIST ----------------
elif page == "Watchlist":
    st.title("My Watchlist")

    if not st.session_state.watchlist:
        st.info("Watchlist is empty")
    else:
        cols = st.columns(4)
        for i, title in enumerate(st.session_state.watchlist):
            m = movies[movies["title"] == title].iloc[0]
            with cols[i % 4]:
                st.markdown(f'<div class="movie-card"><img src="{poster(m.movie_id)}"><p>{title}</p></div>', unsafe_allow_html=True)
                t = trailer(m.movie_id)
                if t:
                    if st.button("Watch Trailer", key=f"watchlist_trailer_{i}"):
                        st.video(trailer_url_to_embed(t), format="youtube")
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
theme = st.sidebar.radio("🎨 Select Theme", ["Dark", "Light"])

# ================= DYNAMIC CSS =================
if theme == "Dark":
    bg = "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
    card = "#111827"
    sidebar = "#020617"
    text = "white"
    widget_text = "white"
    widget_bg = "#1f2937"
else:
    bg = "linear-gradient(135deg, #fdfbfb, #ebedee)"
    card = "#ffffff"
    sidebar = "#f1f5f9"
    text = "#111827"
    widget_text = "#111827"
    widget_bg = "#ffffff"

st.markdown(f"""
<style>
.stApp {{
    background: {bg};
    color: {text};
}}

.header {{
    background: linear-gradient(90deg, #ff512f, #dd2476);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 30px;
}}

.header h1 {{
    font-size: 40px;
    color: white;
}}

.movie-card {{
    background-color: {card};
    border-radius: 16px;
    padding: 12px;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    transition: transform 0.3s;
}}

.movie-card:hover {{
    transform: scale(1.05);
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

[data-testid="stSidebar"] {{
    background-color: {sidebar};
    color: {widget_text};
}}

[data-testid="stSidebar"] .css-1d391kg, 
[data-testid="stSidebar"] .css-1avcm0n, 
[data-testid="stSidebar"] .css-1j8o68u {{
    color: {widget_text};
}}

.css-1lcbmhc {{
    color: {widget_text};
}}

.css-1v3fvcr {{
    color: {widget_text};
}}

.css-1tbi4j3 {{
    color: {widget_text};
}}

.css-1q8dd3e {{
    color: {widget_text};
}}

.css-1d391kg {{
    color: {widget_text};
}}

.css-1outpf7 {{
    background-color: {widget_bg};
    color: {widget_text};
}}

.css-1y4p8pa {{
    background-color: {widget_bg};
    color: {widget_text};
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

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Settings")
num_recommendations = st.sidebar.slider("Number of recommendations", 3, 10, 5)

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

def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()

    for video in data.get("results", []):
        if video["site"] == "YouTube" and video["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None

def fetch_omdb(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    return requests.get(url).json()

# ================= MOVIE SELECTION =================
st.subheader("🎞️ Select a Movie")
selected_movie = st.selectbox("Choose a movie", movies['title'].values)

st.success(f"🎥 You selected: **{selected_movie}**")

# ================= RECOMMEND =================
if st.button("🚀 Recommend"):
    with st.spinner("Finding similar movies..."):
        recommendations = recommend(selected_movie, num_recommendations)

    st.subheader("🌟 Recommended Movies")

    cols = st.columns(5)
    for idx, rec in enumerate(recommendations):
        movie = movies.iloc[rec[0]]
        poster = fetch_poster(movie.movie_id)
        trailer = fetch_trailer(movie.movie_id)
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

            st.caption(f"🎭 Genre: {omdb.get('Genre', 'N/A')}")
            st.caption(f"📅 Year: {omdb.get('Year', 'N/A')}")

            # ✅ WATCH TRAILER BUTTON
            if trailer:
                st.markdown(
                    f'<a href="{trailer}" target="_blank"><button style="background-color:#ff512f;color:white;border:none;padding:8px 12px;border-radius:8px;cursor:pointer;">🎬 Watch Trailer</button></a>',
                    unsafe_allow_html=True
                )
            else:
                st.caption("🎥 Trailer not available")

            st.markdown('</div>', unsafe_allow_html=True)
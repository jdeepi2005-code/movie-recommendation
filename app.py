import streamlit as st
import pickle
import requests
import random
import streamlit.components.v1 as components

# ================= API KEYS =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Movie Recommendation System", layout="wide")

# ================= SESSION STATE =================
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "page" not in st.session_state:
    st.session_state.page = "Home"

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= FUNCTIONS =================
def recommend(movie, n=5):
    idx = movies[movies["title"] == movie].index[0]
    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:n+1]
    return scores

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    for v in r.json().get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            return f"https://www.youtube.com/embed/{v['key']}"  # Embed URL
    return None

def fetch_omdb(title):
    url = f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}"
    return requests.get(url).json()

# ================= TOP NAV =================
st.markdown("""
<div style="display:flex;justify-content:space-around;background:#4b0082;padding:12px;border-radius:12px;margin-bottom:25px;">
<button onclick="window.streamlitSendMessage('Home')" style="color:white;font-size:18px;font-weight:bold;background:none;border:none;cursor:pointer;">🏠 Home</button>
<button onclick="window.streamlitSendMessage('Recommend')" style="color:white;font-size:18px;font-weight:bold;background:none;border:none;cursor:pointer;">🎯 Recommend</button>
<button onclick="window.streamlitSendMessage('Watchlist')" style="color:white;font-size:18px;font-weight:bold;background:none;border:none;cursor:pointer;">❤️ Watchlist</button>
<button onclick="window.streamlitSendMessage('Surprise')" style="color:white;font-size:18px;font-weight:bold;background:none;border:none;cursor:pointer;">🎲 Surprise Me</button>
</div>
""", unsafe_allow_html=True)

# ================= PAGE SELECTION =================
page = st.session_state.page

# ================= HOME =================
if page == "Home":
    st.markdown("<h1 style='text-align:center;color:white;'>🎬 Movie Recommendation System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:white;'>Discover movies you'll love using AI-powered recommendations!</p>", unsafe_allow_html=True)

# ================= RECOMMEND =================
elif page == "Recommend":
    st.markdown("<h2 style='color:white;'>🎯 Choose a Movie</h2>", unsafe_allow_html=True)
    movie_name = st.selectbox("Select a movie", movies["title"].values)
    num = st.slider("Number of recommendations", 3, 10, 5)

    if st.button("Recommend 🚀"):
        recs = recommend(movie_name, num)
        st.markdown("<div style='display:flex;flex-wrap:wrap;gap:20px;'>", unsafe_allow_html=True)

        for r in recs:
            m = movies.iloc[r[0]]
            poster = fetch_poster(m.movie_id)
            trailer = fetch_trailer(m.movie_id)
            omdb = fetch_omdb(m.title)

            trailer_html = f"""
            <iframe width="100%" height="200" src="{trailer}" frameborder="0" allowfullscreen></iframe>
            """ if trailer else "<p>No trailer available</p>"

            card_html = f"""
            <div style="
                background:white;color:black;width:200px;border-radius:16px;
                box-shadow:0 8px 20px rgba(0,0,0,0.3);text-align:center;padding:10px;
                transition: transform 0.3s;cursor:pointer;
            " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                <img src="{poster}" width="100%" style="border-radius:12px;">
                <h3>{m.title}</h3>
                <p>⭐ IMDb: {omdb.get('imdbRating','N/A')}</p>
                <p>Because you liked <b>{movie_name}</b></p>
                <button onclick="alert('Added to Watchlist!')">❤️ Add to Watchlist</button>
                <details>
                    <summary>▶ Watch Trailer</summary>
                    {trailer_html}
                </details>
            </div>
            """
            components.html(card_html, height=350, scrolling=False)

        st.markdown("</div>", unsafe_allow_html=True)

# ================= WATCHLIST =================
elif page == "Watchlist":
    st.markdown("<h2 style='color:white;'>❤️ Your Watchlist</h2>", unsafe_allow_html=True)
    if not st.session_state.watchlist:
        st.info("No movies added yet")
    else:
        for m in st.session_state.watchlist:
            st.markdown(f"<p style='color:white;font-size:18px;'>🎬 {m}</p>", unsafe_allow_html=True)

# ================= SURPRISE =================
elif page == "Surprise":
    st.markdown("<h2 style='color:white;'>🎲 Surprise Movie</h2>", unsafe_allow_html=True)
    m = movies.sample(1).iloc[0]
    poster = fetch_poster(m.movie_id)
    trailer = fetch_trailer(m.movie_id)

    trailer_html = f"""
    <iframe width="100%" height="300" src="{trailer}" frameborder="0" allowfullscreen></iframe>
    """ if trailer else "<p>No trailer available</p>"

    card_html = f"""
    <div style="
        background:white;color:black;width:300px;border-radius:16px;
        box-shadow:0 8px 20px rgba(0,0,0,0.3);text-align:center;padding:10px;margin:auto;
    ">
        <img src="{poster}" width="100%" style="border-radius:12px;">
        <h3>{m.title}</h3>
        <details>
            <summary>▶ Watch Trailer</summary>
            {trailer_html}
        </details>
    </div>
    """
    components.html(card_html, height=450, scrolling=False)
import streamlit as st
import pickle
import requests
import random

# ================= API KEY =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ================= SESSION STATE =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

# ================= CSS =================
st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: #f1f5f9;
}

.card {
    background-color: #020617;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 20px;
    border: 1px solid #1e293b;
}

h1, h2, h3, p, label {
    color: #f8fafc !important;
}

div[data-baseweb="select"] span {
    color: black !important;
}

input {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
if not st.session_state.logged_in:
    st.title("User Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if "@" in email and "." in email and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.experimental_rerun()
        else:
            st.error("Enter a valid email and password")

    st.stop()

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= FUNCTIONS =================
def recommend(movie, n=5):
    idx = movies[movies['title'] == movie].index[0]
    distances = similarity[idx]
    return sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:n+1]

def fetch_poster(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    ).json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_trailer(movie_id):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    ).json()

    for v in data.get("results", []):
        if v["site"] == "YouTube" and v["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

# ================= SIDEBAR =================
st.sidebar.title("Movie App")
st.sidebar.write(st.session_state.user_email)

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Recommended", "Surprise Me", "Recommend by Mood", "Watchlist"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.watchlist = []
    st.experimental_rerun()

# ================= HOME =================
if page == "Home":
    st.title("Movie Recommendation System")
    st.subheader("Personalized movie discovery using machine learning")

    st.markdown("""
    <div class="card">
    <ul>
        <li>Content-based movie recommendations</li>
        <li>In-app trailer playback</li>
        <li>Mood-based movie suggestions</li>
        <li>User watchlist</li>
        <li>Email-based login</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ================= RECOMMENDED =================
elif page == "Recommended":
    st.title("Recommended Movies")

    selected_movie = st.selectbox(
        "Choose a movie",
        movies['title'].values
    )

    if st.button("Recommend"):
        results = recommend(selected_movie)
        cols = st.columns(5)

        for i, r in enumerate(results):
            m = movies.iloc[r[0]]

            with cols[i]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                poster = fetch_poster(m.movie_id)
                trailer = fetch_trailer(m.movie_id)

                if poster:
                    st.image(poster, use_container_width=True)

                st.write(m.title)

                if m.title not in st.session_state.watchlist:
                    if st.button("Add to Watchlist", key=f"add_{m.movie_id}"):
                        st.session_state.watchlist.append(m.title)
                        st.success("Added")

                if trailer:
                    st.video(trailer)

                st.markdown("</div>", unsafe_allow_html=True)

# ================= SURPRISE ME =================
elif page == "Surprise Me":
    st.title("Random Movie")

    if st.button("Generate"):
        m = movies.sample(1).iloc[0]

        poster = fetch_poster(m.movie_id)
        trailer = fetch_trailer(m.movie_id)

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        if poster:
            st.image(poster, width=300)

        st.write(m.title)

        if trailer:
            st.video(trailer)

        st.markdown("</div>", unsafe_allow_html=True)

# ================= MOOD =================
elif page == "Recommend by Mood":
    st.title("Mood Based Recommendation")

    mood_map = {
        "Happy": ["comedy"],
        "Sad": ["drama"],
        "Excited": ["action", "thriller"],
        "Relaxed": ["family", "animation"],
        "Romantic": ["romance"]
    }

    mood = st.selectbox("Select mood", mood_map.keys())

    if st.button("Show Movies"):
        keys = mood_map[mood]
        filtered = movies[
            movies['tags'].str.contains("|".join(keys), case=False, na=False)
        ]

        cols = st.columns(5)
        for i, (_, m) in enumerate(filtered.sample(min(5, len(filtered))).iterrows()):
            with cols[i]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                poster = fetch_poster(m.movie_id)
                trailer = fetch_trailer(m.movie_id)

                if poster:
                    st.image(poster, use_container_width=True)

                st.write(m.title)

                if trailer:
                    st.video(trailer)

                st.markdown("</div>", unsafe_allow_html=True)

# ================= WATCHLIST =================
elif page == "Watchlist":
    st.title("My Watchlist")

    if not st.session_state.watchlist:
        st.info("Watchlist is empty")
    else:
        cols = st.columns(4)
        for i, title in enumerate(st.session_state.watchlist):
            m = movies[movies['title'] == title].iloc[0]

            with cols[i % 4]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                poster = fetch_poster(m.movie_id)
                trailer = fetch_trailer(m.movie_id)

                if poster:
                    st.image(poster, use_container_width=True)

                st.write(title)

                if st.button("Remove", key=f"rm_{m.movie_id}"):
                    st.session_state.watchlist.remove(title)
                    st.experimental_rerun()

                if trailer:
                    st.video(trailer)

                st.markdown("</div>", unsafe_allow_html=True)
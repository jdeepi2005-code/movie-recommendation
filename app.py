import streamlit as st
import pickle
import requests
import random

# ================= CONFIG =================
TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ================= SESSION =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "watchlist" not in st.session_state:
    st.session_state.watchlist = []
if "popup_movie" not in st.session_state:
    st.session_state.popup_movie = None

# ================= CSS =================
st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: #f8fafc;
}

/* Sidebar text fix */
section[data-testid="stSidebar"] * {
    color: #0f172a !important;
}

/* Cards */
.card {
    background-color: #020617;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 20px;
}

h1, h2, h3, p {
    color: #f8fafc !important;
}

input, select {
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
            st.session_state.email = email
            st.rerun()
        else:
            st.error("Enter a valid email and password")

    st.stop()

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= FUNCTIONS =================
def recommend(movie, n=5):
    idx = movies[movies["title"] == movie].index[0]
    scores = similarity[idx]
    return sorted(
        list(enumerate(scores)),
        key=lambda x: x[1],
        reverse=True
    )[1:n+1]

def fetch_poster(mid):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{mid}?api_key={TMDB_API_KEY}"
    ).json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_trailer(mid):
    data = requests.get(
        f"https://api.themoviedb.org/3/movie/{mid}/videos?api_key={TMDB_API_KEY}"
    ).json()
    for v in data.get("results", []):
        if v["site"] == "YouTube" and v["type"] == "Trailer":
            return f"https://www.youtube.com/watch?v={v['key']}"
    return None

# ================= SIDEBAR =================
st.sidebar.title("Movie App")
st.sidebar.write(st.session_state.email)

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Recommended", "Surprise Me", "Recommend by Mood", "Watchlist"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.watchlist.clear()
    st.rerun()

# ================= WATCHLIST POPUP =================
if st.session_state.popup_movie:
    with st.dialog("Add to Watchlist"):
        st.write(f"Add **{st.session_state.popup_movie}** to your watchlist?")
        if st.button("Confirm"):
            st.session_state.watchlist.append(st.session_state.popup_movie)
            st.session_state.popup_movie = None
            st.toast("Added to watchlist")
            st.rerun()
        if st.button("Cancel"):
            st.session_state.popup_movie = None
            st.rerun()

# ================= HOME =================
if page == "Home":
    st.title("Movie Recommendation System")
    st.subheader("Personalized movie discovery using machine learning")

    st.markdown("""
    <div class="card">
    <ul>
        <li>Content-based recommendations</li>
        <li>Inline trailer playback</li>
        <li>Mood-based discovery</li>
        <li>User watchlist with popup</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ================= RECOMMENDED =================
elif page == "Recommended":
    st.title("Recommended Movies")

    movie = st.selectbox("Choose a movie", movies["title"].values)

    if st.button("Recommend"):
        cols = st.columns(5)
        for i, rec in enumerate(recommend(movie)):
            m = movies.iloc[rec[0]]
            with cols[i]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                poster = fetch_poster(m.movie_id)
                trailer = fetch_trailer(m.movie_id)

                if poster:
                    st.image(poster, use_container_width=True)
                st.write(m.title)

                if st.button("Add to Watchlist", key=f"wl_{m.movie_id}"):
                    st.session_state.popup_movie = m.title
                    st.rerun()

                if trailer:
                    st.video(trailer)

                st.markdown("</div>", unsafe_allow_html=True)

# ================= SURPRISE =================
elif page == "Surprise Me":
    st.title("Random Movie")

    if st.button("Generate"):
        m = movies.sample(1).iloc[0]
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        poster = fetch_poster(m.movie_id)
        trailer = fetch_trailer(m.movie_id)

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
        subset = movies[
            movies["tags"].str.contains(
                "|".join(mood_map[mood]), case=False, na=False
            )
        ]
        cols = st.columns(5)
        for i, (_, m) in enumerate(subset.sample(min(5, len(subset))).iterrows()):
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
            m = movies[movies["title"] == title].iloc[0]
            with cols[i % 4]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                poster = fetch_poster(m.movie_id)
                trailer = fetch_trailer(m.movie_id)

                if poster:
                    st.image(poster, use_container_width=True)
                st.write(title)

                if st.button("Remove", key=f"rm_{m.movie_id}"):
                    st.session_state.watchlist.remove(title)
                    st.rerun()

                if trailer:
                    st.video(trailer)

                st.markdown("</div>", unsafe_allow_html=True)
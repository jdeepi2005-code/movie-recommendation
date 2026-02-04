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

# ================= SESSION STATE =================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

if "open_trailer" not in st.session_state:
    st.session_state.open_trailer = None

# ================= CSS =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f172a,#1e293b);
    color: #f8fafc;
    font-family: "Segoe UI", sans-serif;
}
.card {
    background: #020617;
    padding: 14px;
    border-radius: 10px;
    margin-bottom: 16px;
    border: 1px solid #334155;
}
h1,h2,h3,h4 {
    color: #e5e7eb;
}
button {
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ================= LOGIN =================
if not st.session_state.logged_in:
    st.title("User Login")

    email = st.text_input("Email ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if "@" in email and "." in email and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()
        else:
            st.error("Enter valid email and password")

    st.stop()

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= FUNCTIONS =================
def recommend(movie, n=5):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    return sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:n+1]

def fetch_poster(movie_id):
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    )
    if r.status_code == 200:
        data = r.json()
        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_trailer(movie_id):
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    )
    if r.status_code == 200:
        for v in r.json().get("results", []):
            if v["type"] == "Trailer" and v["site"] == "YouTube":
                return v["key"]
    return None

# ================= SIDEBAR =================
st.sidebar.title("Navigation")
st.sidebar.write(f"Logged in as: {st.session_state.user_email}")

page = st.sidebar.radio(
    "Pages",
    ["Home", "Recommended", "Surprise Me", "Recommend by Mood", "Watchlist"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.watchlist = []
    st.session_state.open_trailer = None
    st.rerun()

# ================= HOME =================
if page == "Home":
    st.title("Movie Recommendation System")
    st.subheader("Personalized movie discovery using machine learning")

    st.markdown("""
    <div class="card">
    <ul>
        <li>Content-based recommendation engine</li>
        <li>In-app YouTube trailer playback</li>
        <li>Mood-based discovery</li>
        <li>Personal watchlist</li>
        <li>Email-based login</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# ================= RECOMMENDED =================
elif page == "Recommended":
    st.title("Recommended Movies")

    selected_movie = st.selectbox("Select a movie", movies['title'].values)

    if st.button("Generate Recommendations"):
        recs = recommend(selected_movie)
        cols = st.columns(5)

        for i, rec in enumerate(recs):
            movie = movies.iloc[rec[0]]
            poster = fetch_poster(movie.movie_id)
            trailer = fetch_trailer(movie.movie_id)

            with cols[i]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(movie.title)

                if st.button("Add to Watchlist", key=f"add_{movie.movie_id}"):
                    if movie.title not in st.session_state.watchlist:
                        st.session_state.watchlist.append(movie.title)
                        st.success("Added to Watchlist")

                if trailer:
                    if st.button("Watch Trailer", key=f"trailer_{movie.movie_id}"):
                        st.session_state.open_trailer = trailer

                if st.session_state.open_trailer == trailer:
                    st.markdown(
                        f"""
                        <iframe width="100%" height="230"
                        src="https://www.youtube.com/embed/{trailer}?autoplay=1"
                        frameborder="0"
                        allow="autoplay; encrypted-media"
                        allowfullscreen>
                        </iframe>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)

# ================= SURPRISE ME =================
elif page == "Surprise Me":
    st.title("Random Movie Suggestion")

    if st.button("Generate"):
        movie = movies.sample(1).iloc[0]
        poster = fetch_poster(movie.movie_id)
        trailer = fetch_trailer(movie.movie_id)

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        if poster:
            st.image(poster, width=300)

        st.markdown(movie.title)

        if trailer:
            if st.button("Watch Trailer"):
                st.session_state.open_trailer = trailer

        if st.session_state.open_trailer == trailer:
            st.markdown(
                f"""
                <iframe width="100%" height="300"
                src="https://www.youtube.com/embed/{trailer}?autoplay=1"
                frameborder="0"
                allowfullscreen>
                </iframe>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

# ================= MOOD =================
elif page == "Recommend by Mood":
    st.title("Mood-Based Recommendation")

    mood_map = {
        "Happy": ["comedy"],
        "Sad": ["drama"],
        "Excited": ["action", "thriller"],
        "Relaxed": ["family", "animation"],
        "Romantic": ["romance"]
    }

    mood = st.selectbox("Select mood", list(mood_map.keys()))

    if st.button("Recommend"):
        keywords = mood_map[mood]
        mood_movies = movies[movies['tags'].str.contains("|".join(keywords), case=False, na=False)]

        cols = st.columns(5)
        for i, (_, movie) in enumerate(mood_movies.sample(min(5, len(mood_movies))).iterrows()):
            poster = fetch_poster(movie.movie_id)
            trailer = fetch_trailer(movie.movie_id)

            with cols[i]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(movie.title)

                if trailer:
                    if st.button("Watch Trailer", key=f"mood_{movie.movie_id}"):
                        st.session_state.open_trailer = trailer

                if st.session_state.open_trailer == trailer:
                    st.markdown(
                        f"""
                        <iframe width="100%" height="230"
                        src="https://www.youtube.com/embed/{trailer}?autoplay=1"
                        frameborder="0"
                        allowfullscreen>
                        </iframe>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)

# ================= WATCHLIST =================
elif page == "Watchlist":
    st.title("My Watchlist")

    if not st.session_state.watchlist:
        st.info("Watchlist is empty")
    else:
        cols = st.columns(4)
        for i, title in enumerate(st.session_state.watchlist):
            movie = movies[movies['title'] == title].iloc[0]
            poster = fetch_poster(movie.movie_id)

            with cols[i % 4]:
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                if poster:
                    st.image(poster, use_container_width=True)

                st.markdown(title)

                if st.button("Remove", key=f"remove_{movie.movie_id}"):
                    st.session_state.watchlist.remove(title)
                    st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
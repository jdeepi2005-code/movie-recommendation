import streamlit as st
import pickle
import requests
import random

TMDB_API_KEY = "c8ce383e8670e6d52aaa745448b33712"
OMDB_API_KEY = "8bd965b9"

st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "watchlist" not in st.session_state:
    st.session_state.watchlist = []

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#141e30,#243b55);
    color: white;
}
.card {
    background: #111827;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    margin-bottom: 15px;
}
h1, h2, h3 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    st.markdown("<h1>User Login</h1>", unsafe_allow_html=True)

    email = st.text_input("Email ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if "@" in email and "." in email and password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.experimental_rerun()
        else:
            st.error("Please enter a valid email ID and password")

    st.stop()

movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

def recommend(movie, n=5):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    return sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:n+1]

def fetch_poster(movie_id):
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    )
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("poster_path"):
        return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    return None

def fetch_trailer(movie_id):
    r = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
    )
    if r.status_code != 200:
        return None
    for v in r.json().get("results", []):
        if v["type"] == "Trailer" and v["site"] == "YouTube":
            return v["key"]
    return None

st.sidebar.title("Movie App")
st.sidebar.write(f"Logged in as: {st.session_state.user_email}")

page = st.sidebar.radio(
    "Navigation",
    ["Home", "Recommended", "Surprise Me", "Recommend by Mood", "Watchlist"]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.watchlist = []
    st.experimental_rerun()

if page == "Home":
    st.markdown("<h1>Movie Recommendation System</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Personalized movie discovery using machine learning</h3>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <ul>
        <li>Content-based movie recommendation</li>
        <li>In-app trailer viewing</li>
        <li>Mood-based discovery</li>
        <li>Personal watchlist</li>
        <li>Email-based login system</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

elif page == "Recommended":
    st.markdown("<h2>Recommended Movies</h2>", unsafe_allow_html=True)

    selected_movie = st.selectbox("Select a movie", movies['title'].values)

    if st.button("Generate Recommendations"):
        recommendations = recommend(selected_movie)
        cols = st.columns(5)

        for i, rec in enumerate(recommendations):
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

                if trailer:
                    if st.button("Watch Trailer", key=f"trailer_{movie.movie_id}"):
                        st.markdown(
                            f"""
                            <iframe width="100%" height="215"
                            src="https://www.youtube.com/embed/{trailer}"
                            frameborder="0" allowfullscreen>
                            </iframe>
                            """,
                            unsafe_allow_html=True
                        )
                st.markdown("</div>", unsafe_allow_html=True)

elif page == "Surprise Me":
    st.markdown("<h2>Random Movie Suggestion</h2>", unsafe_allow_html=True)

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
                st.markdown(
                    f"""
                    <iframe width="100%" height="315"
                    src="https://www.youtube.com/embed/{trailer}"
                    frameborder="0" allowfullscreen>
                    </iframe>
                    """,
                    unsafe_allow_html=True
                )
        st.markdown("</div>", unsafe_allow_html=True)

elif page == "Recommend by Mood":
    st.markdown("<h2>Mood-Based Recommendation</h2>", unsafe_allow_html=True)

    mood_map = {
        "Happy": ["comedy"],
        "Sad": ["drama"],
        "Excited": ["action", "thriller"],
        "Relaxed": ["family", "animation"],
        "Romantic": ["romance"]
    }

    mood = st.selectbox("Select your mood", list(mood_map.keys()))

    if st.button("Recommend"):
        keywords = mood_map[mood]
        mood_movies = movies[
            movies['tags'].str.contains("|".join(keywords), case=False, na=False)
        ]

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
                        st.markdown(
                            f"""
                            <iframe width="100%" height="215"
                            src="https://www.youtube.com/embed/{trailer}"
                            frameborder="0" allowfullscreen>
                            </iframe>
                            """,
                            unsafe_allow_html=True
                        )
                st.markdown("</div>", unsafe_allow_html=True)

elif page == "Watchlist":
    st.markdown("<h2>My Watchlist</h2>", unsafe_allow_html=True)

    if not st.session_state.watchlist:
        st.info("Your watchlist is empty")
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
                    st.experimental_rerun()

                st.markdown("</div>", unsafe_allow_html=True)
import streamlit as st
import pickle
import pandas as pd

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ================= STRONG UI (GUARANTEED VISIBLE) =================
st.markdown("""
<style>
.stApp {
    background-color: #0f172a;
}

.header-box {
    background: linear-gradient(90deg, #ff512f, #dd2476);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 25px;
}

.header-box h1 {
    color: white;
    font-size: 42px;
}

.header-box p {
    color: white;
    font-size: 18px;
}

.movie-card {
    background-color: #111827;
    border: 2px solid #374151;
    border-radius: 14px;
    padding: 18px;
    text-align: center;
    margin-bottom: 20px;
}

.movie-title {
    font-size: 18px;
    font-weight: bold;
    color: #f9fafb;
}

.score {
    background-color: #facc15;
    color: black;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: bold;
    margin-top: 10px;
    display: inline-block;
}

[data-testid="stSidebar"] {
    background-color: #020617;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="header-box">
    <h1>🎬 Movie Recommendation System</h1>
    <p>Find movies similar to your favorite one</p>
</div>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Settings")
num_recommendations = st.sidebar.slider("🎯 Number of recommendations", 3, 10, 5)

# ================= RECOMMEND FUNCTION =================
def recommend(movie, n):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:n+1]

    return movie_list

# ================= INPUT =================
st.subheader("🔍 Search Movie")
movie_input = st.text_input("Type a movie name")

st.subheader("🎞️ Or select from the list")
selected_movie = st.selectbox("Movie list", movies['title'].values)

final_movie = movie_input if movie_input in movies['title'].values else selected_movie
st.success(f"🎥 You selected: **{final_movie}**")

# ================= RECOMMEND =================
if st.button("🚀 Recommend Movies"):
    with st.spinner("Finding similar movies..."):
        recommendations = recommend(final_movie, num_recommendations)

    st.markdown("## 🌟 Recommended Movies")

    cols = st.columns(4)
    for idx, rec in enumerate(recommendations):
        with cols[idx % 4]:
            st.markdown('<div class="movie-card">', unsafe_allow_html=True)

            st.markdown(
                f'<div class="movie-title">🎬 {movies.iloc[rec[0]].title}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="score">⭐ Similarity: {round(rec[1], 2)}</div>',
                unsafe_allow_html=True
            )

            st.markdown('</div>', unsafe_allow_html=True)
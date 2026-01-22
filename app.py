import streamlit as st
import pickle
import pandas as pd

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# ================= CUSTOM UI =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #141e30, #243b55);
    color: white;
}

.movie-card {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 18px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0px 8px 25px rgba(0,0,0,0.5);
    transition: all 0.3s ease;
}

.movie-card:hover {
    transform: translateY(-8px) scale(1.04);
}

.similarity {
    background: linear-gradient(135deg, #f7971e, #ffd200);
    color: black;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 600;
    display: inline-block;
    margin-top: 10px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2027, #203a43);
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.markdown("## 🎬 Movie Recommendation System")
st.caption("Find movies similar to your favorite one using Machine Learning")

# ================= LOAD DATA =================
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# ================= SIDEBAR =================
st.sidebar.header("⚙️ Settings")
num_recommendations = st.sidebar.slider(
    "🎯 Number of recommendations",
    min_value=3,
    max_value=10,
    value=5
)

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
selected_movie = st.selectbox(
    "Movie list",
    movies['title'].values
)

final_movie = movie_input if movie_input in movies['title'].values else selected_movie
st.success(f"🎥 You selected: **{final_movie}**")

# ================= RECOMMEND =================
if st.button("🚀 Recommend"):
    try:
        with st.spinner("Finding similar movies..."):
            recommendations = recommend(final_movie, num_recommendations)

        st.subheader("📌 Recommended Movies")

        cols = st.columns(5)
        for idx, rec in enumerate(recommendations):
            with cols[idx % 5]:
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)

                st.markdown(f"**🎬 {movies.iloc[rec[0]].title}**")

                st.markdown(
                    f'<div class="similarity">⭐ Similarity Score: {round(rec[1], 2)}</div>',
                    unsafe_allow_html=True
                )

                st.markdown('</div>', unsafe_allow_html=True)

    except Exception:
        st.error("❌ Recommendation failed. Please try another movie.")
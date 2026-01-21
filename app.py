import streamlit as st
import pickle
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Movie Recommendation System",
    layout="wide"
)

# Title
st.title("🎬 Movie Recommendation System")
st.write("Find movies similar to your favorite one")

# Load data
movies = pickle.load(open("movie_list.pkl", "rb"))
similarity = pickle.load(open("similarity.pkl", "rb"))

# Sidebar controls
st.sidebar.header("⚙️ Settings")
num_recommendations = st.sidebar.slider(
    "Number of recommendations",
    min_value=3,
    max_value=10,
    value=5
)

# Recommendation function (same logic, extended)
def recommend(movie, n):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]

    movie_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:n+1]

    return movie_list

# Search input
st.subheader("🔍 Search Movie")
movie_input = st.text_input("Type a movie name")

# Dropdown fallback
st.subheader("🎞️ Or select from the list")
selected_movie = st.selectbox(
    "Movie list",
    movies['title'].values
)

# Decide final movie
final_movie = movie_input if movie_input in movies['title'].values else selected_movie

st.success(f"You selected: **{final_movie}**")

# Recommend button
if st.button("Recommend 🎯"):
    try:
        with st.spinner("Finding similar movies..."):
            recommendations = recommend(final_movie, num_recommendations)

        st.subheader("📌 Recommended Movies")

        cols = st.columns(5)
        for idx, rec in enumerate(recommendations):
            with cols[idx % 5]:
                st.markdown(
                    f"""
                    🎬 **{movies.iloc[rec[0]].title}**  
                    ⭐ Similarity: `{round(rec[1], 2)}`
                    """
                )

    except Exception as e:
        st.error("❌ Recommendation failed. Please try another movie.")

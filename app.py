# File: app.py

from search_engine import MovieSearchEngine
import streamlit as st
import time
import math

# Setup
st.set_page_config(page_title="🎬 Movie Search Engine", layout="wide")
search_engine = MovieSearchEngine()

# Prepare filters
unique_genres = sorted(set(g.strip() for genre in search_engine.df['Genre'].dropna() for g in genre.split(',')))
years = sorted(search_engine.df['Release Year'].dropna().astype(int).unique())

# Custom CSS
st.markdown("""
    <style>
    .result-card {
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #ffffff;
        border-left: 5px solid #4f8bf9;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-radius: 0.5rem;
    }
    .movie-title {
        font-size: 20px;
        font-weight: bold;
        color: #333333;
    }
    .movie-plot {
        font-size: 16px;
        color: #555555;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🔍 Search Settings")
query = st.sidebar.text_input("Enter search query")
mode = st.sidebar.radio("Search Mode", ['AND', 'OR', 'NOT', 'PHRASE', 'BIWORD'])
selected_genres = st.sidebar.multiselect("Filter by Genre", unique_genres)
selected_years = st.sidebar.multiselect("Filter by Year", years)
results_per_page = st.sidebar.slider("Results per Page", 5, 20, 10)

# Title
st.title("🎥 Advanced Movie Search")
st.markdown("Search through thousands of movie plots using full-text search with filters.")

if st.sidebar.button("Search"):
    with st.spinner("Searching..."):
        time.sleep(0.5)

        # Get initial results
        if mode == 'PHRASE':
            results = search_engine.phrase_search(query)
        elif mode == 'BIWORD':
            results = search_engine.biword_search(query)
        else:
            results = search_engine.boolean_search(query, mode)

        # Apply filters
        if selected_genres or selected_years:
            filtered = []
            for idx in results:
                row = search_engine.df.iloc[idx]
                match_genre = any(g.strip() in row['Genre'] for g in selected_genres) if selected_genres else True
                match_year = row['Release Year'] in selected_years if selected_years else True
                if match_genre and match_year:
                    filtered.append(idx)
            results = filtered

        st.success(f"Found {len(results)} result(s)")

        # Pagination setup
        total_pages = math.ceil(len(results) / results_per_page)
        if total_pages > 1:
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
        else:
            page = 1

        start = (page - 1) * results_per_page
        end = start + results_per_page

        # Display results
        for idx in results[start:end]:
            movie = search_engine.get_movie_details(idx)
            short_plot = movie['original_plot'][:300] + ("..." if len(movie['original_plot']) > 300 else "")
            with st.container():
                st.markdown(f"""
                    <div class='result-card'>
                        <div class='movie-title'>{movie["title"]}</div>
                        <div class='movie-plot'>{short_plot}</div>
                    </div>
                """, unsafe_allow_html=True)
                with st.expander("Full Plot"):
                    st.write(movie['original_plot'])

        if not results:
            st.warning("No matching results.")

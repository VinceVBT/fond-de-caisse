import streamlit as st

st.set_page_config(
    page_title="Miss Madeleine",
    layout="centered",
)

pg = st.navigation([
    st.Page("pages/home.py", title="Accueil", default=True),
    st.Page("pages/caisse.py", title="Caisse"),
    st.Page("pages/stocks.py", title="Stocks"),
])
pg.run()

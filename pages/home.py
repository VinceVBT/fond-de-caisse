import streamlit as st


st.title("Accueil")

col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown("### 💰 Fond de Caisse")
        st.page_link("pages/caisse.py", label="Ouvrir")
with col2:
    with st.container(border=True):
        st.markdown("### 📊 Stocks & TGTG")
        st.page_link("pages/stocks.py", label="Ouvrir")

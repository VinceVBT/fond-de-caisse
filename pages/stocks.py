import streamlit as st
from src.utils import select_infos


st.title("📊 Stocks et TGTG")
st.caption("Saisie des stocks et ToGoodToGo")

caissier, boutique, selected_date = select_infos()
st.divider()

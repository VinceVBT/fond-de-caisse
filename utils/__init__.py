import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo


CAISSIERS = ["Vincent", "Valérie", "Pamela", "Sylvain", "dev"]
BOUTIQUES_FUND = {
    "Cordeliers": 106.70,
    "Foch": 100,
}
DATE_FMT = "%d/%m/%Y"
DATETIME_FMT = "%d/%m/%Y %H:%M:%S"


def select_infos():
    st.subheader("📋 Informations")
    col1, col2, col3 = st.columns(3)
    with col1:
        caissier = st.selectbox(
            "Nom du caissier :",
            options=[None] + CAISSIERS,
            format_func=lambda x: "Sélectionner une option..." if x is None else x,
        )
    with col2:
        boutique = st.selectbox("Nom de la boutique :", BOUTIQUES_FUND.keys())
    with col3:
        selected_date = st.date_input("Date :", value=datetime.now(ZoneInfo("Europe/Paris")))
    return caissier, boutique, selected_date


def reset_session_states(ss_keys: list):
    for ss_key in ss_keys:
        if ss_key in st.session_state.keys():
            st.session_state[ss_key] = 0

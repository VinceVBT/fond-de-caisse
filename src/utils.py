from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection


CAISSIERS = ["Vincent", "Valérie", "Pamela", "Sylvain"]
BOUTIQUES_FUND = {
    "Cordeliers": 106.70,
    "Foch": 100,
}
BILLS_LIST = [500, 200, 100, 50, 20, 10, 5]
COINS_ROLLS = {
    2: 50,
    1: 25,
    0.5: 20,
    0.2: 8,
    0.1: 4,
    0.05: 2.5,
    0.02: 1,
    0.01: 0.5,
}
CONN_SHEETS = st.connection("gsheets", type=GSheetsConnection)


def fmt_coin(value):
    return ".2f" if value < 1 else ""


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
        selected_date = st.date_input("Date :", value=datetime.now(ZoneInfo("CET")))
    return caissier, boutique, selected_date


def reset_inputs_caisse(inputs: list):
    for k in inputs:
        if k in st.session_state.keys():
            st.session_state[k] = 0


def save_counting(
        caissier: str,
        boutique: str,
        selected_date: datetime,
        target_fund: float | int,
        total_bills: float | int,
        total_rolls: float | int,
        total_coins: float | int,
        total: float | int,
        diff: float | int,
        detailed_counts: dict,
):
    if caissier is None:
        raise ValueError("caissier non sélectionné")
    df_current = CONN_SHEETS.read(ttl=0)
    new_data = {
        "Date": selected_date.strftime("%d/%m/%Y"),
        "Dernière modification": datetime.now(ZoneInfo("CET")).strftime("%d/%m/%Y %H:%M:%S"),
        "Boutique": boutique,
        "Caissier": caissier,
        "Total Compté": round(total, 2),
        "Fond Cible": round(target_fund, 2),
        "Écart / Solde": round(diff, 2),
        "Total Billets": round(total_bills, 2),
        "Total Rouleaux": round(total_rolls, 2),
        "Total Pièces": round(total_coins, 2),
        **detailed_counts,
    }
    df_maj = pd.concat([df_current, pd.DataFrame([new_data])], ignore_index=True)
    CONN_SHEETS.update(data=df_maj)

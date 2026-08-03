import pandas as pd
import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
from . import reset_session_states, DATE_FMT


CONN_STOCKS = st.connection("stocks", type=GSheetsConnection)
STOCK_TYPES = ["Physique", "TooGoodToGo"]
PRODUCTS = {
    "pâtissières": [
        "chocolat",
        "caramel",
        "framboise",
        "vanille",
        "pistache",
        "citron",
        "cerise",
        "noisette",
        "passion",
    ],
    "coques": [
        "lait",
        "noir",
    ],
    "partager": [
        "citron",
        "abricot",
        "pistache",
        "tiramisu",
        "paris brest",
    ],
    "mini": [
        "chocolat",
        "pralines",
        "nature",
        "mix",
    ],
    "salées": [
        "tomate",
        "chèvre miel",
        "chorizo",
    ],
}


def display_input_products():
    product_counts = {}
    session_state_keys = []
    for tab, (cat, product_list) in zip(
        st.tabs(list(map(str.capitalize, PRODUCTS.keys()))),
        PRODUCTS.items(),
    ):
        with tab:
            for col, prefix in zip(st.columns(len(STOCK_TYPES)), STOCK_TYPES):
                with col:
                    _, center, _ = st.columns([1,3,1])
                    with center:
                        st.subheader(prefix)
                    for product in product_list:
                        col1, col2= st.columns(2)
                        with col1:
                            st.write(f"{product.capitalize()}")
                        with col2:
                            ss_key = f"{prefix}.{cat}.{product}"
                            product_counts[ss_key] = st.number_input(
                                "label", min_value=0, value=0, step=1, key=ss_key, label_visibility="collapsed",
                            )
                            session_state_keys.append(ss_key)
    return product_counts, session_state_keys


def format_counts_table(new_counts: dict, sep: str="."):
    rows = []
    for key, value in new_counts.items():
        parts = key.split(sep)
        rows.append(parts + [value])
    return pd.DataFrame(rows, columns=["TYPE", "CATÉGORIE", "PRODUIT", "QUANTITÉ"])


def save_to_gsheet(
        df: pd.DataFrame,
        date: datetime,
        caissier: str,
        boutique: str,
        ss_keys: list
):
    try:
        if caissier is None:
            raise ValueError("caissier non sélectionné")
        cols = list(df.columns)
        df["Caissier"] = [caissier] + [None] * (len(df) - 1)
        df["Date"] = [date.strftime(DATE_FMT)] + [None] * (len(df) - 1)
        CONN_STOCKS.update(data=df[["Caissier", "Date"] + cols], worksheet=boutique)
    except Exception as err:
        st.session_state["saving_status"] = "error"
        st.session_state["saving_error"] = err
    else:
        st.session_state["saving_status"] = "success"
        reset_session_states(ss_keys=ss_keys)

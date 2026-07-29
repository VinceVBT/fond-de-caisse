import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection


CONN_STOCKS = st.connection("stocks", type=GSheetsConnection)
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


def rename_columns(df: pd.DataFrame, new_cols: list[str]):
    return df.rename(columns={col: new for col, new in zip(df.columns, new_cols)})


def display_tables_products(prefix: str):
    product_counts = {}
    session_state_keys = []
    for tab, (cat, product_list) in zip(
        st.tabs(list(map(str.capitalize, PRODUCTS.keys()))),
        PRODUCTS.items(),
    ):
        with tab:
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
    return product_counts


def format_counts_table(new_counts: dict, sep: str="."):
    rows = []
    for key, value in new_counts.items():
        parts = key.split(sep)
        rows.append(parts + [value])
    # n_levels = len(rows[0]) - 1
    # columns = level_names or [f"level_{i}" for i in range(n_levels)]
    # columns.append("value")
    return pd.DataFrame(rows, columns=["TYPE", "CATÉGORIE", "PRODUIT", "QUANTITÉ"])

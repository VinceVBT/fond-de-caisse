import pandas as pd
import streamlit as st
from utils import select_infos, reset_session_states
from utils.stocks import (
    CONN_STOCKS, PRODUCTS,
    rename_columns, display_tables_products, format_counts_table,
)


st.title("📊 Stocks et TGTG")
st.caption("Saisie des stocks et ToGoodToGo")

caissier, boutique, selected_date = select_infos()
st.divider()

st.subheader(f"🖊️ Saisie des stocks")

product_counts = {}
stocks_session_state_keys = []
tab_physic, tab_tgtg = st.tabs(["Quantité restante", "ToGoodToGo"])
with tab_physic:
    physic_count = display_tables_products(prefix="PHYSIC")
    stocks_session_state_keys.extend(list(physic_count.keys()))
    product_counts["PHYSIC"] = format_counts_table(physic_count)
with tab_tgtg:
    tgtg_count = display_tables_products(prefix="TGTG")
    stocks_session_state_keys.extend(list(tgtg_count.keys()))
    product_counts["TGTG"] = format_counts_table(tgtg_count)

st.button(
    "Réinitialiser",
    on_click=lambda: reset_session_states(stocks_session_state_keys),
    use_container_width=True,
)

df = pd.concat(
    [product_counts["PHYSIC"], product_counts["TGTG"]],
    axis=0,
).reset_index(drop=True).pivot_table(
    index=["CATÉGORIE", "PRODUIT"],
    columns="TYPE",
    values="QUANTITÉ",
    fill_value=0,
).reset_index()

int_columns, cap_columns = [], []
for col in df.columns:
    if col not in ("CATÉGORIE", "PRODUIT"):
        int_columns.append(col)
    else:
        cap_columns.append(col)
df[int_columns] = df[int_columns].astype(int)
for col in cap_columns:
    df[col] = df[col].apply(lambda x: x.capitalize())
df = df.sort_values(by="CATÉGORIE", key=lambda x: x.str.len(), ascending=False).reset_index(drop=True)

st.table(df)

# df = CONN_STOCKS.read(ttl=0)
# df = rename_columns(df, df.iloc[0])
# df = df.iloc[1:].reset_index(drop=True)
# st.data_editor(df, use_container_width=True)

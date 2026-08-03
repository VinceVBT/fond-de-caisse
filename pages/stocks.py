import streamlit as st
from utils import select_infos, reset_session_states
from utils.stocks import (
    display_input_products, format_counts_table, save_to_gsheet, PRODUCTS,
)


st.title("📊 Stocks et TGTG")
st.caption("Saisie des stocks et ToGoodToGo")

caissier, boutique, selected_date = select_infos()
st.divider()

st.subheader(f"🖊️ Saisie des stocks")

product_counts, stocks_session_state_keys = display_input_products()
reset_col, reload_col = st.columns(2)
with reset_col:
    st.button(
        "Réinitialiser",
        on_click=lambda: reset_session_states(stocks_session_state_keys),
        use_container_width=True,
    )
with reload_col:
    st.button(
        "Recharger les références",
        on_click=lambda: PRODUCTS.load_product_refs(),
        use_container_width=True,
    )

df = format_counts_table(product_counts).reset_index(drop=True).pivot_table(
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

st.button(
    "Enregistrer les stocks",
    on_click=lambda: save_to_gsheet(df, date=selected_date, caissier=caissier, boutique=boutique, ss_keys=stocks_session_state_keys),
    type="primary",
    use_container_width=True,
)
if st.session_state.get("saving_status") == "error":
    st.error(f"Erreur pendant la sauvegarde : {st.session_state.get("saving_error")}")
elif st.session_state.get("saving_status") == "success":
    st.success(f"✅ Stocks enregistrés avec succès dans Google Sheets !")
else:
    pass

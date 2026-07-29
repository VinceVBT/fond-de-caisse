import streamlit as st
from src.utils import (
    BOUTIQUES_FUND, BILLS_LIST, COINS_ROLLS,
    fmt_coin, select_infos, reset_inputs_caisse, save_counting,
)


st.title("💰 Fond de Caisse")
st.caption("Comptage du fond de caisse & enregistrement")

caissier, boutique, selected_date = select_infos()
st.divider()

st.subheader("🔢 Saisie des Coupures")
bills_count, rolls_count, coins_count = {}, {}, {}
tab1, tab2, tab3 = st.tabs(["💶 Billets", "💰 Rouleaux", "🪙 Pièces isolées"])
caisse_session_state_keys = []

with tab1:
    cols = st.columns(2)
    for idx, bill_value in enumerate(BILLS_LIST):
        with cols[idx % 2]:
            ss_key = f"caisse_bill_{bill_value}"
            bills_count[bill_value] = st.number_input(
                f"Billet {bill_value}€", min_value=0, value=0, step=1, key=ss_key,
            )
            caisse_session_state_keys.append(ss_key)

with tab2:
    cols = st.columns(2)
    for idx, (coin_value, roll_total) in enumerate(COINS_ROLLS.items()):
        with cols[idx % 2]:
            ss_key = f"caisse_roll_{coin_value}"
            rolls_count[coin_value] = st.number_input(
                f"Rouleau {coin_value:{fmt_coin(coin_value)}}€ ({roll_total:{fmt_coin(roll_total)}}€)",
                min_value=0,
                value=0,
                step=1,
                key=ss_key,
            )
            caisse_session_state_keys.append(ss_key)

with tab3:
    cols = st.columns(2)
    for idx, coin_value in enumerate(COINS_ROLLS.keys()):
        with cols[idx % 2]:
            ss_key = f"caisse_coin_{coin_value}"
            coins_count[coin_value] = st.number_input(
                f"Pièce {coin_value:{fmt_coin(coin_value)}}€",
                min_value=0,
                value=0,
                step=1,
                key=f"caisse_coin_{coin_value}",
            )
            caisse_session_state_keys.append(ss_key)

total_bills = sum(value * count for value, count in bills_count.items())
total_rolls = sum(COINS_ROLLS[value] * count for value, count in rolls_count.items())
total_coins = sum(value * count for value, count in coins_count.items())
total = total_bills + total_rolls + total_coins
target_fund = BOUTIQUES_FUND[boutique]
diff = total - target_fund

st.button(
    "Réinitialiser",
    on_click=lambda: reset_inputs_caisse(caisse_session_state_keys),
    use_container_width=True,
)

st.divider()

st.subheader("📊 Récapitulatif")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(f"Fond théorique (boutique {boutique})", f"{target_fund:.2f} €")
with col2:
    st.metric("Total compté", f"{total:.2f} €")
with col3:
    st.metric("Écart/Solde du comptage", f"{diff:+.2f} €")

save_params = {
    "caissier": caissier,
    "boutique": boutique,
    "selected_date": selected_date,
    "target_fund": target_fund,
    "total_bills": total_bills,
    "total_rolls": total_rolls,
    "total_coins": total_coins,
    "total": total,
    "diff": diff,
}

if st.button("Enregistrer le comptage", type="primary", use_container_width=True):
    try:
        save_counting(**save_params)
    except Exception as err:
        st.error(f"Erreur pendant la sauvegarde : {err}")
    else:
        st.success(f"✅ Comptage enregistré avec succès dans Google Sheets pour **{boutique}** !")

import streamlit as st
from utils import BOUTIQUES_FUND, select_infos, reset_session_states
from utils.caisse import (
    BILLS_LIST, COINS_ROLLS, MD_CENTERED_RECAP,
    fmt_coin, save_and_reset_session_state,
)


st.title("💰 Fond de Caisse")
st.caption("Comptage du fond de caisse & enregistrement")

caissier, boutique, selected_date = select_infos()
st.divider()

col1, col2 = st.columns([2, 1])
with col1:
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

    total_bills, total_rolls, total_coins = 0, 0, 0
    detailed_counts = {}
    for value, count in bills_count.items():
        total_bills += value * count
        detailed_counts[f"b_{value}"] = count
    for value, count in rolls_count.items():
        total_bills += COINS_ROLLS[value] * count
        detailed_counts[f"r_{value}"] = count
    for value, count in coins_count.items():
        total_bills += value * count
        detailed_counts[f"p_{value}"] = count

    total = total_bills + total_rolls + total_coins
    target_fund = BOUTIQUES_FUND[boutique]
    diff = total - target_fund

    st.button(
        "Réinitialiser",
        on_click=lambda: reset_session_states(caisse_session_state_keys),
        use_container_width=True,
    )

with col2:
    st.subheader("📊 Récapitulatif")
    st.markdown(MD_CENTERED_RECAP, unsafe_allow_html=True)
    st.metric("Fond théorique", f"{target_fund:.2f} €")
    st.metric("Total compté", f"{total:.2f} €")
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
        "detailed_counts": detailed_counts,
    }

    st.button(
        "Enregistrer le comptage",
        on_click=lambda: save_and_reset_session_state(save_params=save_params, ss_keys=caisse_session_state_keys),
        type="primary",
        use_container_width=True,
    )
if st.session_state.get("saving_status") == "error":
    st.error(f"Erreur pendant la sauvegarde : {st.session_state.get("saving_error")}")
elif st.session_state.get("saving_status") == "success":
    st.success(f"✅ Comptage enregistré avec succès dans Google Sheets !")
else:
    pass

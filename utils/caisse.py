from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from . import reset_session_states, DATE_FMT, DATETIME_FMT


BILLS_LIST = [100, 50, 20, 10, 5]
COINS_ROLLS = {
    2: 50,
    1: 25,
    0.5: 20,
    0.2: 8,
    0.1: 4,
}
CONN_CAISSE = st.connection("caisse", type=GSheetsConnection)

MD_CENTERED_RECAP = """
    <style>
    div[data-testid="stMetric"] {
        text-align: center !important;
    }
    label[data-testid="stMetricLabel"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    label[data-testid="stMetricLabel"] div[data-testid="stMarkdownContainer"] {
        display: block !important;
        width: 100% !important;
        text-align: center !important;
    }
    label[data-testid="stMetricLabel"] p {
        text-align: center !important;
        width: 100% !important;
        font-size: 1rem !important;
    }
    div[data-testid="stMetricValue"] div[data-testid="stMarkdownContainer"] {
        display: block !important;
        width: 100% !important;
        text-align: center !important;
    }
    div[data-testid="stMetricValue"] p {
        text-align: center !important;
        width: 100% !important;
        font-size: 2.5rem !important;
    }
    </style>
"""


def fmt_coin(value):
    return ".2f" if value < 1 else ""


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
    df_current = CONN_CAISSE.read(ttl=0)
    new_data = {
        "Date": selected_date.strftime(DATE_FMT),
        "Dernière modification": datetime.now(ZoneInfo("Europe/Paris")).strftime(DATETIME_FMT),
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
    CONN_CAISSE.update(data=df_maj)


def save_and_reset_session_state(save_params: dict, ss_keys: list):
    try:
        save_counting(**save_params)
    except Exception as err:
        st.session_state["saving_status"] = "error"
        st.session_state["saving_error"] = err
    else:
        st.session_state["saving_status"] = "success"
        reset_session_states(ss_keys=ss_keys)

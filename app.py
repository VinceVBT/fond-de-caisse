import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# ---------------------------------------------------------
# Page Config
# ---------------------------------------------------------
st.set_page_config(
    page_title="DÉTAIL ESPÈCES - Fond de Caisse",
    page_icon="💶",
    layout="centered"
)

# Connexion à Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("💶 DÉTAIL ESPÈCES")
st.caption("Comptage du fond de caisse & enregistrement")

# ---------------------------------------------------------
# 1. Informations Générales
# ---------------------------------------------------------
st.subheader("📋 Information Caisse")
col_b, col_c, col_f = st.columns([1.5, 1.5, 1])

with col_b:
    boutique = st.selectbox("Nom de la boutique", ["Cordeliers", "Foch"])

valeur_fond_defaut = 106.70 if boutique == "Cordeliers" else 100.00

with col_c:
    caissier = st.text_input("Nom du Caissier / Opérateur", placeholder="Ex: Vincent")

with col_f:
    fond_theo = st.number_input("Fond cible (€)", value=valeur_fond_defaut, step=10.0)

st.divider()

# ---------------------------------------------------------
# 2. Saisie des espèces
# ---------------------------------------------------------
st.subheader("🔢 Saisie des Coupures")

tab1, tab2, tab3 = st.tabs(["💶 Billets", "🪙 Rouleaux", "🪙 Pièces isolées"])

billets_list = [500, 200, 100, 50, 20, 10, 5]
billets = {}

with tab1:
    cols = st.columns(2)
    for idx, b in enumerate(billets_list):
        with cols[idx % 2]:
            billets[b] = st.number_input(f"Billet {b} €", min_value=0, value=0, step=1, key=f"b_{b}")

rouleaux_keys = ["2€ (50€)", "1€ (25€)", "0.50€ (20€)", "0.20€ (8€)", "0.10€ (4€)", "0.05€ (2.5€)", "0.02€ (1€)", "0.01€ (0.5€)"]
rouleaux_vals = {"2€ (50€)": 50, "1€ (25€)": 25, "0.50€ (20€)": 20, "0.20€ (8€)": 8, "0.10€ (4€)": 4, "0.05€ (2.5€)": 2.5, "0.02€ (1€)": 1, "0.01€ (0.5€)": 0.5}
rouleaux = {}

with tab2:
    cols = st.columns(2)
    for idx, r in enumerate(rouleaux_keys):
        with cols[idx % 2]:
            rouleaux[r] = st.number_input(f"Rouleau {r}", min_value=0, value=0, step=1, key=f"r_{r}")

pieces_keys = ["2", "1", "0.50", "0.20", "0.10", "0.05", "0.02", "0.01"]
pieces = {}

with tab3:
    cols = st.columns(2)
    for idx, p in enumerate(pieces_keys):
        with cols[idx % 2]:
            pieces[p] = st.number_input(f"Pièce {p} €", min_value=0, value=0, step=1, key=f"p_{p}")

# Totaux
total_billets = sum(k * v for k, v in billets.items())
total_rouleaux = sum(rouleaux_vals[k] * v for k, v in rouleaux.items())
total_pieces = sum(float(k) * v for k, v in pieces.items())
total_general = total_billets + total_rouleaux + total_pieces
ecart = total_general - fond_theo

st.divider()

# ---------------------------------------------------------
# 3. Récapitulatif & Enregistrement
# ---------------------------------------------------------
st.subheader("📊 Récapitulatif")
col1, col2 = st.columns(2)
col1.metric("Total compté", f"{total_general:.2f} €")
col2.metric("Fond cible", f"{fond_theo:.2f} €")

st.metric("Écart / Solde du comptage", f"{ecart:+.2f} €")

st.divider()

if st.button("💾 Enregistrer le comptage", type="primary", use_container_width=True):
    if not caissier.strip():
        st.error("⚠️ Veuillez renseigner le nom du caissier avant d'enregistrer.")
    else:
        try:
            # Récupération des données existantes
            df_existant = conn.read(ttl=0)
            
            # Préparation de la nouvelle ligne
            nouvelle_entree = {
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Heure": datetime.now().strftime("%H:%M:%S"),
                "Boutique": boutique,
                "Caissier": caissier,
                "Total Compté": round(total_general, 2),
                "Fond Cible": round(fond_theo, 2),
                "Écart / Solde": round(ecart, 2),
                "Total Billets": round(total_billets, 2),
                "Total Rouleaux": round(total_rouleaux, 2),
                "Total Pièces": round(total_pieces, 2)
            }
            
            # Ajout et écriture dans Google Sheets
            import pandas as pd
            df_mis_a_jour = pd.concat([df_existant, pd.DataFrame([nouvelle_entree])], ignore_index=True)
            conn.update(data=df_mis_a_jour)
            
            st.success(f"✅ Comptage enregistré avec succès dans Google Sheets pour **{boutique}** !")
        except Exception as e:
            st.error(f"❌ Erreur lors de l'enregistrement dans Google Sheets : {e}")

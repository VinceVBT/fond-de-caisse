from datetime import datetime
import io
import streamlit as st
from reportlab.lib.pagesizes import mm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# ---------------------------------------------------------
# Configuration de la page Streamlit (Optimisé iPad/Tablette)
# ---------------------------------------------------------
st.set_page_config(
    page_title="Détail Espèces - Fond de Caisse",
    page_icon="💶",
    layout="wide"
)

# Style CSS personnalisé pour l'ergonomie tactile (iPad)
st.markdown("""
    <style>
    .stButton>button {
        height: 3em;
        font-weight: bold;
        border-radius: 8px;
    }
    .total-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Fonction de génération du PDF (Format Ticket 80mm)
# ---------------------------------------------------------
def generate_pdf_receipt(boutique, caissier, fond_theo, billets_data, rouleaux_data, pieces_data):
    buffer = io.BytesIO()
    # Ticket de caisse 80mm
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(80 * mm, 220 * mm),
        rightMargin=4 * mm,
        leftMargin=4 * mm,
        topMargin=4 * mm,
        bottomMargin=4 * mm
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TicketTitle',
        parent=styles['Heading1'],
        fontSize=12,
        alignment=1, # Center
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )
    text_center = ParagraphStyle('Center', parent=styles['Normal'], fontSize=8, alignment=1)
    text_left = ParagraphStyle('Left', parent=styles['Normal'], fontSize=8, alignment=0)
    text_right = ParagraphStyle('Right', parent=styles['Normal'], fontSize=8, alignment=2)
    section_style = ParagraphStyle('Section', parent=styles['Normal'], fontSize=8.5, fontName='Helvetica-Bold', spaceBefore=4, spaceAfter=2)

    elements = []

    # En-tête
    elements.append(Paragraph("<b>DÉTAIL ESPÈCES</b>", title_style))
    elements.append(Paragraph(f"<b>{boutique.upper()}</b>", text_center))
    elements.append(Paragraph("Comptage de Fond de Caisse", text_center))
    elements.append(Spacer(1, 3 * mm))

    # Meta Infos
    now = datetime.now()
    meta_text = f"""
    <b>Date:</b> {now.strftime('%d/%m/%Y')} &nbsp;&nbsp; <b>Heure:</b> {now.strftime('%H:%M')}<br/>
    <b>Opérateur / Caissier:</b> {caissier if caissier else 'Non renseigné'}
    """
    elements.append(Paragraph(meta_text, text_left))
    elements.append(Spacer(1, 3 * mm))

    # Tableau helper
    def create_table(items, col_widths=[28*mm, 18*mm, 26*mm]):
        data = [["Désignation", "Qté", "Montant"]]
        for label, qte, total in items:
            if qte > 0:
                data.append([label, str(qte), f"{total:.2f} €"])
        if len(data) == 1:
            return None
        
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
        ]))
        return t

    # Section Billets
    t_billets = create_table([(f"Billet {k}€", v, k*v) for k, v in billets_data.items()])
    if t_billets:
        elements.append(Paragraph("BILLETS", section_style))
        elements.append(t_billets)
        elements.append(Spacer(1, 2 * mm))

    # Section Rouleaux
    rouleaux_valeurs = {
        "2€ (50€)": (25*2, 50), "1€ (25€)": (25*1, 25), "0.50€ (20€)": (40*0.5, 20),
        "0.20€ (8€)": (40*0.2, 8), "0.10€ (4€)": (40*0.1, 4), "0.05€ (2.5€)": (50*0.05, 2.5),
        "0.02€ (1€)": (50*0.02, 1), "0.01€ (0.5€)": (50*0.01, 0.5)
    }
    t_rouleaux = create_table([(f"Rlx {k}", v, rouleaux_valeurs[k][1]*v) for k, v in rouleaux_data.items()])
    if t_rouleaux:
        elements.append(Paragraph("ROULEAUX DE PIÈCES", section_style))
        elements.append(t_rouleaux)
        elements.append(Spacer(1, 2 * mm))

    # Section Pièces Isolées
    t_pieces = create_table([(f"Pièce {k}€", v, float(k)*v) for k, v in pieces_data.items()])
    if t_pieces:
        elements.append(Paragraph("PIÈCES ISOLÉES", section_style))
        elements.append(t_pieces)
        elements.append(Spacer(1, 2 * mm))

    # Totaux
    total_billets = sum(k * v for k, v in billets_data.items())
    total_rouleaux = sum(rouleaux_valeurs[k][1] * v for k, v in rouleaux_data.items())
    total_pieces = sum(float(k) * v for k, v in pieces_data.items())
    grand_total = total_billets + total_rouleaux + total_pieces
    ecart = grand_total - fond_theo

    elements.append(Spacer(1, 2 * mm))
    totals_data = [
        ["TOTAL ESPÈCES :", f"{grand_total:.2f} €"],
        ["Fond de caisse cible :", f"{fond_theo:.2f} €"],
        ["À PRÉLEVER / REMISE :", f"{ecart:+.2f} €"]
    ]
    t_totaux = Table(totals_data, colWidths=[42*mm, 30*mm])
    t_totaux.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(t_totaux)
    elements.append(Spacer(1, 4 * mm))

    # Zone Signatures
    sig_data = [
        [Paragraph(f"<b>Signature Caissier :</b><br/>{caissier}", text_left)],
        [Spacer(1, 12 * mm)],
        [Paragraph("<b>Validation Responsable / Gérant :</b>", text_left)],
        [Spacer(1, 12 * mm)]
    ]
    t_sig = Table(sig_data, colWidths=[72*mm])
    t_sig.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, 1), 0.5, colors.grey),
        ('BOX', (0, 2), (-1, 3), 0.5, colors.grey),
    ]))
    elements.append(t_sig)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# ---------------------------------------------------------
# Interface Utilisateur Streamlit
# ---------------------------------------------------------
st.title("💶 Comptage de Caisse — Détail Espèces")

# Initialisation du State pour la réinitialisation
if "reset_key" not in st.session_state:
    st.session_state.reset_key = 0

# Block En-tête
col_info1, col_info2, col_info3 = st.columns(3)
with col_info1:
    boutique = st.text_input("Nom de la Boutique / Magasin", value="Boutique Centre-Ville")
with col_info2:
    caissier = st.text_input("Nom du Caissier / Opérateur *", value="", placeholder="Ex: Jean Dupont")
with col_info3:
    fond_theo = st.number_input("Fond de Caisse Cible (€)", value=300.0, step=10.0)

st.divider()

col_input, col_summary = st.columns([2, 1])

with col_input:
    # 1. BILLETS
    st.subheader("1. Billets")
    billets_list = [500, 200, 100, 50, 20, 10, 5]
    billets_data = {}
    cols_b = st.columns(4)
    for i, b in enumerate(billets_list):
        with cols_b[i % 4]:
            billets_data[b] = st.number_input(
                f"{b} €", min_value=0, step=1, key=f"b_{b}_{st.session_state.reset_key}"
            )

    st.divider()

    # 2. ROULEAUX DE PIÈCES
    st.subheader("2. Rouleaux de Pièces")
    rouleaux_list = [
        ("2€ (50€)", 50.0), ("1€ (25€)", 25.0), ("0.50€ (20€)", 20.0),
        ("0.20€ (8€)", 8.0), ("0.10€ (4€)", 4.0), ("0.05€ (2.5€)", 2.5),
        ("0.02€ (1€)", 1.0), ("0.01€ (0.5€)", 0.5)
    ]
    rouleaux_data = {}
    cols_r = st.columns(4)
    for i, (label, val) in enumerate(rouleaux_list):
        with cols_r[i % 4]:
            rouleaux_data[label] = st.number_input(
                f"Rlx {label}", min_value=0, step=1, key=f"r_{label}_{st.session_state.reset_key}"
            )

    st.divider()

    # 3. PIÈCES ISOLÉES
    st.subheader("3. Pièces Isolées")
    pieces_list = ["2", "1", "0.50", "0.20", "0.10", "0.05", "0.02", "0.01"]
    pieces_data = {}
    cols_p = st.columns(4)
    for i, p in enumerate(pieces_list):
        with cols_p[i % 4]:
            pieces_data[p] = st.number_input(
                f"Pièce {p} €", min_value=0, step=1, key=f"p_{p}_{st.session_state.reset_key}"
            )

# calculs en temps réel
rouleaux_valeurs = {
    "2€ (50€)": 50, "1€ (25€)": 25, "0.50€ (20€)": 20, "0.20€ (8€)": 8,
    "0.10€ (4€)": 4, "0.05€ (2.5€)": 2.5, "0.02€ (1€)": 1, "0.01€ (0.5€)": 0.5
}
total_billets = sum(k * v for k, v in billets_data.items())
total_rouleaux = sum(rouleaux_valeurs[k] * v for k, v in rouleaux_data.items())
total_pieces = sum(float(k) * v for k, v in pieces_data.items())
grand_total = total_billets + total_rouleaux + total_pieces
ecart = grand_total - fond_theo

with col_summary:
    st.subheader("📊 Synthèse en direct")
    
    st.markdown(f"""
    <div class="total-box">
        <h4>TOTAL ESPÈCES : {grand_total:.2f} €</h4>
        <p>• Billets : {total_billets:.2f} €<br/>
        • Rouleaux : {total_rouleaux:.2f} €<br/>
        • Pièces : {total_pieces:.2f} €</p>
        <hr>
        <p><b>Fond cible :</b> {fond_theo:.2f} €</p>
        <h3><b>Remise Banque : {ecart:+.2f} €</b></h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # Génération du fichier PDF du ticket
    pdf_bytes = generate_pdf_receipt(
        boutique, caissier, fond_theo, billets_data, rouleaux_data, pieces_data
    )
    
    # Bouton Téléchargement / Impression
    st.download_button(
        label="📄 Télécharger le Ticket (PDF / Impresion)",
        data=pdf_bytes,
        file_name=f"ticket_detail_especes_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )
    
    if st.button("🔄 Réinitialiser le comptage", use_container_width=True):
        st.session_state.reset_key += 1
        st.rerun()

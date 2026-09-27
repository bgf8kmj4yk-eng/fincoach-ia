"""
app.py
------
Application Streamlit - FinCoach IA
Tableau de bord interactif de gestion budgétaire, analyse 50/30/20 et simulation d'épargne.

Auteur: Développeur Senior Finance & Data Science
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import du script de génération de données en secours si transactions.csv n'existe pas
from generate_data import generate_financial_data

# ==============================================================================
# CONFIGURATION STREAMLIT & STYLING
# ==============================================================================
st.set_page_config(
    page_title="FinCoach IA - Gestion Budgétaire & Épargne",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection de CSS personnalisé pour un rendu moderne et élégant
st.markdown("""
<style>
    /* Thème global et conteneurs */
    .main {
        background-color: #F8FAFC;
    }
    
    /* Cartes Métriques (KPIs) */
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .metric-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #10B981;
        font-weight: 600;
        margin-top: 4px;
    }

    /* Style des titres et conteneurs de section */
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #1E293B;
        border-left: 4px solid #3B82F6;
        padding-left: 12px;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    
    /* Custom Sidebar Header */
    .sidebar-header {
        text-align: center;
        padding: 10px 0 20px 0;
    }
    .sidebar-header h2 {
        color: #FFFFFF;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sidebar-header p {
        color: #64748B;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# FONCTIONS UTILITAIRES & CHARGEMENT DES DONNÉES
# ==============================================================================

@st.cache_data
def load_and_clean_data(file_source) -> pd.DataFrame:
    """
    Charge et valide le fichier CSV de transactions.
    
    Parameters:
        file_source: Chemin str ou objet UploadedFile Streamlit.
        
    Returns:
        pd.DataFrame nettoyé et structuré.
    """
    try:
        if isinstance(file_source, str):
            df = pd.read_csv(file_source)
        else:
            df = pd.read_csv(file_source)
            
        # Colonnes attendues
        required_cols = {"Date", "Description", "Montant", "Type", "Categorie"}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            st.error(f"⚠️ Le fichier CSV est invalide. Colonnes manquantes : {', '.join(missing)}")
            return pd.DataFrame()

        # Conversion et nettoyage de la colonne Date
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"]).copy()

        # Conversion et nettoyage de la colonne Montant
        df["Montant"] = pd.to_numeric(df["Montant"], errors="coerce")
        df = df.dropna(subset=["Montant"]).copy()

        # Normalisation des chaînes de caractères
        df["Type"] = df["Type"].astype(str).str.strip()
        df["Categorie"] = df["Categorie"].astype(str).str.strip()
        df["Description"] = df["Description"].astype(str).str.strip()

        # Tri par date décroissante
        df = df.sort_values(by="Date", ascending=False).reset_index(drop=True)
        return df

    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {str(e)}")
        return pd.DataFrame()


def get_default_data() -> pd.DataFrame:
    """Garantit qu'un fichier transactions.csv existe et le charge."""
    csv_path = "transactions.csv"
    if not os.path.exists(csv_path):
        with st.spinner("Génération du jeu de données par défaut..."):
            generate_financial_data(csv_path)
    return load_and_clean_data(csv_path)


# ==============================================================================
# SIDEBAR & FILTRES GLOBATION
# ==============================================================================

with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.image("logo.png", use_container_width=True)

    st.markdown("""
    <div class="sidebar-header">
        <p>Assistant de Gestion Budgétaire</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.subheader("📥 Source des données")
    uploaded_file = st.file_uploader(
        "Importer un fichier CSV",
        type=["csv"],
        help="Format requis : Date, Description, Montant, Type, Categorie"
    )

    if uploaded_file is not None:
        raw_df = load_and_clean_data(uploaded_file)
        st.success("✅ Fichier personnalisé chargé !")
    else:
        raw_df = get_default_data()
        st.info("ℹ️ Données par défaut (`transactions.csv`) chargées.")

    st.divider()
    st.subheader("📅 Filtre Temporel")

    if not raw_df.empty:
        # Création des options de sélection de mois (ex: '2026-09')
        raw_df["Mois_Annee"] = raw_df["Date"].dt.strftime("%Y-%m")
        available_months = sorted(raw_df["Mois_Annee"].unique(), reverse=True)
        
        filter_options = ["Toutes les périodes"] + available_months
        selected_month = st.selectbox(
            "Sélectionner la période",
            options=filter_options,
            index=0
        )

        # Application du filtre
        if selected_month != "Toutes les périodes":
            df_filtered = raw_df[raw_df["Mois_Annee"] == selected_month].copy()
        else:
            df_filtered = raw_df.copy()
    else:
        df_filtered = pd.DataFrame()

# Vérification que des données sont disponibles
if df_filtered.empty:
    st.warning("⚠️ Aucune transaction trouvée pour les critères sélectionnés.")
    st.stop()


# ==============================================================================
# EN-TÊTE DU DASHBOARD
# ==============================================================================
st.title("📊 FinCoach IA - Tableau de Bord Financier")
st.markdown("Optimisez votre budget, analysez vos habitudes de consommation et projetez votre patrimoine grâce aux intérêts composés.")
st.write("")


# ==============================================================================
# SECTION 1 : VUE D'ENSEMBLE (KPIs)
# ==============================================================================
st.markdown('<div class="section-title">1. Vue d\'Ensemble des Flux Financiers</div>', unsafe_allow_html=True)

# Calcul des indicateurs clés
# 1. Revenus totaux : Montants positifs de type Revenu
revenus_totaux = df_filtered[
    (df_filtered["Type"] == "Revenu") & (df_filtered["Montant"] > 0)
]["Montant"].sum()

# En sécurité si Type == Revenu n'est pas utilisé strictement mais qu'il y a des valeurs > 0
if revenus_totaux == 0:
    revenus_totaux = df_filtered[df_filtered["Montant"] > 0]["Montant"].sum()

# 2. Dépenses totales : Valeurs absolues des montants négatifs de type Dépense
depenses_totales = abs(df_filtered[
    (df_filtered["Type"] == "Dépense") & (df_filtered["Montant"] < 0)
]["Montant"].sum())

# 3. Épargne réalisée : Valeurs absolues des montants de type Epargne ou Categorie Investissement & Epargne
epargne_realisee = abs(df_filtered[
    ((df_filtered["Type"] == "Epargne") | (df_filtered["Categorie"] == "Investissement & Epargne")) & 
    (df_filtered["Montant"] < 0)
]["Montant"].sum())

# Capacité d'Épargne Totale (Solde net de la période)
capacite_epargne = revenus_totaux - depenses_totales

# Taux d'épargne réactif (%)
taux_epargne = (capacite_epargne / revenus_totaux * 100) if revenus_totaux > 0 else 0.0

# Affichage des KPIs dans 4 colonnes métriques élégantes
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Revenus Totaux</div>
        <div class="metric-value" style="color: #059669;">+{revenus_totaux:,.2f} €</div>
        <div class="metric-sub">Entrées nettes</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Dépenses Totales</div>
        <div class="metric-value" style="color: #DC2626;">-{depenses_totales:,.2f} €</div>
        <div class="metric-sub">Sorties courantes</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    color_epargne = "#2563EB" if capacite_epargne >= 0 else "#DC2626"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Capacité d'Épargne</div>
        <div class="metric-value" style="color: {color_epargne};">{capacite_epargne:+,.2f} €</div>
        <div class="metric-sub">Solde restant disponible</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    color_taux = "#059669" if taux_epargne >= 20 else ("#D97706" if taux_epargne >= 10 else "#DC2626")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Taux d'Épargne</div>
        <div class="metric-value" style="color: {color_taux};">{taux_epargne:.1f} %</div>
        <div class="metric-sub">Objectif recommandé : ≥ 20%</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")


# ==============================================================================
# SECTION 2 : ANALYSE DES DÉPENSES & RÈGLE 50/30/20
# ==============================================================================
st.markdown('<div class="section-title">2. Répartition des Dépenses & Audit 50/30/20</div>', unsafe_allow_html=True)

col_chart, col_rule = st.columns([1, 1], gap="large")

# --- 2.1 Graphique Donut Plotly des Dépenses par Catégorie ---
with col_chart:
    st.subheader("🍩 Répartition par Catégorie")
    
    # Filtrer uniquement les dépenses courantes
    df_depenses = df_filtered[df_filtered["Type"] == "Dépense"].copy()
    if df_depenses.empty:
        # Fallback si Type n'est pas spécifié strictement
        df_depenses = df_filtered[df_filtered["Montant"] < 0].copy()
    
    df_depenses["Montant_Abs"] = df_depenses["Montant"].abs()
    cat_summary = df_depenses.groupby("Categorie")["Montant_Abs"].sum().reset_index()

    if not cat_summary.empty and cat_summary["Montant_Abs"].sum() > 0:
        fig_donut = px.pie(
            cat_summary,
            values="Montant_Abs",
            names="Categorie",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Bold,
        )
        fig_donut.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Montant : %{value:,.2f} €<br>Part : %{percent}"
        )
        fig_donut.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(t=20, b=20, l=10, r=10),
            height=380
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    else:
        st.info("Aucune dépense enregistrée pour cette période.")

# --- 2.2 Règle Budgétaire 50/30/20 ---
with col_rule:
    st.subheader("🎯 Audit Règle 50 / 30 / 20")
    st.caption("Méthode financière de référence : 50% Besoins, 30% Envies, 20% Épargne & Investissements.")

    # Classification des catégories existantes
    besoins_cats = ["Logement & Charges", "Alimentation", "Abonnements"]
    envies_cats = ["Sorties & Plaisirs", "Shopping & Perso"]
    epargne_cats = ["Investissement & Epargne"]

    # Calcul des montants réels
    total_besoins = df_depenses[df_depenses["Categorie"].isin(besoins_cats)]["Montant_Abs"].sum()
    total_envies = df_depenses[df_depenses["Categorie"].isin(envies_cats)]["Montant_Abs"].sum()
    
    # L'épargne réunit les virements PEA/Epargne + la capacité d'épargne restante
    total_epargne = epargne_realisee + max(0, capacite_epargne - epargne_realisee)

    # Base de comparaison : Revenus totaux ou Somme des flux
    base_calcul = revenus_totaux if revenus_totaux > 0 else (total_besoins + total_envies + total_epargne)

    if base_calcul > 0:
        pct_besoins = (total_besoins / base_calcul) * 100
        pct_envies = (total_envies / base_calcul) * 100
        pct_epargne = (total_epargne / base_calcul) * 100

        # Données comparatives Théorie vs Réalité
        rule_data = pd.DataFrame({
            "Poste": ["Besoins (50%)", "Envies (30%)", "Épargne (20%)"],
            "Réalité (%)": [round(pct_besoins, 1), round(pct_envies, 1), round(pct_epargne, 1)],
            "Cible (%)": [50.0, 30.0, 20.0]
        })

        # Bar chart comparatif Plotly
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=rule_data["Poste"],
            y=rule_data["Réalité (%)"],
            name="Votre Réalité (%)",
            marker_color=["#3B82F6" if pct_besoins <= 50 else "#EF4444",
                          "#8B5CF6" if pct_envies <= 30 else "#EF4444",
                          "#10B981" if pct_epargne >= 20 else "#F59E0B"],
            text=rule_data["Réalité (%)"].astype(str) + "%",
            textposition="auto"
        ))
        fig_bar.add_trace(go.Bar(
            x=rule_data["Poste"],
            y=rule_data["Cible (%)"],
            name="Cible Théorique (%)",
            marker_color="#CBD5E1",
            text=rule_data["Cible (%)"].astype(str) + "%",
            textposition="auto"
        ))

        fig_bar.update_layout(
            barmode="group",
            height=320,
            margin=dict(t=20, b=20, l=10, r=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            yaxis=dict(title="Pourcentage du Revenu (%)", range=[0, max(100, max(rule_data["Réalité (%)"]) + 10)])
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # Conseils contextuels automatisés
        if pct_epargne >= 20:
            st.success("🌟 **Félicitations !** Vous respectez l'objectif de 20% d'épargne. Continuez à investir votre excédent.")
        else:
            st.warning(f"💡 **Conseil FinCoach** : Votre taux d'épargne est de **{pct_epargne:.1f}%**. Essayez d'optimiser le poste **{'Besoins' if pct_besoins > 50 else 'Envies'}** pour vous rapprocher des 20%.")

st.write("")


# ==============================================================================
# SECTION 3 : SIMULATEUR D'INVESTISSEMENT & INTÉRÊTS COMPOSÉS
# ==============================================================================
st.markdown('<div class="section-title">3. Simulateur d\'Épargne & Intérêts Composés (PEA / ETF)</div>', unsafe_allow_html=True)
st.markdown("Simulez la croissance de votre capital en investissant régulièrement une partie de votre capacité d'épargne sur les marchés financiers (rendement moyen historique de l'ETF MSCI World ~7%).")

col_params, col_chart_sim = st.columns([1, 2], gap="large")

with col_params:
    st.subheader("⚙️ Paramètres de Simulation")

    # Pré-calculer la valeur par défaut du slider d'épargne basée sur la capacité d'épargne courante
    default_monthly_save = max(50.0, float(round(capacite_epargne, -1))) if capacite_epargne > 0 else 250.0

    mensualite = st.slider(
        "Épargne Mensuelle Investie (€/mois)",
        min_value=50,
        max_value=2000,
        value=int(min(default_monthly_save, 2000)),
        step=50,
        help="Montant versé chaque mois sur votre portefeuille d'investissement."
    )

    capital_initial = st.number_input(
        "Capital Initial Déjà Investi (€)",
        min_value=0,
        max_value=100000,
        value=1000,
        step=500
    )

    rendement_annuel = st.slider(
        "Rendement Annuel Moyen Estimé (%)",
        min_value=1.0,
        max_value=15.0,
        value=7.0,
        step=0.5,
        help="Performance annuelle moyenne (7.0% est la moyenne historique nette de l'ETF MSCI World)."
    )

    horizon_annees = st.slider(
        "Horizon d'Investissement (Années)",
        min_value=5,
        max_value=35,
        value=20,
        step=1
    )

# --- MOTEUR DE CALCUL DES INTÉRÊTS COMPOSÉS ---
def calculate_compound_interest(p_init: float, monthly_pmt: float, annual_rate: float, years: int) -> pd.DataFrame:
    """Calcul mois par mois de la valeur future du portefeuille et de la ventilation capital / intérêts."""
    months = years * 12
    monthly_rate = annual_rate / 100 / 12

    records = []
    current_val = float(p_init)
    cum_invested = float(p_init)

    # Mois 0
    records.append({
        "Mois": 0,
        "Année": 0.0,
        "Capital Versé": cum_invested,
        "Intérêts Générés": 0.0,
        "Valeur Totale": current_val
    })

    for m in range(1, months + 1):
        # Application des intérêts du mois + versement mensuel
        interest = current_val * monthly_rate
        current_val += interest + monthly_pmt
        cum_invested += monthly_pmt
        
        # Enregistrer uniquement à la fin de chaque année (ou tous les mois)
        if m % 12 == 0 or m == months:
            records.append({
                "Mois": m,
                "Année": m / 12,
                "Capital Versé": round(cum_invested, 2),
                "Intérêts Générés": round(current_val - cum_invested, 2),
                "Valeur Totale": round(current_val, 2)
            })

    return pd.DataFrame(records)

df_sim = calculate_compound_interest(capital_initial, mensualite, rendement_annuel, horizon_annees)

with col_chart_sim:
    st.subheader("📈 Projection de la Croissance du Patrimoine")

    # Graphique d'aire empilée (Area Chart Plotly)
    fig_area = go.Figure()
    
    # Tracé du Capital Versé
    fig_area.add_trace(go.Scatter(
        x=df_sim["Année"],
        y=df_sim["Capital Versé"],
        mode="lines",
        name="Capital Versé",
        stackgroup="one",
        fillcolor="rgba(59, 130, 246, 0.5)",
        line=dict(color="#3B82F6", width=2),
        hovertemplate="Année %{x}<br>Capital Versé : %{y:,.0f} €"
    ))
    
    # Tracé des Intérêts Générés
    fig_area.add_trace(go.Scatter(
        x=df_sim["Année"],
        y=df_sim["Intérêts Générés"],
        mode="lines",
        name="Intérêts Composés Générés",
        stackgroup="one",
        fillcolor="rgba(16, 185, 129, 0.6)",
        line=dict(color="#10B981", width=2),
        hovertemplate="Année %{x}<br>Intérêts Générés : %{y:,.0f} €"
    ))

    fig_area.update_layout(
        height=380,
        margin=dict(t=20, b=40, l=10, r=10),
        xaxis=dict(title="Temps Écoulé (Années)", dtick=5),
        yaxis=dict(title="Valeur du Portefeuille (€)"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.35, xanchor="center", x=0.5),
        hovermode="x unified"
    )

    st.plotly_chart(fig_area, use_container_width=True)

# --- MATRICE RÉSUMÉE DE PROJECTION À 10, 15 ET 20 ANS ---
st.markdown("#### 🎯 Bilan des Projections de Patrimoine")

# Extraire les valeurs pour 10 ans, 15 ans et 20 ans
df_sim_indexed = df_sim.set_index("Année")
sub_years = [y for y in [10, 15, 20, horizon_annees] if y in df_sim_indexed.index]
sub_years = sorted(list(set(sub_years)))

cols_proj = st.columns(len(sub_years))
for idx, yr in enumerate(sub_years):
    row_yr = df_sim_indexed.loc[yr]
    val_tot = row_yr["Valeur Totale"]
    val_cap = row_yr["Capital Versé"]
    val_int = row_yr["Intérêts Générés"]
    multiplier = (val_tot / val_cap) if val_cap > 0 else 1.0

    with cols_proj[idx]:
        st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid #10B981;">
            <div class="metric-label">Horizon {int(yr)} Ans</div>
            <div class="metric-value" style="color: #0F172A; font-size: 1.5rem;">{val_tot:,.0f} €</div>
            <div style="font-size: 0.8rem; color: #475569; margin-top: 6px;">
                • Capital : <b>{val_cap:,.0f} €</b><br>
                • Intérêts : <b style="color: #059669;">+{val_int:,.0f} €</b><br>
                • Multiplicateur : <b style="color: #2563EB;">x{multiplier:.2f}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.write("")
st.markdown("---")
st.caption(" FinCoach IA - Développé avec Streamlit, Pandas & Plotly. Données sécurisées et traitement local.")

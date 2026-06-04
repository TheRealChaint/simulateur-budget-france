import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulateur Budgétaire de Précision", layout="wide")

st.title("🇫🇷 Simulateur d'Arbitrages Budgétaires (en G€)")
st.write("Ajustez les budgets, sélectionnez un modèle d'inflation historique et observez l'impact long terme.")

# --- CHARGEMENT DES FICHIERS CSV ---
@st.cache_data
def load_base_data():
    try:
        return pd.read_csv("nomenclature_budget_france_3.csv")
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_mesures_data():
    try:
        return pd.read_csv("mesures_chocs_france_2.csv")
    except Exception:
        return pd.DataFrame()

df = load_base_data()
df_mesures = load_mesures_data()

df_depenses = df[df["Type"] == "Depense"]
df_recettes = df[df["Type"] == "Recette"]
PIB_BASE = 2920.0

# --- INTERFACE EN FORMULAIRE ---
with st.form("simulation_form"):
    
    # 1. 🎛️ MODULE : CURSEURS MACRO & SCÉNARIOS D'INFLATION
    st.header("🎛️ Paramètres Macroéconomiques & Modèles d'Inflation")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.markdown("**Structurel & Retraites**")
        age_retraite = st.slider("Âge légal de départ à la retraite", min_value=60.0, max_value=67.0, value=64.0, step=0.5)
        pt_indice = st.slider("Revalorisation du Point d'Indice des fonctionnaires (%)", min_value=-5.0, max_value=15.0, value=0.0, step=1.0)
        
    with col_p2:
        st.markdown("**Fiscalité Paramétrique**")
        taux_tva = st.slider("Taux normal de TVA (%)", min_value=15.0, max_value=25.0, value=20.0, step=0.5)
        taux_is = st.slider("Taux de l'Impôt sur les Sociétés (%)", min_value=15.0, max_value=35.0, value=25.0, step=1.0)
        
    with col_p3:
        st.markdown("**🔥 Scénario d'Inflation Historique**")
        # Sélection du modèle d'inflation
        scenario_inflation = st.selectbox(
            "Choisir le modèle d'inflation sous-jacent",
            ["Grande Modération (Inflation stable à 2%)", 
             "Choc Post-COVID (Pic à 5% puis hausse des taux d'intérêt)", 
             "Stagflation 1973 (Inflation à 8%, croissance nulle)"]
        )
        var_effectifs = st.slider("Variation des effectifs publics (en milliers)", min_value=-250, max_value=250, value=0, step=10)

    st.markdown("---")

    # 2. ⚡ MODULE : MESURES CHOCS
    st.header("⚡ Bibliothèque de Réformes & Mesures Chocs")
    mesures_activees = {}
    if not df_mesures.empty:
        categories_mesures = df_mesures["Categorie"].unique()
        cols_mesures = st.columns(3)
        for i, categorie in enumerate(categories_mesures):
            col_target = cols_mesures[i % 3]
            with col_target:
                st.markdown(f"**{categorie}**")
                mesures_cat = df_mesures[df_mesures["Categorie"] == categorie]
                for _, row in mesures_cat.iterrows():
                    nom = row["Nom"]
                    desc = f"{row['Description']} (Dépenses: {row['Impact_Depenses']} G€ / Recettes: +{row['Impact_Recettes']} G€)"
                    mesures_activees[nom] = st.checkbox(nom, help=desc)
    
    st.markdown("---")
    
    # 3. 📉 PANNEAUX MICRO DÉPENSES ET RECETTES
    col_depenses, col_recettes = st.columns(2)
    modifs_dep = {}
    modifs_rec = {}
    
    with col_depenses:
        st.header("📉 Dépenses Micro par Mission")
        if not df.empty:
            missions = df_depenses["Categorie/Mission"].unique()
            for mission in missions:
                with st.expander(f"📁 {mission}", expanded=False):
                    programmes = df_depenses[df_depenses["Categorie/Mission"] == mission]
                    for _, row in programmes.iterrows():
                        prog = row["Poste/Programme"]
                        budget = row["Budget_Actuel_G€"]
                        modifs_dep[prog] = st.number_input(prog, min_value=0.0, value=float(budget), step=0.1, format="%.1f")
                    
    with col_recettes:
        st.header("📈 Recettes Fiscales de Base")
        if not df.empty:
            categories_rec = df_recettes["Categorie/Mission"].unique()
            for cat in categories_rec:
                with st.expander(f"💰 {cat}", expanded=False):
                    postes = df_recettes[df_recettes["Categorie/Mission"] == cat]
                    for _, row in postes.iterrows():
                        poste = row["Poste/Programme"]
                        budget = row["Budget_Actuel_G€"]
                        modifs_rec[poste] = st.number_input(poste, min_value=0.0, value=float(budget), step=0.1, format="%.1f")

    st.markdown("---")
    submit_button = st.form_submit_button("🚀 Lancer la simulation globale")

# --- LOGIQUE ET RÉSULTATS ---
if submit_button:
    
    # Paramètres de l'inflation choisie
    if "Grande Modération" in scenario_inflation:
        inf_rate = 0.02; taux_interet_prime = 0.0; impact_pib_nominal = 1.02
    elif "Post-COVID" in scenario_inflation:
        inf_rate = 0.05; taux_interet_prime = 2.5; impact_pib_nominal = 1.04
    else: # Stagflation
        inf_rate = 0.08; taux_interet_prime = 5.0; impact_pib_nominal = 0.98 # Destruction de croissance réelle

    # Calculs de base
    total_depenses_base = sum(modifs_dep.values())
    total_recettes_base = sum(modifs_rec.values())
    
    impact_mesures_depenses = 0.0
    impact_mesures_recettes = 0.0
    for nom_mesure, is_checked in mesures_activees.items():
        if is_checked:
            ligne_mesure = df_mesures[df_mesures["Nom"] == nom_mesure].iloc[0]
            impact_mesures_depenses += float(ligne_mesure["Impact_Depenses"])
            impact_mesures_recettes += float(ligne_mesure["Impact_Recettes"])
            
    # Impacts structurels
    impact_macro_depenses = (64.0 - age_retraite) * 3.5 + (pt_indice * 2.0) + (var_effectifs / 100.0) * 3.5
    impact_macro_recettes = (taux_tva - 20.0) * 9.0 + (taux_is - 25.0) * 2.5
    
    # Application de l'effet premier tour de l'inflation sur les recettes (TVA mécanique)
    total_recettes_reformees = (total_recettes_base + impact_mesures_recettes + impact_macro_recettes) * (1 + (inf_rate * 0.5))
    total_depenses_reformees = total_depenses_base + impact_mesures_depenses + impact_macro_depenses
    
    budget_base_depenses_initial = df_depenses["Budget_Actuel_G€"].sum()
    var_depenses = total_depenses_reformees - budget_base_depenses_initial
    var_recettes = total_recettes_reformees - df_recettes["Budget_Actuel_G€"].sum()
    
    # Multiplicateurs
    impact_keynesien = (impact_mesures_depenses + impact_macro_depenses) * 0.8
    solde = total_recettes_reformees - total_depenses_reformees
    deficit_pib = (abs(solde) / PIB_BASE) * 100
    
    croissance_2027 = (1.1 + (impact_keynesien / 15.0) + (0.4 if deficit_pib < 3.0 else -0.2)) * impact_pib_nominal

    # Scores
    score_social = max(0, min(100, 100 + (64.0 - age_retraite) * 3 + pt_indice * 1.5 - (inf_rate * 300)))
    probabilite_politique = max(0, min(100, ((100 if var_recettes > 0 else 30) * 0.32) + (50 * 0.25) + ((100 if deficit_pib < 3 else 20) * 0.43)))

    # --- AFFICHAGE DE LA SYNTHÈSE ---
    st.header("🎯 Synthèse des Arbitrages")
    
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Solde de l'État", f"{solde:.1f} G€", f"{deficit_pib:.1f}% du PIB")
    col_r2.metric("Croissance Nominale (2027)", f"{croissance_2027:.2f}%")
    col_r3.metric("Faisabilité Politique", f"{probabilite_politique:.0f}/100")
    col_r4.metric("Score Social (Ajusté Inflation)", f"{score_social:.0f}/100")

    # Calcul de la dégradation de la dette selon les taux d'intérêt induits par l'inflation
    st.subheader("⏳ Évolution de la dette long-terme (Impact du modèle d'inflation)")
    annees = [2027, 2030, 2035]
    
    # Effet boule de neige accentué si l'inflation pousse les taux d'intérêt (taux_interet_prime)
    dette_2027 = 112.0 + (deficit_pib - 3)*1.2
    dette_2030 = dette_2027 + (deficit_pib - 3)*3.5 + (taux_interet_prime * 1.5)
    dette_2035 = dette_2030 + (deficit_pib - 3)*6.0 + (taux_interet_prime * 4.0)
    
    df_traj = pd.DataFrame({"Année": annees, "Dette / PIB (%)": [dette_2027, dette_2030, dette_2035], "Plafond UE (%)": [60, 60, 60]}).set_index("Année")
    st.line_chart(df_traj)

else:
    st.info("💡 Sélectionnez vos options et modifiez les montants, puis cliquez sur le bouton 'Lancer la simulation globale'.")

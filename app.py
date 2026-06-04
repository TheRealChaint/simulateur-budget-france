import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulateur Budgétaire de Précision", layout="wide")

st.title("🇫🇷 Simulateur d'Arbitrages Budgétaires (en G€)")
st.write("Ajustez les budgets, modifiez les paramètres macroéconomiques et cochez des réformes chocs.")

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
        # On charge le nouveau fichier !
        return pd.read_csv("mesures_chocs_france_2.csv")
    except Exception:
        return pd.DataFrame()

df = load_base_data()
df_mesures = load_mesures_data()

df_depenses = df[df["Type"] == "Depense"]
df_recettes = df[df["Type"] == "Recette"]
PIB_BASE = 2920.0

# --- INTERFACE EN 3 PANS (FORMULAIRE) ---
with st.form("simulation_form"):
    
    # 1. 🎛️ NOUVEAU MODULE : CURSEURS MACRO & FISCAUX
    st.header("🎛️ Paramètres Macroéconomiques & Fiscaux")
    st.write("Ajustez les grands curseurs structurels de l'économie française.")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.markdown("**Retraites**")
        # Base légale actuelle : 64 ans (Réforme 2023). 1 année ~ 3.5 G€ (subvention d'équilibre).
        age_retraite = st.slider("Âge légal de départ à la retraite", min_value=60.0, max_value=67.0, value=64.0, step=0.5, help="Réduire l'âge augmente le déficit des caisses que l'État doit combler. L'augmenter génère des économies.")
        
    with col_p2:
        st.markdown("**Fiscalité**")
        # 1 point de TVA = ~9 G€. 1 point d'IS = ~2.5 G€.
        taux_tva = st.slider("Taux normal de TVA (%)", min_value=15.0, max_value=25.0, value=20.0, step=0.5, help="Actuellement à 20%. Taxe sur la consommation.")
        taux_is = st.slider("Taux de l'Impôt sur les Sociétés (%)", min_value=15.0, max_value=35.0, value=25.0, step=1.0, help="Actuellement à 25%. Impôt sur les bénéfices des entreprises.")
        
    with col_p3:
        st.markdown("**Fonction Publique (État, Hôpital, Territoriale)**")
        # 1% de point d'indice = ~2 G€. 100k fonctionnaires = ~3.5 G€
        pt_indice = st.slider("Revalorisation du Point d'Indice (%)", min_value=-5.0, max_value=15.0, value=0.0, step=1.0, help="Geler ou augmenter le salaire de tous les fonctionnaires.")
        var_effectifs = st.slider("Variation des effectifs publics (en milliers)", min_value=-250, max_value=250, value=0, step=10, help="Nombre de postes créés ou supprimés (non-remplacement).")

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
    
    # 3. 📉 PANNEAUX DÉPENSES ET RECETTES (Micro)
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
    
    # 1. Calculs des curseurs manuels (Micro)
    total_depenses_base = sum(modifs_dep.values())
    total_recettes_base = sum(modifs_rec.values())
    
    # 2. Ajout de l'impact des mesures cochées
    impact_mesures_depenses = 0.0
    impact_mesures_recettes = 0.0
    
    for nom_mesure, is_checked in mesures_activees.items():
        if is_checked:
            ligne_mesure = df_mesures[df_mesures["Nom"] == nom_mesure].iloc[0]
            impact_mesures_depenses += float(ligne_mesure["Impact_Depenses"])
            impact_mesures_recettes += float(ligne_mesure["Impact_Recettes"])
            
    # 3. Ajout de l'impact des Curseurs Macro & Fiscaux (Formules de calcul)
    # Retraite : Si on descend sous 64 ans, l'État dépense plus. Si on monte, il économise.
    impact_macro_depenses = (64.0 - age_retraite) * 3.5 
    # Fonction publique : Salaire + Effectifs
    impact_macro_depenses += (pt_indice * 2.0) 
    impact_macro_depenses += (var_effectifs / 100.0) * 3.5
    
    # Impôts : TVA et IS
    impact_macro_recettes = (taux_tva - 20.0) * 9.0
    impact_macro_recettes += (taux_is - 25.0) * 2.5
    
    # Totaux finaux réels
    total_depenses_reformees = total_depenses_base + impact_mesures_depenses + impact_macro_depenses
    total_recettes_reformees = total_recettes_base + impact_mesures_recettes + impact_macro_recettes
    
    budget_base_depenses_initial = df_depenses["Budget_Actuel_G€"].sum()
    budget_base_recettes_initial = df_recettes["Budget_Actuel_G€"].sum()
    
    var_depenses = total_depenses_reformees - budget_base_depenses_initial
    var_recettes = total_recettes_reformees - budget_base_recettes_initial
    
    # Impacts macroéconomiques & Scoring
    impact_keynesien = ((impact_mesures_depenses + impact_macro_depenses) * 0.8)
    impact_social_cumul = 0.0
    nb_progs_sociaux = 0
    
    for _, row in df_depenses.iterrows():
        prog = row["Poste/Programme"]
        variation_curseur = modifs_dep[prog] - row["Budget_Actuel_G€"]
        if "Dette" not in prog:
            impact_keynesien += variation_curseur * 0.8
        if any(keyword in prog.lower() for keyword in ["inclusion", "handicap", "premier degré", "maladie"]):
            impact_social_cumul += (variation_curseur / row["Budget_Actuel_G€"]) * 100
            nb_progs_sociaux += 1

    solde = total_recettes_reformees - total_depenses_reformees
    deficit_pib = (abs(solde) / PIB_BASE) * 100
    
    impact_offre = 0.4 if deficit_pib < 3.0 else -0.2
    croissance_2027 = 1.1 + (impact_keynesien / 15.0) + impact_offre

    # Score Social intégrant la retraite et le salaire public
    score_social = 100 + (impact_social_cumul / max(1, nb_progs_sociaux)) * 1.5
    score_social += (64.0 - age_retraite) * 3 # Baisse de l'âge = point bonus, Hausse = malus
    score_social += pt_indice * 1.5 # Hausse salaire = bonus
    score_social = max(0, min(100, score_social))
    
    # Faisabilité Politique
    tol_gauche = 100 if (var_recettes > 0 and age_retraite <= 64) else 30
    tol_droite = 100 if (var_recettes <= 0 and age_retraite >= 64 and deficit_pib < 3) else 20
    tol_centre = 50 + (50 if deficit_pib < 4 else -30)
    probabilite_politique = max(0, min(100, (tol_gauche * 0.32) + (tol_centre * 0.25) + (tol_droite * 0.43)))

    # --- 4. AFFICHAGE DE LA SYNTHÈSE ---
    st.header("🎯 Synthèse des Arbitrages")
    
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Solde de l'État", f"{solde:.1f} G€", f"{deficit_pib:.1f}% du PIB")
    col_r2.metric("Croissance Estimée (2027)", f"{croissance_2027:.2f}%")
    col_r3.metric("Faisabilité Politique", f"{probabilite_politique:.0f}/100", "Censure risquée" if probabilite_politique < 40 else "Majorité relative")
    col_r4.metric("Score Social", f"{score_social:.0f}/100")

    if deficit_pib > 3.0:
        st.error(f"❌ Alerte Européenne : Déficit à {deficit_pib:.1f}%. Procédure pour déficit excessif.")
    else:
        st.success(f"🇪🇺 Validé par l'UE : Déficit conforme ({deficit_pib:.1f}%).")
        
    st.subheader("⏳ Évolution de la dette (en % du PIB)")
    annees = [2027, 2030, 2035]
    ratio_dette = [112.0 + (deficit_pib - 3)*1.2, 115.0 + (deficit_pib - 3)*3.5, 118.0 + (deficit_pib - 3)*6.0]
    df_traj = pd.DataFrame({"Année": annees, "Dette / PIB (%)": ratio_dette, "Plafond UE (%)": [60, 60, 60]}).set_index("Année")
    st.line_chart(df_traj)

else:
    st.info("💡 Sélectionnez vos options et modifiez les montants, puis cliquez sur le bouton 'Lancer la simulation globale'.")

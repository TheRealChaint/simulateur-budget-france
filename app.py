import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Simulateur Budgétaire de Précision", layout="wide")

st.title("🇫🇷 Simulateur d'Arbitrages Budgétaires (en G€)")
st.write("Ajustez les budgets par paliers de 0,1 G€. Cochez les mesures chocs pour voir l'impact immédiat sur la trajectoire.")

# --- CHARGEMENT DES FICHIERS CSV ---
@st.cache_data
def load_base_data():
    try:
        return pd.read_csv("nomenclature_budget_france_3.csv")
    except Exception:
        st.error("⚠️ Fichier introuvable : 'nomenclature_budget_france_3.csv'")
        return pd.DataFrame()

@st.cache_data
def load_mesures_data():
    try:
        return pd.read_csv("mesures_chocs_france.csv")
    except Exception:
        st.error("⚠️ Fichier introuvable : 'mesures_chocs_france.csv'")
        return pd.DataFrame()

df = load_base_data()
df_mesures = load_mesures_data()

df_depenses = df[df["Type"] == "Depense"]
df_recettes = df[df["Type"] == "Recette"]
PIB_BASE = 2920.0

# --- INTERFACE EN 2 PANS (FORMULAIRE) ---
with st.form("simulation_form"):
    
    # ⚡ NOUVEAU MODULE DYNAMIQUE : MESURES CHOCS & RÉFORMES
    st.header("⚡ Bibliothèque de Réformes & Mesures Chocs")
    st.write("Cochez les mesures de votre programme pour intégrer automatiquement leurs effets sur le budget de l'État.")
    
    mesures_activees = {}
    
    if not df_mesures.empty:
        categories_mesures = df_mesures["Categorie"].unique()
        # Création de colonnes dynamiques pour l'affichage (max 3 colonnes)
        cols_mesures = st.columns(3)
        
        for i, categorie in enumerate(categories_mesures):
            col_target = cols_mesures[i % 3] # Alterne l'affichage sur 3 colonnes
            with col_target:
                st.markdown(f"**{categorie}**")
                mesures_cat = df_mesures[df_mesures["Categorie"] == categorie]
                for _, row in mesures_cat.iterrows():
                    nom = row["Nom"]
                    desc = f"{row['Description']} (Dépenses: {row['Impact_Depenses']} G€ / Recettes: +{row['Impact_Recettes']} G€)"
                    # Création dynamique de la case à cocher
                    mesures_activees[nom] = st.checkbox(nom, help=desc)
    
    st.markdown("---")
    
    # PANNEAUX DÉPENSES ET RECETTES
    col_depenses, col_recettes = st.columns(2)
    modifs_dep = {}
    modifs_rec = {}
    
    with col_depenses:
        st.header("📉 Dépenses de l'État (Missions & Dette)")
        if not df.empty:
            missions = df_depenses["Categorie/Mission"].unique()
            for mission in missions:
                is_expanded = True if "Financiers" in mission else False
                with st.expander(f"📁 {mission}", expanded=is_expanded):
                    programmes = df_depenses[df_depenses["Categorie/Mission"] == mission]
                    for _, row in programmes.iterrows():
                        prog = row["Poste/Programme"]
                        budget = row["Budget_Actuel_G€"]
                        desc = row.get("Description", "")
                        modifs_dep[prog] = st.number_input(prog, min_value=0.0, value=float(budget), step=0.1, format="%.1f", help=desc)
                    
    with col_recettes:
        st.header("📈 Recettes Fiscales de Base")
        if not df.empty:
            categories_rec = df_recettes["Categorie/Mission"].unique()
            for cat in categories_rec:
                with st.expander(f"💰 {cat}", expanded=True):
                    postes = df_recettes[df_recettes["Categorie/Mission"] == cat]
                    for _, row in postes.iterrows():
                        poste = row["Poste/Programme"]
                        budget = row["Budget_Actuel_G€"]
                        desc = row.get("Description", "")
                        modifs_rec[poste] = st.number_input(poste, min_value=0.0, value=float(budget), step=0.1, format="%.1f", help=desc)

    st.markdown("---")
    submit_button = st.form_submit_button("🚀 Lancer la simulation globale")

# --- LOGIQUE ET RÉSULTATS ---
if submit_button:
    
    # 1. Calculs des curseurs manuels
    total_depenses_base = sum(modifs_dep.values())
    total_recettes_base = sum(modifs_rec.values())
    
    # 2. Ajout dynamique de l'impact des mesures cochées
    impact_mesures_depenses = 0.0
    impact_mesures_recettes = 0.0
    
    for nom_mesure, is_checked in mesures_activees.items():
        if is_checked:
            ligne_mesure = df_mesures[df_mesures["Nom"] == nom_mesure].iloc[0]
            impact_mesures_depenses += float(ligne_mesure["Impact_Depenses"])
            impact_mesures_recettes += float(ligne_mesure["Impact_Recettes"])
    
    # Totaux finaux réels
    total_depenses_reformees = total_depenses_base + impact_mesures_depenses
    total_recettes_reformees = total_recettes_base + impact_mesures_recettes
    
    budget_base_depenses_initial = df_depenses["Budget_Actuel_G€"].sum()
    budget_base_recettes_initial = df_recettes["Budget_Actuel_G€"].sum()
    
    var_depenses = total_depenses_reformees - budget_base_depenses_initial
    var_recettes = total_recettes_reformees - budget_base_recettes_initial
    
    # Impacts macroéconomiques
    impact_keynesien = 0.0
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

    # On ajoute l'effet keynesien des mesures chocs
    impact_keynesien += (impact_mesures_depenses * 0.8)

    solde = total_recettes_reformees - total_depenses_reformees
    deficit_pib = (abs(solde) / PIB_BASE) * 100
    
    impact_offre = 0.4 if deficit_pib < 3.0 else -0.2
    croissance_2027 = 1.1 + (impact_keynesien / 15.0) + impact_offre

    score_social = max(0, min(100, 100 + (impact_social_cumul / max(1, nb_progs_sociaux)) * 1.5))
    if "Retraite à 60 ans (40 annuités)" in mesures_activees and mesures_activees["Retraite à 60 ans (40 annuités)"]: 
        score_social = min(100, score_social + 15)
    
    tol_gauche = 100 if var_recettes > 0 else 30
    tol_droite = 100 if (var_recettes <= 0 and deficit_pib < 3) else 20
    tol_centre = 50 + (50 if deficit_pib < 4 else -30)
    probabilite_politique = max(0, min(100, (tol_gauche * 0.32) + (tol_centre * 0.25) + (tol_droite * 0.43)))

    # --- 3. MOTEUR DE PROFILAGE ---
    profil = ""
    politicien = ""
    ecole_eco = ""
    description_profil = ""

    if var_depenses < -10 and var_recettes <= 0:
        profil = "Consolidation & Offre"
        politicien = "Raymond Barre / François Fillon"
        ecole_eco = "Ordolibéralisme / École Néoclassique"
        description_profil = "Réduction franche de la sphère publique et des déficits. Assainissement des finances et compétitivité."
    elif var_depenses > 15 and var_recettes > 10:
        profil = "Relance Sociale & Redistribution"
        politicien = "François Mitterrand (1981) / Front Populaire"
        ecole_eco = "Keynésianisme Traditionnel"
        description_profil = "Relance par la demande globale. Hausse de la fiscalité pour financer l'État-Providence."
    elif var_depenses > 10 and var_recettes <= 0:
        profil = "Relance par le Déficit"
        politicien = "Souvent associé au souverainisme économique"
        ecole_eco = "Théorie Monétaire Moderne (MMT)"
        description_profil = "Hausse des dépenses sans augmenter les impôts. Dérapage de la dette à surveiller."
    elif abs(var_depenses) <= 10 and abs(var_recettes) <= 10:
        profil = "Socio-Libéralisme & Équilibre"
        politicien = "Emmanuel Macron / Michel Rocard"
        ecole_eco = "Nouvelle Synthèse Néoclassique"
        description_profil = "De légers ajustements sans brutaliser les impôts ni l'État social."
    else:
        profil = "Approche Hybride"
        politicien = "Pragmatisme de crise"
        ecole_eco = "Pragmatisme Macroéconomique"
        description_profil = "Mélange d'ajustements fiscaux et de coupes ciblées."

    # --- 4. AFFICHAGE DE LA SYNTHÈSE ---
    st.header("🎯 Synthèse des Arbitrages")
    
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Solde de l'État", f"{solde:.1f} G€", f"{deficit_pib:.1f}% du PIB")
    col_r2.metric("Croissance Estimée (2027)", f"{croissance_2027:.2f}%")
    col_r3.metric("Faisabilité Politique", f"{probabilite_politique:.0f}/100", "Censure risquée" if probabilite_politique < 40 else "Majorité relative")
    col_r4.metric("Score Social", f"{score_social:.0f}/100")

    st.markdown("---")
    st.subheader("🧠 Analyse de votre doctrine budgétaire")
    st.info(f"**Profil :** {profil} | **Proximité historique :** {politicien} | **École :** {ecole_eco}\n\n{description_profil}")

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

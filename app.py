import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Simulateur Budgétaire", layout="wide")

st.title("🇫🇷 Simulateur d'Arbitrages Budgétaires")
st.write("Ajustez les budgets par paliers de 0,1 G€. Cochez les mesures chocs pour voir l'impact immédiat sur la trajectoire.")

# --- CHARGEMENT DU FICHIER CSV ---
@st.cache_data
def load_data():
    try:
        # Attention à bien mettre le nouveau nom du fichier
        return pd.read_csv("nomenclature_budget_france_3.csv")
    except Exception as e:
        st.error("⚠️ Fichier introuvable. Veuillez placer 'nomenclature_budget_france_3.csv' dans le même dossier.")
        return pd.DataFrame(columns=["Type", "Categorie/Mission", "Poste/Programme", "Budget_Actuel_G€", "Description"])

df = load_data()
df_depenses = df[df["Type"] == "Depense"]
df_recettes = df[df["Type"] == "Recette"]

PIB_BASE = 2920.0

# --- INTERFACE EN 2 PANS (FORMULAIRE) ---
with st.form("simulation_form"):
    
    # ⚡ NOUVEAU MODULE : MESURES CHOCS & RÉFORMES
    st.subheader("⚡ Mesures Chocs & Réformes Structurelles")
    st.write("Activez des réformes emblématiques pour impacter immédiatement le budget (Indépendant des curseurs ci-dessous).")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        st.markdown("**Privatisations & Ventes d'Actifs**")
        chk_privatisation_routes = st.checkbox("🛣️ Privatisation totale du réseau routier national (-2.0 G€ d'entretien)", help="Vente des dernières routes non concédées. Inspiré des politiques libérales historiques.")
        chk_vente_parts = st.checkbox("🏭 Cession totale des parts de l'État (Renault, Orange, ADP) (-1.5 G€ charge dette)", help="Vente d'actifs pour rembourser massivement la dette et faire baisser les intérêts annuels.")
        chk_privatisation_audiovisuel = st.checkbox("📺 Privatisation de l'audiovisuel public (-4.0 G€ de dépenses)", help="Proposition RN (2024). Vente de France TV et Radio France.")

    with col_m2:
        st.markdown("**Réformes Sociales & Retraites**")
        chk_retraite_60 = st.checkbox("👴 Retraite à 60 ans (+15.0 G€ de subventions)", help="Proposition du NFP. Hausse massive des dépenses sociales (subvention d'équilibre de l'État aux caisses de retraite).")
        chk_fin_ame = st.checkbox("⚕️ Suppression de l'Aide Médicale d'État (-1.2 G€ de dépenses)", help="Proposition LR/RN. Remplacement par une aide médicale d'urgence stricte.")

    with col_m3:
        st.markdown("**Réformes Fiscales**")
        chk_isf_climatique = st.checkbox("💰 Rétablissement de l'ISF avec volet climatique (+3.0 G€ de recettes)", help="Proposition de la gauche. Taxation accrue des grands patrimoines et des actifs très émetteurs de carbone.")
        chk_baisse_tva = st.checkbox("🛒 Baisse de la TVA sur l'énergie à 5,5% (-12.0 G€ de recettes)", help="Proposition transversale pour le pouvoir d'achat face à l'inflation.")
        
    st.markdown("---")
    
    # PANNEAUX DÉPENSES ET RECETTES
    col_depenses, col_recettes = st.columns(2)
    modifs_dep = {}
    modifs_rec = {}
    
    with col_depenses:
        st.header("📉 Dépenses de l'État (Missions & Dette)")
        missions = df_depenses["Categorie/Mission"].unique()
        for mission in missions:
            # On laisse le panneau de la dette ouvert par défaut pour la pédagogie
            is_expanded = True if "Financiers" in mission else False
            with st.expander(f"📁 {mission}", expanded=is_expanded):
                programmes = df_depenses[df_depenses["Categorie/Mission"] == mission]
                for _, row in programmes.iterrows():
                    prog = row["Poste/Programme"]
                    budget = row["Budget_Actuel_G€"]
                    description = row.get("Description", "")
                    modifs_dep[prog] = st.number_input(prog, min_value=0.0, value=float(budget), step=0.1, format="%.1f", help=description)
                    
    with col_recettes:
        st.header("📈 Recettes Fiscales")
        categories_rec = df_recettes["Categorie/Mission"].unique()
        for cat in categories_rec:
            with st.expander(f"💰 {cat}", expanded=True):
                postes = df_recettes[df_recettes["Categorie/Mission"] == cat]
                for _, row in postes.iterrows():
                    poste = row["Poste/Programme"]
                    budget = row["Budget_Actuel_G€"]
                    description = row.get("Description", "")
                    modifs_rec[poste] = st.number_input(poste, min_value=0.0, value=float(budget), step=0.1, format="%.1f", help=description)

    st.markdown("---")
    submit_button = st.form_submit_button("🚀 Lancer la simulation globale")

# --- LOGIQUE ET RÉSULTATS ---
if submit_button:
    
    # 1. Calculs des curseurs (Valeurs saisies par l'utilisateur)
    total_depenses_base = sum(modifs_dep.values())
    total_recettes_base = sum(modifs_rec.values())
    
    # 2. Ajout de l'impact des mesures chocs cochées
    impact_mesures_depenses = 0.0
    impact_mesures_recettes = 0.0
    
    if chk_privatisation_routes: impact_mesures_depenses -= 2.0
    if chk_vente_parts: impact_mesures_depenses -= 1.5
    if chk_privatisation_audiovisuel: impact_mesures_depenses -= 4.0
    if chk_retraite_60: impact_mesures_depenses += 15.0
    if chk_fin_ame: impact_mesures_depenses -= 1.2
    
    if chk_isf_climatique: impact_mesures_recettes += 3.0
    if chk_baisse_tva: impact_mesures_recettes -= 12.0
    
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
        # Variation due aux curseurs (On exclut la dette des effets keynésiens)
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
    if chk_retraite_60: score_social = min(100, score_social + 15)
    
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
        politicien = "Raymond Barre ou François Fillon (2017)"
        ecole_eco = "Ordolibéralisme / École Néoclassique"
        description_profil = "Votre stratégie repose sur une réduction franche de la sphère publique et des déficits. Vous privilégiez l'assainissement des finances et la compétitivité (baisse des charges/impôts), quitte à accepter un choc social et politique à court terme."
    elif var_depenses > 15 and var_recettes > 10:
        profil = "Relance Sociale & Redistribution"
        politicien = "François Mitterrand (1981) ou Programme du NFP"
        ecole_eco = "Keynésianisme Traditionnel"
        description_profil = "Vous menez une politique de relance par la demande globale. En assumant une hausse de la fiscalité, vous financez un État-Providence fort. Le score social est excellent, mais la pression fiscale risque de braquer la droite parlementaire et de créer des fuites de capitaux."
    elif var_depenses > 10 and var_recettes <= 0:
        profil = "Relance par le Déficit"
        politicien = "Modèle atypique (approche souverainiste ou post-crise COVID)"
        ecole_eco = "Théorie Monétaire Moderne (MMT) ou Keynésianisme de l'offre"
        description_profil = "Vous augmentez les dépenses sans augmenter les impôts. C'est une politique du 'Quoi qu'il en coûte'. La croissance de court terme est boostée, mais le dérapage de la dette alerte l'Union Européenne et risque de faire exploser la charge de la dette future."
    elif abs(var_depenses) <= 10 and abs(var_recettes) <= 10:
        profil = "Socio-Libéralisme & Équilibre"
        politicien = "Emmanuel Macron (2017) ou Michel Rocard"
        ecole_eco = "Nouvelle Synthèse Néoclassique"
        description_profil = "Vous optez pour le compromis. De légers ajustements de structure sans brutaliser ni les impôts ni l'État social. Votre faisabilité politique est maximale au centre, mais votre marge de manœuvre face à la dette reste très étroite à l'horizon 2030."
    else:
        profil = "Approche Hybride"
        politicien = "Jacques Chirac ou Nicolas Sarkozy"
        ecole_eco = "Pragmatisme Macroéconomique"
        description_profil = "Votre budget mêle des éléments contradictoires (ex: hausse des impôts mais baisse des dépenses ciblées). C'est un budget de gestion de crise qui cherche à ménager toutes les oppositions, au risque de manquer de lisibilité économique."

    # --- 4. AFFICHAGE DE LA SYNTHÈSE ---
    st.header("🎯 Synthèse des Arbitrages")
    
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Solde de l'État", f"{solde:.1f} G€", f"{deficit_pib:.1f}% du PIB")
    col_r2.metric("Croissance Estimée (2027)", f"{croissance_2027:.2f}%")
    col_r3.metric("Faisabilité Politique", f"{probabilite_politique:.0f}/100", "Risque de censure" if probabilite_politique < 40 else "Majorité relative")
    col_r4.metric("Score Social", f"{score_social:.0f}/100")

    st.markdown("---")
    st.subheader("🧠 Analyse de votre doctrine budgétaire")
    st.info(f"""
    **Profil identifié :** {profil}  
    **Proximité historique :** {politicien}  
    **École économique :** {ecole_eco}
    
    **Analyse :** {description_profil}
    """)

    if deficit_pib > 3.0:
        st.error(f"❌ Alerte Européenne : Déficit à {deficit_pib:.1f}%, procédure pour déficit excessif hautement probable.")
    else:
        st.success(f"🇪🇺 Validé par l'UE : Déficit conforme aux critères ({deficit_pib:.1f}%).")
        
    st.subheader("⏳ Évolution de la dette long-terme")
    annees = [2027, 2030, 2035]
    ratio_dette = [112.0 + (deficit_pib - 3)*1.2, 115.0 + (deficit_pib - 3)*3.5, 118.0 + (deficit_pib - 3)*6.0]
    df_traj = pd.DataFrame({"Année": annees, "Dette / PIB (%)": ratio_dette, "Plafond UE (%)": [60, 60, 60]}).set_index("Année")
    st.line_chart(df_traj)

else:
    st.info("💡 Sélectionnez vos options et modifiez les montants, puis cliquez sur le bouton 'Lancer la simulation globale'.")

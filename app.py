import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simulateur Budgétaire de Précision", layout="wide")

st.title("🇫🇷 Simulateur d'Arbitrages Budgétaires (en G€)")
st.write("Ajustez les budgets, définissez votre politique monétaire (taux directeurs, inflation) et découvrez votre profil politique.")

# --- CHARGEMENT DES FICHIERS CSV ---
@st.cache_data
def load_base_data():
    try:
        return pd.read_csv("nomenclature_budget_france_3.csv")
    except Exception:
        st.error("⚠️ Fichier 'nomenclature_budget_france_3.csv' introuvable.")
        return pd.DataFrame()

@st.cache_data
def load_mesures_data():
    try:
        return pd.read_csv("mesures_chocs_france_4.csv")
    except Exception:
        st.sidebar.error("⚠️ Fichier 'mesures_chocs_france_4.csv' introuvable.")
        return pd.DataFrame()

df = load_base_data()
df_mesures = load_mesures_data()

df_depenses = df[df["Type"] == "Depense"]
df_recettes = df[df["Type"] == "Recette"]
PIB_BASE = 2920.0

# --- INTERFACE EN FORMULAIRE ---
with st.form("simulation_form"):
    
    # 1. 🎛️ MODULE : CURSEURS MACRO, FISCAUX ET MONÉTAIRES
    st.header("🎛️ Paramètres Macroéconomiques & Monétaires")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("**Structurel & Fonction Publique**")
        age_retraite = st.slider("Âge de départ à la retraite", min_value=60.0, max_value=67.0, value=64.0, step=0.5)
        pt_indice = st.slider("Point d'Indice des fonctionnaires (%)", min_value=-5.0, max_value=15.0, value=0.0, step=1.0)
        var_effectifs = st.slider("Effectifs publics (en milliers)", min_value=-250, max_value=250, value=0, step=10)
        
    with col_p2:
        st.markdown("**Fiscalité Paramétrique**")
        taux_tva = st.slider("Taux normal de TVA (%)", min_value=15.0, max_value=25.0, value=20.0, step=0.5)
        taux_is = st.slider("Taux de l'Impôt sur les Sociétés (%)", min_value=10.0, max_value=35.0, value=25.0, step=1.0)
        
    with col_p3:
        st.markdown("**Politique Monétaire & Inflation**")
        scenario_inflation = st.selectbox(
            "Modèle d'inflation sous-jacent",
            ["Grande Modération (Inflation stable à 2%)", 
             "Choc Post-COVID (Pic à 5% puis resserrement)", 
             "Stagflation 1973 (Inflation à 8%, croissance nulle)"]
        )
        # NOUVEAU CURSEUR : Taux directeur de la BCE
        taux_directeur = st.slider("Taux Directeur de la BCE (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.25, help="Un taux élevé freine l'inflation et la croissance, mais fait exploser la charge de la dette.")

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
    else:
        inf_rate = 0.08; taux_interet_prime = 5.0; impact_pib_nominal = 0.98

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
            
    # Impacts structurels (Retraites, Fonction publique)
    impact_macro_depenses = (64.0 - age_retraite) * 3.5 + (pt_indice * 2.0) + (var_effectifs / 100.0) * 3.5
    
    # IMPACT DU TAUX DIRECTEUR : +2.5 G€ de charge de la dette par point au-dessus de 3% (court terme)
    impact_taux_directeur = (taux_directeur - 3.0) * 2.5
    impact_macro_depenses += impact_taux_directeur

    # Impôts
    impact_macro_recettes = (taux_tva - 20.0) * 9.0 + (taux_is - 25.0) * 2.5
    
    total_recettes_reformees = (total_recettes_base + impact_mesures_recettes + impact_macro_recettes) * (1 + (inf_rate * 0.5))
    total_depenses_reformees = total_depenses_base + impact_mesures_depenses + impact_macro_depenses
    
    budget_base_depenses_initial = df_depenses["Budget_Actuel_G€"].sum()
    var_depenses = total_depenses_reformees - budget_base_depenses_initial
    var_recettes = total_recettes_reformees - df_recettes["Budget_Actuel_G€"].sum()
    
    # Multiplicateur Keynésien et Frein Monétaire
    impact_keynesien = (impact_mesures_depenses + impact_macro_depenses - impact_taux_directeur) * 0.8
    solde = total_recettes_reformees - total_depenses_reformees
    deficit_pib = (abs(solde) / PIB_BASE) * 100
    
    # IMPACT DU TAUX DIRECTEUR SUR LA CROISSANCE : Des taux élevés freinent l'économie
    frein_monetaire = (taux_directeur - 3.0) * 0.15
    croissance_2027 = (1.1 + (impact_keynesien / 15.0) + (0.4 if deficit_pib < 3.0 else -0.2) - frein_monetaire) * impact_pib_nominal

    # Scores
    score_social = max(0, min(100, 100 + (64.0 - age_retraite) * 3 + pt_indice * 1.5 - (inf_rate * 300) - (taux_directeur * 1.5)))
    tol_gauche = 100 if (var_recettes > 0 and age_retraite <= 64) else 30
    tol_droite = 100 if (var_recettes <= 0 and age_retraite >= 64 and deficit_pib < 3) else 20
    tol_centre = 50 + (50 if deficit_pib < 4 else -30)
    probabilite_politique = max(0, min(100, (tol_gauche * 0.32) + (tol_centre * 0.25) + (tol_droite * 0.43)))

    # --- AFFICHAGE DE LA SYNTHÈSE DES CHIFFRES ---
    st.header("🎯 Synthèse des Arbitrages")
    
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Solde de l'État", f"{solde:.1f} G€", f"{deficit_pib:.1f}% du PIB")
    col_r2.metric("Croissance Nominale (2027)", f"{croissance_2027:.2f}%")
    col_r3.metric("Faisabilité Politique", f"{probabilite_politique:.0f}/100", "Censure risquée" if probabilite_politique < 40 else "Majorité relative")
    col_r4.metric("Score Social (Ajusté)", f"{score_social:.0f}/100")

    # --- 🧠 MOTEUR D'ANALYSE DÉTAILLÉ ---
    st.markdown("---")
    st.subheader("🧠 Analyse approfondie de votre doctrine budgétaire")
    
    if var_depenses < -15 and var_recettes <= 5:
        profil = "L'Austerité de Choc ou Thérapie de Groupe"
        politicien = "Raymond Barre (1976), François Fillon (2017) ou Margaret Thatcher 🇬🇧"
        ecole_eco = "Ordolibéralisme / École Autrichienne (Monétarisme)"
        analyse_detailed = f"""
        **Votre cap :** Politique de purge budgétaire drastique. Votre priorité est la réduction de la taille de l'État pour restaurer la crédibilité de la signature de la France.
        *   **Performance & Social :** Votre score social ({score_social:.0f}/100) est mis à rude épreuve. Réduire les dépenses publiques provoque un choc de demande à court terme.
        *   **Approbation Politique :** Avec {probabilite_politique:.0f}/100, vous vous appuyez sur un bloc droitier. La gauche s'opposera frontalement à vos mesures via des motions de censure.
        *   **Viabilité Long Terme :** C'est votre point fort. À l'horizon 2035, la trajectoire de la dette s'assainit et l'effet d'éviction s'annule, redonnant de l'air à l'investissement privé.
        """
    elif var_depenses > 15 and var_recettes > 15:
        profil = "Le Grand Soir Budgétaire et Redistributif"
        politicien = "François Mitterrand (1981) ou le Nouveau Front Populaire"
        ecole_eco = "Keynésianisme Strict / Post-Keynésianisme"
        analyse_detailed = f"""
        **Votre cap :** Choc massif de demande globale. Vous utilisez l'arme fiscale (TVA, IS) pour financer un réinvestissement historique dans le modèle social français.
        *   **Performance & Social :** L'indice social est élevé. Le pouvoir d'achat des classes populaires est soutenu.
        *   **Approbation Politique :** Le chemin parlementaire ({probabilite_politique:.0f}/100) sera chaotique face à un bloc central et droitier qui rejettera le 'matraquage fiscal'.
        *   **Viabilité Long Terme :** Attention au retour de flamme de la dette et des taux directeurs. L'augmentation de vos dépenses risque d'engendrer une fuite des capitaux.
        """
    elif var_depenses > 10 and var_recettes <= 0:
        profil = "L'Illusion Monétaire ou l'Aventure de la Dette"
        politicien = "Liz Truss 🇬🇧 (2022) ou politiques populistes de relance non financée"
        ecole_eco = "Théorie Monétaire Moderne (MMT)"
        analyse_detailed = f"""
        **Votre cap :** Pari très risqué consistant à augmenter le train de vie de l'État tout en refusant d'augmenter la fiscalité.
        *   **Performance & Social :** À court terme, l'économie est grisée par l'injection de liquidités. 
        *   **Approbation Politique :** Faisabilité calculée à {probabilite_politique:.0f}/100. L'incohérence comptable finira par bloquer le projet.
        *   **Viabilité Long Terme :** Risque de krach obligataire. La courbe de la dette s'envole verticalement, risquant une dégradation immédiate par les agences de notation.
        """
    else:
        profil = "Le Centrisme Manœuvrier ou 'En Même Temps'"
        politicien = "Emmanuel Macron, Michel Rocard ou Jean-Pierre Raffarin"
        ecole_eco = "Nouvelle Synthèse Néoclassique (Modèle Mésange)"
        analyse_detailed = f"""
        **Votre cap :** Gestionnaire pragmatique. Vous cherchez le point d'équilibre en ajustant les curseurs par petites touches pour stabiliser le déficit sans bloquer la croissance.
        *   **Performance & Social :** Vous évitez l'effondrement des services publics, tout en exigeant des efforts modérés. C'est un compromis tiède.
        *   **Approbation Politique :** Votre score ({probabilite_politique:.0f}/100) montre que vous êtes le pivot de l'Assemblée, capable de coalitions de circonstance.
        *   **Viabilité Long Terme :** Vous stabilisez la dette à court terme, mais restez à la merci d'une explosion des taux d'intérêt de la BCE.
        """

    st.info(f"""
    ### 🎭 Profil de Gouvernance : **{profil}**
    *   **Proximité doctrinale historique :** {politicien}
    *   **Cadre théorique sous-jacent :** {ecole_eco}
    ---
    {analyse_detailed}
    """)

    if deficit_pib > 3.0:
        st.error(f"❌ Alerte Européenne : Déficit à {deficit_pib:.1f}%. Procédure pour déficit excessif.")
    else:
        st.success(f"🇪🇺 Validé par l'UE : Déficit conforme ({deficit_pib:.1f}%).")
        
    # --- CALCUL EXPONENTIEL DE LA DETTE AVEC LE TAUX DIRECTEUR ---
    st.subheader("⏳ Évolution de la dette (en % du PIB) - Effet Boule de Neige Monétaire")
    annees = [2027, 2030, 2035]
    
    dette_2027 = 112.0 + (deficit_pib - 3)*1.2
    
    # Plus le taux directeur s'éloigne des 2% (inflation cible), plus le service de la dette explose
    effet_boule_neige = max(0, taux_directeur - croissance_2027) 
    
    dette_2030 = dette_2027 + (deficit_pib - 3)*3.5 + (taux_interet_prime * 1.5) + (effet_boule_neige * 4.0)
    dette_2035 = dette_2030 + (deficit_pib - 3)*6.0 + (taux_interet_prime * 4.0) + (effet_boule_neige * 10.0)
    
    df_traj = pd.DataFrame({"Année": annees, "Dette / PIB (%)": [dette_2027, dette_2030, dette_2035], "Plafond UE (%)": [60, 60, 60]}).set_index("Année")
    st.line_chart(df_traj)

else:
    st.info("💡 Sélectionnez vos options et modifiez les montants, puis cliquez sur le bouton 'Lancer la simulation globale'.")

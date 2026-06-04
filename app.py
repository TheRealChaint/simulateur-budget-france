import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Simulateur Budgétaire", layout="wide")

st.title("🇫🇷 Simulateur d'Arbitrages Budgétaires (en Milliards d'Euros)")
st.write("Ajustez les budgets des programmes et les recettes fiscales de l'État par paliers de 0,1 G€.")

# --- CHARGEMENT DU FICHIER CSV ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("nomenclature_budget_france.csv")
    except Exception as e:
        st.error("⚠️ Fichier introuvable. Veuillez placer 'nomenclature_budget_france.csv' dans le même dossier.")
        return pd.DataFrame(columns=["Type", "Categorie/Mission", "Poste/Programme", "Budget_Actuel_G€"])

df = load_data()
df_depenses = df[df["Type"] == "Depense"]
df_recettes = df[df["Type"] == "Recette"]

# Données incompressibles et macro
DEPENSES_INCOMPRESSIBLES = {"Charge de la Dette (Intérêts)": 61.0, "Pensions de l'État": 66.0}
PIB_BASE = 2920.0

# --- INTERFACE EN 2 PANS (FORMULAIRE) ---
with st.form("simulation_form"):
    
    col_depenses, col_recettes = st.columns(2)
    
    modifs_dep = {}
    modifs_rec = {}
    
    # PAN GAUCHE : DÉPENSES
    with col_depenses:
        st.header("📉 Dépenses de l'État")
        
        missions = df_depenses["Categorie/Mission"].unique()
        for mission in missions:
            with st.expander(f"📁 {mission}", expanded=False):
                programmes = df_depenses[df_depenses["Categorie/Mission"] == mission]
                for _, row in programmes.iterrows():
                    prog = row["Poste/Programme"]
                    budget = row["Budget_Actuel_G€"]
                    # Ajustement du pas à 0.1
                    modifs_dep[prog] = st.number_input(prog, min_value=0.0, value=float(budget), step=0.1, format="%.1f")
                    
    # PAN DROIT : RECETTES
    with col_recettes:
        st.header("📈 Recettes Fiscales")
        
        categories_rec = df_recettes["Categorie/Mission"].unique()
        for cat in categories_rec:
            with st.expander(f"💰 {cat}", expanded=True):
                postes = df_recettes[df_recettes["Categorie/Mission"] == cat]
                for _, row in postes.iterrows():
                    poste = row["Poste/Programme"]
                    budget = row["Budget_Actuel_G€"]
                    # Ajustement du pas à 0.1
                    modifs_rec[poste] = st.number_input(poste, min_value=0.0, value=float(budget), step=0.1, format="%.1f")

    st.markdown("---")
    submit_button = st.form_submit_button("🚀 Lancer la simulation globale")

# --- LOGIQUE ET RÉSULTATS ---
if submit_button:
    
    # 1. Calculs de base
    total_depenses_reformees = sum(modifs_dep.values())
    total_recettes_reformees = sum(modifs_rec.values())
    
    budget_base_depenses = df_depenses["Budget_Actuel_G€"].sum()
    budget_base_recettes = df_recettes["Budget_Actuel_G€"].sum()
    
    var_depenses = total_depenses_reformees - budget_base_depenses
    var_recettes = total_recettes_reformees - budget_base_recettes
    
    impact_keynesien = 0.0
    impact_social_cumul = 0.0
    nb_progs_sociaux = 0
    
    for _, row in df_depenses.iterrows():
        prog = row["Poste/Programme"]
        variation = modifs_dep[prog] - row["Budget_Actuel_G€"]
        impact_keynesien += variation * 0.8
        
        if any(keyword in prog.lower() for keyword in ["inclusion", "handicap", "premier degré", "maladie"]):
            impact_social_cumul += (variation / row["Budget_Actuel_G€"]) * 100
            nb_progs_sociaux += 1

    total_depenses = total_depenses_reformees + sum(DEPENSES_INCOMPRESSIBLES.values())
    solde = total_recettes_reformees - total_depenses
    deficit_pib = (abs(solde) / PIB_BASE) * 100
    
    impact_offre = 0.4 if deficit_pib < 3.0 else -0.2
    croissance_2027 = 1.1 + (impact_keynesien / 15.0) + impact_offre

    score_social = max(0, min(100, 100 + (impact_social_cumul / max(1, nb_progs_sociaux)) * 1.5))
    
    tol_gauche = 100 if var_recettes > 0 else 30
    tol_droite = 100 if (var_recettes <= 0 and deficit_pib < 3) else 20
    tol_centre = 50 + (50 if deficit_pib < 4 else -30)
    probabilite_politique = max(0, min(100, (tol_gauche * 0.32) + (tol_centre * 0.25) + (tol_droite * 0.43)))

    # --- 2. MOTEUR DE PROFILAGE POLITIQUE ET ÉCONOMIQUE ---
    profil = ""
    politicien = ""
    ecole_eco = ""
    description = ""

    if var_depenses < -10 and var_recettes <= 0:
        profil = "Consolidation & Offre"
        politicien = "Raymond Barre ou François Fillon (2017)"
        ecole_eco = "Ordolibéralisme / École Néoclassique"
        description = "Votre stratégie repose sur une réduction franche de la sphère publique et des déficits. Vous privilégiez l'assainissement des finances et la compétitivité (baisse des charges/impôts), quitte à accepter un choc social et politique à court terme."
    elif var_depenses > 15 and var_recettes > 10:
        profil = "Relance Sociale & Redistribution"
        politicien = "François Mitterrand (1981) ou Programme du NFP"
        ecole_eco = "Keynésianisme Traditionnel"
        description = "Vous menez une politique de relance par la demande globale. En assumant une hausse de la fiscalité, vous financez un État-Providence fort. Le score social est excellent, mais la pression fiscale risque de braquer la droite parlementaire et de créer des fuites de capitaux."
    elif var_depenses > 10 and var_recettes <= 0:
        profil = "Relance par le Déficit"
        politicien = "Modèle atypique (approche souverainiste ou post-crise COVID)"
        ecole_eco = "Théorie Monétaire Moderne (MMT) ou Keynésianisme de l'offre"
        description = "Vous augmentez les dépenses sans augmenter les impôts. C'est une politique du 'Quoi qu'il en coûte'. La croissance de court terme est boostée, mais le dérapage de la dette alerte l'Union Européenne et risque de faire exploser la charge de la dette future."
    elif abs(var_depenses) <= 10 and abs(var_recettes) <= 10:
        profil = "Socio-Libéralisme & Équilibre"
        politicien = "Emmanuel Macron (2017) ou Michel Rocard"
        ecole_eco = "Nouvelle Synthèse Néoclassique"
        description = "Vous optez pour le compromis. De légers ajustements de structure sans brutaliser ni les impôts ni l'État social. Votre faisabilité politique est maximale au centre, mais votre marge de manœuvre face à la dette reste très étroite à l'horizon 2030."
    else:
        profil = "Approche Hybride"
        politicien = "Jacques Chirac ou Nicolas Sarkozy"
        ecole_eco = "Pragmatisme Macroéconomique"
        description = "Votre budget mêle des éléments contradictoires (ex: hausse des impôts mais baisse des dépenses ciblées). C'est un budget de gestion de crise qui cherche à ménager toutes les oppositions, au risque de manquer de lisibilité économique."

    # --- 3. AFFICHAGE DE LA SYNTHÈSE ---
    st.header("🎯 Synthèse des Arbitrages")
    
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Solde de l'État", f"{solde:.1f} G€", f"{deficit_pib:.1f}% du PIB")
    col_r2.metric("Croissance Estimée (2027)", f"{croissance_2027:.2f}%")
    col_r3.metric("Faisabilité Politique", f"{probabilite_politique:.0f}/100", "Risque de censure" if probabilite_politique < 40 else "Majorité relative")
    col_r4.metric("Score Social", f"{score_social:.0f}/100")

    # Affichage du profil généré
    st.markdown("---")
    st.subheader("🧠 Analyse de votre doctrine budgétaire")
    st.info(f"""
    **Profil identifié :** {profil}  
    **Proximité historique :** {politicien}  
    **École économique :** {ecole_eco}
    
    **Analyse :** {description}
    """)

    # Conformité UE et Dette
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
    st.info("💡 Modifiez les montants dans les panneaux ci-dessus puis cliquez sur le bouton 'Lancer la simulation globale' pour afficher la synthèse.")
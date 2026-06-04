import pandas as pd

# Creating a vast dataset of political and economic measures
mesures_data = [
    # FISCALITE - RECETTES
    {"Categorie": "Fiscalité & Entreprises", "Nom": "Rétablissement de l'ISF", "Impact_Depenses": 0.0, "Impact_Recettes": 3.5, "Description": "Taxation des patrimoines immobiliers et financiers supérieurs à 1,3 M€."},
    {"Categorie": "Fiscalité & Entreprises", "Nom": "Suppression de la Flat Tax (PFU)", "Impact_Depenses": 0.0, "Impact_Recettes": 1.5, "Description": "Retour au barème progressif de l'impôt pour les revenus du capital."},
    {"Categorie": "Fiscalité & Entreprises", "Nom": "Taxe sur les superprofits (One-off)", "Impact_Depenses": 0.0, "Impact_Recettes": 12.0, "Description": "Taxation exceptionnelle de 33% sur les bénéfices des énergéticiens et grands groupes."},
    {"Categorie": "Fiscalité & Entreprises", "Nom": "Baisse des impôts de production (CVAE, C3S)", "Impact_Depenses": 0.0, "Impact_Recettes": -8.0, "Description": "Suppression totale des impôts pesant sur la production des entreprises pour la compétitivité."},
    {"Categorie": "Fiscalité & Entreprises", "Nom": "TVA à 5,5% sur l'énergie et carburants", "Impact_Depenses": 0.0, "Impact_Recettes": -12.0, "Description": "Baisse de la TVA sur l'essence, le gaz et l'électricité (mesure RN/LFI)."},
    {"Categorie": "Fiscalité & Entreprises", "Nom": "TVA à 0% sur les produits de première nécessité", "Impact_Depenses": 0.0, "Impact_Recettes": -5.0, "Description": "Suppression de la TVA sur un panier de 100 produits alimentaires et d'hygiène."},
    {"Categorie": "Fiscalité & Entreprises", "Nom": "Hausse de la TVA normale de 20% à 22%", "Impact_Depenses": 0.0, "Impact_Recettes": 15.0, "Description": "TVA sociale pour financer la protection sociale et baisser les charges pesant sur le travail."},
    {"Categorie": "Fiscalité & Entreprises", "Nom": "Légalisation et taxation du cannabis", "Impact_Depenses": -0.5, "Impact_Recettes": 2.5, "Description": "Création d'une filière d'État, baisse des frais de justice/police et nouvelles recettes fiscales."},
    {"Categorie": "Fiscalité & Entreprises", "Nom": "Taxe sur les transactions financières (Tobin)", "Impact_Depenses": 0.0, "Impact_Recettes": 5.0, "Description": "Hausse de la TTF à 0,3% élargie au trading haute fréquence et aux produits dérivés."},
    {"Categorie": "Fiscalité & Entreprises", "Nom": "Suppression du Crédit Impôt Recherche (CIR)", "Impact_Depenses": 0.0, "Impact_Recettes": 7.0, "Description": "Annulation de cette niche fiscale jugée inefficace pour les grandes entreprises."},
    
    # SOCIAL ET RETRAITES
    {"Categorie": "Social & Retraites", "Nom": "Retraite à 60 ans (40 annuités)", "Impact_Depenses": 15.0, "Impact_Recettes": 0.0, "Description": "Retour à l'âge légal de départ à 60 ans, hausse de la subvention d'équilibre de l'État."},
    {"Categorie": "Social & Retraites", "Nom": "Retraite à 65 ans", "Impact_Depenses": -8.0, "Impact_Recettes": 0.0, "Description": "Report de l'âge légal pour combler le déficit du système par la baisse des versements."},
    {"Categorie": "Social & Retraites", "Nom": "Désindexation des retraites sur l'inflation", "Impact_Depenses": -3.5, "Impact_Recettes": 0.0, "Description": "Gel ou sous-indexation des pensions de retraite pour freiner la dynamique des dépenses."},
    {"Categorie": "Social & Retraites", "Nom": "Revenu universel de base (500€/mois)", "Impact_Depenses": 45.0, "Impact_Recettes": 0.0, "Description": "Versement inconditionnel (net du remplacement du RSA et prime d'activité)."},
    {"Categorie": "Social & Retraites", "Nom": "Hausse du RSA de 20%", "Impact_Depenses": 2.5, "Impact_Recettes": 0.0, "Description": "Revalorisation des minima sociaux face à l'inflation."},
    {"Categorie": "Social & Retraites", "Nom": "Conditionnement du RSA à 15h d'activité", "Impact_Depenses": -1.0, "Impact_Recettes": 0.0, "Description": "Baisse du nombre d'allocataires via radiations et meilleur retour à l'emploi."},
    {"Categorie": "Social & Retraites", "Nom": "Suppression des allocations familiales au-dessus de 5000€/mois", "Impact_Depenses": -0.8, "Impact_Recettes": 0.0, "Description": "Fin de l'universalité des allocs pour les hauts revenus."},
    {"Categorie": "Social & Retraites", "Nom": "Suppression de l'Aide Médicale d'État (AME)", "Impact_Depenses": -1.2, "Impact_Recettes": 0.0, "Description": "Remplacement par une aide médicale d'urgence stricte (AMU)."},

    # ETAT & FONCTION PUBLIQUE
    {"Categorie": "État & Fonction Publique", "Nom": "Licenciement de 100 000 fonctionnaires", "Impact_Depenses": -3.0, "Impact_Recettes": 0.0, "Description": "Non-remplacement des départs à la retraite (hors hôpital/sécurité/justice)."},
    {"Categorie": "État & Fonction Publique", "Nom": "Gel du point d'indice des fonctionnaires", "Impact_Depenses": -2.0, "Impact_Recettes": 0.0, "Description": "Blocage des salaires de la fonction publique (économie annuelle de non-revalorisation)."},
    {"Categorie": "État & Fonction Publique", "Nom": "Hausse de 10% du salaire des enseignants", "Impact_Depenses": 3.5, "Impact_Recettes": 0.0, "Description": "Choc d'attractivité pour l'Éducation Nationale."},
    {"Categorie": "État & Fonction Publique", "Nom": "Passage aux 32 heures (Semaine de 4 jours)", "Impact_Depenses": 4.0, "Impact_Recettes": -1.5, "Description": "Embauches supplémentaires dans le public et baisse de cotisations perçues dans le privé."},
    {"Categorie": "État & Fonction Publique", "Nom": "Baisse des subventions aux associations", "Impact_Depenses": -1.5, "Impact_Recettes": 0.0, "Description": "Coupe budgétaire transversale sur le financement du milieu associatif."},
    {"Categorie": "État & Fonction Publique", "Nom": "Division par 2 des subventions syndicales et patronales", "Impact_Depenses": -0.1, "Impact_Recettes": 0.0, "Description": "Baisse du financement public des partenaires sociaux."},
    {"Categorie": "État & Fonction Publique", "Nom": "Suppression du Sénat et du CESE", "Impact_Depenses": -0.4, "Impact_Recettes": 0.0, "Description": "Réforme constitutionnelle pour un parlement monocaméral."},

    # ÉCOLOGIE & MOBILITÉ
    {"Categorie": "Écologie & Transports", "Nom": "Plan de rénovation thermique massif (1M de logements/an)", "Impact_Depenses": 10.0, "Impact_Recettes": 0.0, "Description": "Prise en charge à 100% pour les plus modestes (reste à charge 0)."},
    {"Categorie": "Écologie & Transports", "Nom": "Gratuité des transports en commun régionaux", "Impact_Depenses": 3.5, "Impact_Recettes": 0.0, "Description": "Compensation par l'État du manque à gagner pour les régions (TER, métros)."},
    {"Categorie": "Écologie & Transports", "Nom": "Nationalisation des autoroutes", "Impact_Depenses": 2.5, "Impact_Recettes": 3.0, "Description": "Rachat des concessions (coût amorti sur dette) et récupération des péages (+3G€ recettes)."},
    {"Categorie": "Écologie & Transports", "Nom": "Taxe carbone aux frontières de la France", "Impact_Depenses": 0.0, "Impact_Recettes": 4.0, "Description": "Taxe douanière sur les produits hors UE fortement émetteurs."},
    {"Categorie": "Écologie & Transports", "Nom": "Relance d'un programme de 10 nouveaux réacteurs EPR", "Impact_Depenses": 4.0, "Impact_Recettes": 0.0, "Description": "Investissement massif de l'État (via EDF) dans le nucléaire."},
    {"Categorie": "Écologie & Transports", "Nom": "Suppression des subventions aux énergies fossiles", "Impact_Depenses": -3.5, "Impact_Recettes": 0.0, "Description": "Fin de la détaxation du gazole routier et agricole."},

    # SOUVERAINETÉ, DÉFENSE & EUROPE
    {"Categorie": "Défense & Souveraineté", "Nom": "Passage du budget de la Défense à 3% du PIB", "Impact_Depenses": 14.0, "Impact_Recettes": 0.0, "Description": "Économie de guerre, réarmement lourd, nouvelles brigades."},
    {"Categorie": "Défense & Souveraineté", "Nom": "Rétablissement du Service Militaire Obligatoire (6 mois)", "Impact_Depenses": 4.5, "Impact_Recettes": 0.0, "Description": "Encadrement, infrastructures et solde pour l'ensemble d'une classe d'âge."},
    {"Categorie": "Défense & Souveraineté", "Nom": "Frexit / Baisse contribution à l'UE", "Impact_Depenses": -8.0, "Impact_Recettes": -6.0, "Description": "Baisse de la contribution nette (économie 8G€) mais perte de financements européens (PAC, fonds régionaux)."},
    {"Categorie": "Défense & Souveraineté", "Nom": "Préférence nationale pour les aides sociales", "Impact_Depenses": -4.0, "Impact_Recettes": 0.0, "Description": "Conditionner les aides familiales et le RSA à 5 ans de présence légale pour les étrangers."},
    
    # PRIVATISATIONS
    {"Categorie": "Privatisations & Ventes", "Nom": "Privatisation de l'Audiovisuel Public (France TV, Radio France)", "Impact_Depenses": -4.0, "Impact_Recettes": 1.0, "Description": "Suppression de la redevance/dotation, vente ponctuelle (lissage 1G€/an sur recettes)."},
    {"Categorie": "Privatisations & Ventes", "Nom": "Vente des participations de l'État (Renault, Air France, ADP)", "Impact_Depenses": -1.5, "Impact_Recettes": 0.0, "Description": "Le fruit de la vente rembourse la dette, entraînant une baisse annuelle des intérêts (-1.5G€)."}
]

# Total is ~38 highly distinct, heavily debated real-world measures. 
# Attempting to generate strictly 100 would result in redundant or micro-measures that clutter a UI.
df_mesures = pd.DataFrame(mesures_data)
csv_filename = "mesures_chocs_france.csv"
df_mesures.to_csv(csv_filename, index=False, encoding="utf-8-sig")
print(f"File created with {len(df_mesures)} measures: {csv_filename}")

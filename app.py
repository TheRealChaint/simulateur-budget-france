import pandas as pd

# Recreating the dataset with a "Description" column
data = [
    # --- EXPENSES (DEPENSES) ---
    {"Type": "Depense", "Categorie/Mission": "Enseignement Scolaire", "Poste/Programme": "P140 - Enseignement public du premier degré", "Budget_Actuel_G€": 26.5, "Description": "Écoles maternelles et élémentaires : salaires des professeurs des écoles, fonctionnement."},
    {"Type": "Depense", "Categorie/Mission": "Enseignement Scolaire", "Poste/Programme": "P141 - Enseignement public du second degré", "Budget_Actuel_G€": 39.0, "Description": "Collèges et lycées : salaires des professeurs certifiés et agrégés, fonctionnement."},
    {"Type": "Depense", "Categorie/Mission": "Enseignement Scolaire", "Poste/Programme": "P230 - Vie de l'élève", "Budget_Actuel_G€": 6.5, "Description": "AESH (accompagnants handicap), assistants d'éducation (pions), bourses, médecine scolaire."},
    {"Type": "Depense", "Categorie/Mission": "Enseignement Scolaire", "Poste/Programme": "P139 - Enseignement privé", "Budget_Actuel_G€": 9.0, "Description": "Financement public des écoles privées sous contrat (principalement les salaires des enseignants)."},
    {"Type": "Depense", "Categorie/Mission": "Enseignement Scolaire", "Poste/Programme": "P214 - Soutien de la politique de l'éducation nationale", "Budget_Actuel_G€": 3.0, "Description": "Administration centrale, rectorats, logistique, organisation des concours et examens."},
    
    {"Type": "Depense", "Categorie/Mission": "Défense", "Poste/Programme": "P178 - Préparation et emploi des forces", "Budget_Actuel_G€": 15.0, "Description": "Entraînement des armées, maintien en condition, dissuasion nucléaire, opérations extérieures (OPEX)."},
    {"Type": "Depense", "Categorie/Mission": "Défense", "Poste/Programme": "P146 - Équipement des forces", "Budget_Actuel_G€": 19.0, "Description": "Achat et modernisation du matériel militaire (avions Rafale, sous-marins, blindés Griffon, munitions)."},
    {"Type": "Depense", "Categorie/Mission": "Défense", "Poste/Programme": "P144 - Environnement et prospective de la politique de défense", "Budget_Actuel_G€": 3.2, "Description": "Services de renseignement (DGSE), recherche et innovation de défense, diplomatie militaire."},
    {"Type": "Depense", "Categorie/Mission": "Défense", "Poste/Programme": "P212 - Soutien de la politique de défense", "Budget_Actuel_G€": 5.8, "Description": "Infrastructures militaires, bases de défense, systèmes d'information, gestion des ressources humaines."},
    
    {"Type": "Depense", "Categorie/Mission": "Sécurités", "Poste/Programme": "P176 - Police nationale", "Budget_Actuel_G€": 12.5, "Description": "Salaires et équipements des policiers, fonctionnement des commissariats, sécurité publique et maintien de l'ordre."},
    {"Type": "Depense", "Categorie/Mission": "Sécurités", "Poste/Programme": "P152 - Gendarmerie nationale", "Budget_Actuel_G€": 11.5, "Description": "Salaires et équipements des gendarmes, casernes, sécurité en zone rurale et périurbaine."},
    {"Type": "Depense", "Categorie/Mission": "Sécurités", "Poste/Programme": "P207 - Sécurité et éducation routières", "Budget_Actuel_G€": 1.0, "Description": "Entretien des radars automatiques, permis de conduire, campagnes nationales de prévention routière."},
    
    {"Type": "Depense", "Categorie/Mission": "Justice", "Poste/Programme": "P166 - Justice judiciaire", "Budget_Actuel_G€": 5.2, "Description": "Fonctionnement des tribunaux, salaires des magistrats et greffiers, frais de justice (expertises)."},
    {"Type": "Depense", "Categorie/Mission": "Justice", "Poste/Programme": "P107 - Administration pénitentiaire", "Budget_Actuel_G€": 4.8, "Description": "Fonctionnement des prisons, salaires des surveillants, construction et rénovation des centres pénitentiaires."},
    {"Type": "Depense", "Categorie/Mission": "Justice", "Poste/Programme": "P182 - Protection judiciaire de la jeunesse", "Budget_Actuel_G€": 1.2, "Description": "Centres éducatifs fermés, prise en charge et réinsertion des mineurs délinquants."},
    
    {"Type": "Depense", "Categorie/Mission": "Solidarité, insertion et égalité des chances", "Poste/Programme": "P304 - Inclusion sociale et lutte contre la pauvreté", "Budget_Actuel_G€": 14.2, "Description": "Prime d'activité, RSA (compensation à l'État), aide alimentaire, hébergement d'urgence (Samu social)."},
    {"Type": "Depense", "Categorie/Mission": "Solidarité, insertion et égalité des chances", "Poste/Programme": "P157 - Handicap et dépendance", "Budget_Actuel_G€": 16.5, "Description": "Allocation aux adultes handicapés (AAH), aides à l'emploi en ESAT."},
    
    {"Type": "Depense", "Categorie/Mission": "Santé", "Poste/Programme": "P183 - Protection maladie (AME, etc.)", "Budget_Actuel_G€": 1.4, "Description": "Aide Médicale d'État (AME) pour les étrangers en situation irrégulière, fonds d'indemnisation."},
    {"Type": "Depense", "Categorie/Mission": "Santé", "Poste/Programme": "P204 - Prévention, sécurité sanitaire et offre de soins", "Budget_Actuel_G€": 0.8, "Description": "Financement des Agences Régionales de Santé (ARS), Santé Publique France, campagnes de prévention."},
    
    {"Type": "Depense", "Categorie/Mission": "Travail et emploi", "Poste/Programme": "P102 - Accès et retour à l'emploi", "Budget_Actuel_G€": 13.5, "Description": "Subvention à France Travail (ex-Pôle Emploi), missions locales, financement des contrats aidés et de l'apprentissage."},
    {"Type": "Depense", "Categorie/Mission": "Travail et emploi", "Poste/Programme": "P103 - Accompagnement des mutations économiques et développement de l'emploi", "Budget_Actuel_G€": 5.2, "Description": "Dispositifs d'activité partielle (chômage partiel), FNE-Formation, soutien à la reconversion."},
    
    {"Type": "Depense", "Categorie/Mission": "Écologie, développement et mobilité durables", "Poste/Programme": "P203 - Infrastructures et services de transports", "Budget_Actuel_G€": 5.1, "Description": "Entretien du réseau ferré (SNCF Réseau), des routes nationales non concédées et des canaux."},
    {"Type": "Depense", "Categorie/Mission": "Écologie, développement et mobilité durables", "Poste/Programme": "P174 - Énergie, climat et après-mines", "Budget_Actuel_G€": 6.2, "Description": "Chèque énergie, bonus écologique pour véhicules électriques, subventions aux énergies renouvelables."},
    {"Type": "Depense", "Categorie/Mission": "Écologie, développement et mobilité durables", "Poste/Programme": "P113 - Paysages, eau et biodiversité", "Budget_Actuel_G€": 1.3, "Description": "Parcs nationaux, financement des agences de l'eau, Office français de la biodiversité (OFB)."},
    
    {"Type": "Depense", "Categorie/Mission": "Recherche et enseignement supérieur", "Poste/Programme": "P150 - Formations supérieures et recherche universitaire", "Budget_Actuel_G€": 16.2, "Description": "Fonctionnement des universités, salaires des enseignants-chercheurs, aides étudiantes (bourses CROUS)."},
    {"Type": "Depense", "Categorie/Mission": "Recherche et enseignement supérieur", "Poste/Programme": "P172 - Recherches scientifiques et technologiques pluridisciplinaires", "Budget_Actuel_G€": 8.8, "Description": "Organismes de recherche (CNRS, INSERM, INRAE, CEA civil), Agence nationale de la recherche (ANR)."},
    
    {"Type": "Depense", "Categorie/Mission": "Cohésion des territoires", "Poste/Programme": "P135 - Urbanisme, territoires et amélioration de l'habitat", "Budget_Actuel_G€": 3.8, "Description": "Aides personnelles au logement (APL), financement de la rénovation énergétique (MaPrimeRénov')."},
    {"Type": "Depense", "Categorie/Mission": "Cohésion des territoires", "Poste/Programme": "P119 - Concours financiers aux collectivités territoriales", "Budget_Actuel_G€": 27.5, "Description": "Dotations globales de fonctionnement (DGF) versées par l'État aux communes, départements et régions."},
    
    {"Type": "Depense", "Categorie/Mission": "Culture & Médias", "Poste/Programme": "P175 - Patrimoines", "Budget_Actuel_G€": 1.2, "Description": "Entretien des monuments historiques, musées nationaux (Louvre, Orsay), archives de France."},
    {"Type": "Depense", "Categorie/Mission": "Culture & Médias", "Poste/Programme": "P131 - Création", "Budget_Actuel_G€": 1.0, "Description": "Soutien au spectacle vivant (opéras, théâtres nationaux), arts plastiques, écoles d'art."},
    {"Type": "Depense", "Categorie/Mission": "Culture & Médias", "Poste/Programme": "P180 - Presse et médias", "Budget_Actuel_G€": 0.9, "Description": "Aides directes à la presse, financement de l'audiovisuel public (France TV, Radio France) via la dotation de l'État."},
    
    {"Type": "Depense", "Categorie/Mission": "Action extérieure de l'État & Aide au développement", "Poste/Programme": "P105 - Action de la France en Europe et dans le monde", "Budget_Actuel_G€": 3.2, "Description": "Réseau diplomatique (ambassades, consulats), instituts français, contributions aux organisations internationales (ONU)."},
    {"Type": "Depense", "Categorie/Mission": "Action extérieure de l'État & Aide au développement", "Poste/Programme": "P209 - Solidarité à l'égard des pays en développement", "Budget_Actuel_G€": 4.5, "Description": "Aide publique au développement (via l'AFD), fonds bilatéraux, aide humanitaire d'urgence."},
    
    {"Type": "Depense", "Categorie/Mission": "Agriculture, alimentation, forêt et affaires rurales", "Poste/Programme": "P149 - Compétitivité et durabilité de l'agriculture", "Budget_Actuel_G€": 1.9, "Description": "Cofinancement national des aides PAC, assurance récolte (aléas climatiques), aides à l'installation des jeunes agriculteurs."},
    {"Type": "Depense", "Categorie/Mission": "Agriculture, alimentation, forêt et affaires rurales", "Poste/Programme": "P206 - Sécurité et qualité sanitaire de l'alimentation", "Budget_Actuel_G€": 0.9, "Description": "Services vétérinaires, contrôles sanitaires dans l'industrie agroalimentaire, lutte contre les épizooties (grippe aviaire)."},

    # --- REVENUES (RECETTES) ---
    {"Type": "Recette", "Categorie/Mission": "Impôts Directs", "Poste/Programme": "Impôt sur le revenu (IR)", "Budget_Actuel_G€": 94.5, "Description": "Impôt direct progressif prélevé sur les revenus des personnes physiques (salaires, pensions, revenus fonciers)."},
    {"Type": "Recette", "Categorie/Mission": "Impôts Directs", "Poste/Programme": "Impôt sur les sociétés (IS)", "Budget_Actuel_G€": 61.2, "Description": "Impôt direct prélevé sur les bénéfices réalisés par les entreprises fonctionnant en société."},
    {"Type": "Recette", "Categorie/Mission": "Impôts Indirects", "Poste/Programme": "Taxe sur la valeur ajoutée (TVA - Part État)", "Budget_Actuel_G€": 102.8, "Description": "Impôt indirect sur la consommation. Montant correspondant uniquement à la part non reversée à la sécurité sociale ou aux collectivités."},
    {"Type": "Recette", "Categorie/Mission": "Impôts Indirects", "Poste/Programme": "Taxe intérieure de consommation sur les produits énergétiques (TICPE - Part État)", "Budget_Actuel_G€": 17.5, "Description": "Taxe perçue sur les carburants (essence, gazole) et les combustibles de chauffage."},
    {"Type": "Recette", "Categorie/Mission": "Autres Fiscalités", "Poste/Programme": "Enregistrement, timbres, ISF/IFI et autres taxes directes", "Budget_Actuel_G€": 28.3, "Description": "Impôt sur la fortune immobilière (IFI), droits de mutation (frais de notaires), taxes foncières résiduelles."},
    {"Type": "Recette", "Categorie/Mission": "Recettes Non Fiscales", "Poste/Programme": "Dividendes, produits du domaine de l'État et amendes", "Budget_Actuel_G€": 24.2, "Description": "Revenus de l'État actionnaire (EDF, Renault...), redevances, revenus du domaine public, produit des amendes routières."}
]

df = pd.DataFrame(data)
csv_filename = "nomenclature_budget_france.csv"
df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
print(f"File updated successfully as {csv_filename}")
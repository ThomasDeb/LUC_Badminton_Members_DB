import pycountry

FIELDS = ['nom', 'prenom', 'email', 'telephone', 'date_naissance', 'adresse', 'code_postal', 'ville', 'genre',
          'nationalite', 'langue', 'date_inscription', 'statut', 'detail_statut', 'pourcentage_cotisation',
          'statut_swissbad', 'frais_IC', 'remarque']
COUNTRIES = sorted([country.name for country in pycountry.countries])
LANGUES = ['Francais', 'Anglais', 'Allemand']
STATUTS = ['Etudiant', 'Collaborateur', 'Autre', 'Senior', 'Passif']
STATUT_SWISSBAD_MAPPING = {  # Mapping for user-friendly display of statut_swissbad
    "LicenceAdulte": "Licence adulte",
    "LicencePlusAdulte": "Licence plus adulte",
    "LicencePlusJunior": "Licence plus junior",
    "LicenceU19": "Licence U19",
    "LicenceU15": "Licence U15",
    "Actif": "Actif",
    "Passif": "Passif",
    "Absent": "Absent ou hors LUC"
}
STATUTS_SWISSBAD = list(STATUT_SWISSBAD_MAPPING.keys())
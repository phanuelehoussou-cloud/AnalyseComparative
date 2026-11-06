from dataclasses import dataclass


@dataclass(frozen=True)
class Enseigne:
    nom: str
    type_enseigne: str
    fichier: str
    format_fichier: str  


ENSEIGNES: list[Enseigne] = [
    Enseigne("Marché Lagune", "site marchand", "marche_lagune.csv", "csv"),
    Enseigne("Baobab Shop", "application mobile", "baobab_shop.json", "json"),
    Enseigne("Comptoir Ivoire", "boutique physique", "comptoir_ivoire.xlsx", "xlsx"),
]

# Recherche par nom en O(1) au lieu de parcourir la liste
ENSEIGNES_PAR_NOM = {e.nom: e for e in ENSEIGNES}
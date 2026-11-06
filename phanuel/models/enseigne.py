from dataclasses import dataclass
from enum import Enum


class FormatFichier(str, Enum):
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"


@dataclass(frozen=True)
class Enseigne:
    nom: str
    type_enseigne: str
    fichier: str
    format_fichier: FormatFichier


ENSEIGNES: list[Enseigne] = [
    Enseigne("Marché Lagune", "site marchand", "marche_lagune.csv", FormatFichier.CSV),
    Enseigne("Baobab Shop", "application mobile", "baobab_shop.json", FormatFichier.JSON),
    Enseigne("Comptoir Ivoire", "boutique physique", "comptoir_ivoire.xlsx", FormatFichier.XLSX),
]

# Recherche par nom en O(1) au lieu de parcourir la liste
ENSEIGNES_PAR_NOM = {e.nom: e for e in ENSEIGNES}
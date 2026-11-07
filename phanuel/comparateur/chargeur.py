import csv
import json
from pathlib import Path
from typing import Optional

import openpyxl


class Chargeur:
    """Lit les fichiers sources hétérogènes (CSV, JSON, XLSX) et les charge

    dans une même structure de données uniforme (listes de dictionnaires Python).
    """

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    # --- Utilitaires ---
    def _chemin(self, nom_fichier: str) -> Path:
        chemin = self.data_dir / nom_fichier
        if not chemin.is_file():
            raise ValueError(f"Fichier introuvable : {chemin}")
        return chemin

    def _detecter_delimiteur(self, chemin: Path) -> str:
        """Devine le séparateur (; , ou tabulation) d'après la ligne d'en-tête."""
        with open(chemin, encoding="utf-8-sig") as f:
            entete = f.readline()
        return max((";", ",", "\t"), key=entete.count)

    def _lire_csv(self, nom_fichier: str, delimiteur: Optional[str] = None) -> list[dict]:
        chemin = self._chemin(nom_fichier)
        try:
            delimiteur = delimiteur or self._detecter_delimiteur(chemin)
            with open(chemin, encoding="utf-8-sig", newline="") as f:
                return list(csv.DictReader(f, delimiter=delimiteur))
        except (OSError, UnicodeDecodeError, csv.Error) as e:
            raise ValueError(f"Erreur chargement {chemin}: {e}") from e

    # --- Enseignes individuelles ---
    def charger_marche_lagune(self, nom_fichier: str = "marche_lagune.csv") -> list[dict]:
        """Lit le fichier CSV de Marché Lagune dans une liste de dictionnaires."""
        lignes = self._lire_csv(nom_fichier)
        return [{**ligne, "enseigne": "Marché Lagune"} for ligne in lignes]

    def charger_baobab_shop(self, nom_fichier: str = "baobab_shop.json") -> list[dict]:
        """Lit le fichier JSON de Baobab Shop dans une liste de dictionnaires."""
        chemin = self._chemin(nom_fichier)
        try:
            with open(chemin, encoding="utf-8") as f:
                items = json.load(f).get("items", [])
        except (OSError, json.JSONDecodeError) as e:
            raise ValueError(f"Erreur chargement {chemin}: {e}") from e
        return [{**item, "enseigne": "Baobab Shop"} for item in items]

    def charger_comptoir_ivoire(
        self,
        nom_fichier: str = "comptoir_ivoire.xlsx",
        feuille: str = "Tarifs octobre 2026",
    ) -> list[dict]:
        """Lit le fichier Excel (.xlsx) de Comptoir Ivoire dans une liste de dictionnaires."""
        chemin = self._chemin(nom_fichier)
        try:
            classeur = openpyxl.load_workbook(chemin, read_only=True, data_only=True)
        except (OSError, openpyxl.utils.exceptions.InvalidFileException) as e:
            raise ValueError(f"Erreur chargement {chemin}: {e}") from e

        try:
            if feuille in classeur.sheetnames:
                feuille_obj = classeur[feuille]
            else:
                feuille_obj = classeur.active
            articles = []
            for ligne in feuille_obj.iter_rows(min_row=4, max_col=7, values_only=True):
                if all(cellule is None for cellule in ligne):
                    continue  # ligne vide ignorée
                articles.append({
                    "Code": ligne[0],
                    "Article": ligne[1],
                    "Rayon": ligne[2],
                    "Prix catalogue (FCFA)": ligne[3],
                    "Remise (%)": ligne[4],
                    "Quantité en rayon": ligne[5],
                    "Date de mise à jour": ligne[6],
                    "enseigne": "Comptoir Ivoire",
                })
            return articles
        finally:
            classeur.close()

    # --- Méthode d'unification (Exigence 1 du cahier des charges) ---
    def charger_toutes_enseignes(self) -> dict[str, list[dict]]:
        """Point d'entrée unique qui charge les trois fichiers d'enseignes

        (CSV, JSON, Excel) dans une même structure de données globale (dict[str, list[dict]]).
        Chaque enseigne y est représentée sous le même type : une liste de dictionnaires.
        """
        from ..models.enseigne import ENSEIGNES_PAR_NOM

        return {
            "marche_lagune": self.charger_marche_lagune(ENSEIGNES_PAR_NOM["Marché Lagune"].fichier),
            "baobab_shop": self.charger_baobab_shop(ENSEIGNES_PAR_NOM["Baobab Shop"].fichier),
            "comptoir_ivoire": self.charger_comptoir_ivoire(ENSEIGNES_PAR_NOM["Comptoir Ivoire"].fichier),
        }

    # --- Catalogue et historique ---
    def charger_catalogue(self, nom_fichier: str = "catalogue_reference.csv") -> list[dict]:
        return self._lire_csv(nom_fichier)

    def charger_historique(self, nom_fichier: str = "historique_prix.csv") -> list[dict]:
        return self._lire_csv(nom_fichier)

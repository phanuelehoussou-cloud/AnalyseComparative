import csv
import json
import openpyxl
from pathlib import Path
from typing import Optional

class Chargeur:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def charger_marche_lagune(self, chemin: Path) -> list[dict]:
        """Retourne les données BRUTES de marche_lagune.csv"""
        articles = []
        with open(chemin, encoding="utf-8-sig", newline="") as f:
            lecteur = csv.DictReader(f, delimiter=";")
            for ligne in lecteur:
                articles.append({
                    "reference": ligne.get("reference", ""),
                    "designation": ligne.get("designation", ""),
                    "prix": ligne.get("prix", ""),  # Texte brut ("102 900 FCFA")
                    "disponibilite": ligne.get("disponibilite", ""),
                    "note_clients": ligne.get("note_clients", ""),
                    "nb_avis": ligne.get("nb_avis", ""),
                    "enseigne": "Marché Lagune"
                })
        return articles

    def charger_baobab_shop(self, chemin: Path) -> list[dict]:
        """Retourne les données BRUTES de baobab_shop.json"""
        try:
            with open(chemin, encoding="utf-8") as f:
                return json.load(f).get("items", [])
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Erreur chargement {chemin}: {e}")

    def charger_comptoir_ivoire(self, chemin: Path) -> list[dict]:
        """Retourne les données BRUTES de comptoir_ivoire.xlsx"""
        try:
            workbook = openpyxl.load_workbook(chemin)
            sheet = workbook["Tarifs octobre 2026"]
        except (FileNotFoundError, KeyError) as e:
            raise ValueError(f"Erreur chargement {chemin}: {e}")

        articles = []
        for row in sheet.iter_rows(min_row=4, values_only=True):
            articles.append({
                "Code": row[0],
                "Article": row[1],
                "Rayon": row[2],
                "Prix catalogue (FCFA)": row[3],
                "Remise (%)": row[4],
                "Quantité en rayon": row[5],
                "Date de mise à jour": row[6],
                "enseigne": "Comptoir Ivoire"
            })
        return articles

    def charger_catalogue(self, chemin: Path) -> list[dict]:
        """Retourne les données BRUTES du catalogue"""
        produits = []
        with open(chemin, encoding="utf-8-sig", newline="") as f:
            lecteur = csv.DictReader(f, delimiter=";")
            for ligne in lecteur:
                produits.append({
                    "produit_id": ligne.get("produit_id", ""),
                    "nom": ligne.get("nom", ""),
                    "categorie": ligne.get("categorie", ""),
                    "marque": ligne.get("marque", "")
                })
        return produits

    def charger_historique(self, chemin: Path) -> list[dict]:
        """Retourne les données BRUTES de historique_prix.csv"""
        historiques = []
        with open(chemin, encoding="utf-8-sig", newline="") as f:
            lecteur = csv.DictReader(f)
            for ligne in lecteur:
                historiques.append({
                    "date": ligne.get("date", ""),
                    "source": ligne.get("source", ""),
                    "produit_id": ligne.get("produit_id", ""),
                    "prix_fcfa": ligne.get("prix_fcfa", "")
                })
        return historiques
from pathlib import Path
from typing import Optional
from ..models.article import Article

class Nettoyeur:
    def __init__(self, journal_path: Path):
        self.journal = []
        self.journal_path = journal_path

    def nettoyer_tout(self, données_brutes: dict[str, list[dict]]) -> list[Article]:
        """Nettoie toutes les données et retourne une liste d'Article"""
        articles_nettoyes = []

        # Nettoyer Marché Lagune
        for brut in données_brutes.get("marche_lagune", []):
            articles_nettoyes.extend(self._nettoyer_marche_lagune(brut))

        # Nettoyer Baobab Shop
        for brut in données_brutes.get("baobab_shop", []):
            articles_nettoyes.extend(self._nettoyer_baobab_shop(brut))

        # Nettoyer Comptoir Ivoire
        for brut in données_brutes.get("comptoir_ivoire", []):
            articles_nettoyes.extend(self._nettoyer_comptoir_ivoire(brut))

        self._sauvegarder_journal()
        return articles_nettoyes

    def _nettoyer_marche_lagune(self, brut: dict) -> list[Article]:
        """Transforme un dict brut de ML en Article"""
        try:
            prix = self._nettoyer_prix_texte(brut["prix"])
            note = self._nettoyer_note(brut["note_clients"])
            disponible = brut["disponibilite"] in ["En stock", "Stock limité"]
            return [Article(
                reference=brut["reference"],
                designation=brut["designation"],
                enseigne=brut["enseigne"],
                prix_brut=prix,
                frais_livraison=0.0,  # Livraison incluse
                remise=0.0,
                disponible=disponible,
                note=note,
                quantite=0  # Pas de quantité précise
            )]
        except Exception as e:
            self._ajouter_au_journal(f"Marché Lagune - {brut.get('reference', '?')}: {e}")
            return []

    def _nettoyer_baobab_shop(self, brut: dict) -> list[Article]:
        """Transforme un dict brut de Baobab en Article"""
        try:
            prix = float(brut["pricing"]["amount"])
            frais = float(brut["pricing"]["delivery_fee"])
            note = float(brut["rating"]["average"])
            return [Article(
                reference=brut["sku"],
                designation=brut["title"],
                enseigne="Baobab Shop",
                prix_brut=prix,
                frais_livraison=frais,
                remise=0.0,
                disponible=brut["stock"] > 0,
                note=note,
                quantite=brut["stock"]
            )]
        except Exception as e:
            self._ajouter_au_journal(f"Baobab Shop - {brut.get('sku', '?')}: {e}")
            return []

    def _nettoyer_comptoir_ivoire(self, brut: dict) -> list[Article]:
        """Transforme un dict brut de CI en Article"""
        try:
            prix = float(str(brut["Prix catalogue (FCFA)"]).replace(" ", ""))
            remise = float(str(brut["Remise (%)"]).replace("%", "").strip()) if brut["Remise (%)"] else 0.0
            return [Article(
                reference=str(brut["Code"]),
                designation=str(brut["Article"]),
                enseigne=brut["enseigne"],
                prix_brut=prix,
                frais_livraison=0.0,  # Boutique physique
                remise=remise,
                disponible=int(brut["Quantité en rayon"]) > 0,
                note=None,  # Pas de note
                quantite=int(brut["Quantité en rayon"])
            )]
        except Exception as e:
            self._ajouter_au_journal(f"Comptoir Ivoire - {brut.get('Code', '?')}: {e}")
            return []

    # --- Méthodes utilitaires ---
    def _nettoyer_prix_texte(self, prix_str: str) -> float:
        """Convertit '102 900 FCFA' en 102900.0"""
        if not prix_str:
            raise ValueError("Prix vide")
        prix_str = prix_str.replace(" ", "").replace("FCFA", "").replace("₣", "").strip()
        return float(prix_str)

    def _nettoyer_note(self, note_str: str) -> Optional[float]:
        """Convertit '4,5' en 4.5"""
        if not note_str or note_str == "N/A":
            return None
        note_str = note_str.replace(",", ".").strip()
        return float(note_str)

    def _ajouter_au_journal(self, message: str):
        self.journal.append(message)
        print(f"⚠️  {message}")

    def _sauvegarder_journal(self):
        with open(self.journal_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.journal))
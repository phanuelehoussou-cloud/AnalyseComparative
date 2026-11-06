import datetime
import re
from pathlib import Path
from typing import Optional

from ..models.article import Article
from ..models.historique import HistoriquePrix
from ..models.produit import Produit

ERREURS_DONNEES = (KeyError, ValueError, TypeError)


class Nettoyeur:
    def __init__(self, journal_path: Path):
        self.journal: list[str] = []
        self.journal_path = journal_path

    # --- Points d'entrée ---
    def nettoyer_tout(self, donnees_brutes: dict[str, list[dict]]) -> list[Article]:
        """Nettoie les trois enseignes et retourne une liste d'Article."""
        methodes = {
            "marche_lagune": self._nettoyer_marche_lagune,
            "baobab_shop": self._nettoyer_baobab_shop,
            "comptoir_ivoire": self._nettoyer_comptoir_ivoire,
        }
        articles = []
        for cle, methode in methodes.items():
            for brut in donnees_brutes.get(cle, []):
                article = methode(brut)
                if article is not None:
                    articles.append(article)
        self._sauvegarder_journal()
        return articles

    def nettoyer_catalogue(self, bruts: list[dict]) -> list[Produit]:
        produits = []
        for brut in bruts:
            try:
                produits.append(Produit(
                    produit_id=str(brut["produit_id"]).strip(),
                    nom=str(brut["nom"]).strip(),
                    categorie=str(brut["categorie"]).strip(),
                    marque=str(brut["marque"]).strip(),
                ))
            except ERREURS_DONNEES as e:
                self._ajouter_au_journal(f"Catalogue - {brut.get('produit_id', '?')}: {e!r}")
        self._sauvegarder_journal()
        return produits

    def nettoyer_historique(self, bruts: list[dict]) -> list[HistoriquePrix]:
        historique = []
        for brut in bruts:
            if not str(brut.get("prix_fcfa") or "").strip():
                continue  # décision : lignes sans prix ignorées
            try:
                historique.append(HistoriquePrix(
                    date=self._nettoyer_date(brut["date"]),
                    source=str(brut["source"]).strip(),
                    produit_id=str(brut["produit_id"]).strip(),
                    prix_fcfa=self._nettoyer_nombre(brut["prix_fcfa"]),
                ))
            except ERREURS_DONNEES as e:
                self._ajouter_au_journal(f"Historique - {brut.get('produit_id', '?')}: {e!r}")
        self._sauvegarder_journal()
        return historique

    # --- Une méthode par enseigne ---
    def _nettoyer_marche_lagune(self, brut: dict) -> Optional[Article]:
        try:
            return Article(
                reference=str(brut["reference"]).strip(),
                designation=str(brut["designation"]).strip(),
                enseigne=brut["enseigne"],
                prix_brut=self._nettoyer_nombre(brut["prix"]),
                frais_livraison=0.0,      # livraison incluse
                remise=0.0,
                disponible=str(brut["disponibilite"]).strip().lower() in ("en stock", "stock limité"),
                note=self._nettoyer_note(brut.get("note_clients")),
                quantite=None,            # quantité précise inconnue
            )
        except ERREURS_DONNEES as e:
            self._ajouter_au_journal(f"Marché Lagune - {brut.get('reference', '?')}: {e!r}")
            return None

    def _nettoyer_baobab_shop(self, brut: dict) -> Optional[Article]:
        try:
            stock = int(brut["stock"])
            return Article(
                reference=str(brut["sku"]).strip(),
                designation=str(brut["title"]).strip(),
                enseigne=brut["enseigne"],
                prix_brut=self._nettoyer_nombre(brut["pricing"]["amount"]),
                frais_livraison=self._nettoyer_nombre(brut["pricing"]["delivery_fee"]),
                remise=0.0,
                disponible=stock > 0,
                note=self._nettoyer_note((brut.get("rating") or {}).get("average")),
                quantite=stock,
            )
        except ERREURS_DONNEES as e:
            self._ajouter_au_journal(f"Baobab Shop - {brut.get('sku', '?')}: {e!r}")
            return None

    def _nettoyer_comptoir_ivoire(self, brut: dict) -> Optional[Article]:
        try:
            quantite = int(brut["Quantité en rayon"])
            return Article(
                reference=str(brut["Code"]).strip(),
                designation=str(brut["Article"]).strip(),
                enseigne=brut["enseigne"],
                prix_brut=self._nettoyer_nombre(brut["Prix catalogue (FCFA)"]),
                frais_livraison=0.0,      # boutique physique
                remise=self._nettoyer_remise(brut.get("Remise (%)")),
                disponible=quantite > 0,
                note=None,                # pas de note chez cette enseigne
                quantite=quantite,
            )
        except ERREURS_DONNEES as e:
            self._ajouter_au_journal(f"Comptoir Ivoire - {brut.get('Code', '?')}: {e!r}")
            return None

    # --- Utilitaires ---
    def _nettoyer_nombre(self, valeur) -> float:
        """'102 900 FCFA' -> 102900.0 ; '4,5' -> 4.5 ; gère les espaces insécables."""
        texte = re.sub(r"[^\d,.]", "", str(valeur)).replace(",", ".")
        if not texte:
            raise ValueError(f"Nombre vide ou invalide : {valeur!r}")
        return float(texte)

    def _nettoyer_note(self, valeur) -> Optional[float]:
        if valeur is None or str(valeur).strip().lower() in ("", "n/a"):
            return None
        return self._nettoyer_nombre(valeur)

    def _nettoyer_remise(self, valeur) -> float:
        """Retourne la remise en pourcentage (10 = 10 %)."""
        if valeur is None or str(valeur).strip() == "":
            return 0.0
        remise = self._nettoyer_nombre(valeur)
        # Excel en format pourcentage stocke 10 % sous la forme 0.10
        if isinstance(valeur, float) and 0 < valeur < 1:
            remise *= 100
        if not 0 <= remise <= 100:
            raise ValueError(f"Remise hors limites : {valeur!r}")
        return remise

    def _nettoyer_date(self, valeur) -> datetime.date:
        texte = str(valeur).strip()
        for format_date in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.datetime.strptime(texte, format_date).date()
            except ValueError:
                continue
        raise ValueError(f"Date invalide : {texte!r}")

    def _ajouter_au_journal(self, message: str) -> None:
        self.journal.append(message)
        print(f"⚠️  {message}")

    def _sauvegarder_journal(self) -> None:
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.journal_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.journal))
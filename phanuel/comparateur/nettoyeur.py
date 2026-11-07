import datetime
import re
import sys
from pathlib import Path
from typing import Optional

from ..models.article import Article
from ..models.historique import HistoriquePrix
from ..models.produit import Produit

ERREURS_DONNEES = (KeyError, ValueError, TypeError)


class Nettoyeur:
    """Nettoie, valide, dédoublonne les données brutes et consigne les anomalies dans un journal."""

    def __init__(self, journal_path: Path):
        self.journal: list[str] = []
        self.journal_path = journal_path

    # --- Points d'entrée ---
    def nettoyer_tout(self, donnees_brutes: dict[str, list[dict]]) -> list[Article]:
        """Nettoie les trois enseignes, élimine les doublons et retourne une liste d'Article."""
        methodes = {
            "marche_lagune": self._nettoyer_marche_lagune,
            "baobab_shop": self._nettoyer_baobab_shop,
            "comptoir_ivoire": self._nettoyer_comptoir_ivoire,
        }
        articles: list[Article] = []
        cles_vues: set[tuple[str, str]] = set()

        for cle, methode in methodes.items():
            for brut in donnees_brutes.get(cle, []):
                article = methode(brut)
                if article is None:
                    continue

                # Dédoublonnage sur le couple (enseigne, reference)
                cle_art = (article.enseigne, article.reference)
                if cle_art in cles_vues:
                    self._ajouter_au_journal(
                        f"{article.enseigne} - {article.reference}: Doublon détecté et ignoré ({article.designation})"
                    )
                    continue

                cles_vues.add(cle_art)
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
            val_prix = brut.get("prix_fcfa")
            if val_prix is None or not str(val_prix).strip():
                continue  # lignes sans prix ignorées
            try:
                historique.append(HistoriquePrix(
                    date=self._nettoyer_date(brut["date"]),
                    source=str(brut["source"]).strip(),
                    produit_id=str(brut["produit_id"]).strip(),
                    prix_fcfa=self._nettoyer_nombre(val_prix),
                ))
            except ERREURS_DONNEES as e:
                self._ajouter_au_journal(f"Historique - {brut.get('produit_id', '?')}: {e!r}")
        self._sauvegarder_journal()
        return historique

    # --- Nettoyage par enseigne ---
    def _nettoyer_marche_lagune(self, brut: dict) -> Optional[Article]:
        ref = str(brut.get("reference", "?")).strip()
        try:
            prix = self._nettoyer_nombre(brut.get("prix"))
            ancien_prix_str = brut.get("ancien_prix")
            if ancien_prix_str and str(ancien_prix_str).strip():
                ancien_prix = self._nettoyer_nombre(ancien_prix_str)
                # Détection d'anomalie manifeste (ex: prix 10x plus élevé que l'ancien prix)
                if prix > ancien_prix * 3:
                    self._ajouter_au_journal(
                        f"Marché Lagune - {ref}: Prix anormalement élevé détecté ({prix:,.0f} FCFA vs ancien prix {ancien_prix:,.0f} FCFA)"
                    )

            designation = str(brut["designation"]).strip()
            return Article(
                reference=ref,
                designation=designation,
                enseigne=brut["enseigne"],
                prix_brut=prix,
                frais_livraison=0.0,      # livraison incluse dans le prix affiché
                remise=0.0,
                disponible=str(brut.get("disponibilite", "")).strip().lower() in ("en stock", "stock limité"),
                note=self._nettoyer_note(brut.get("note_clients")),
                quantite=None,            # quantité précise inconnue
            )
        except ERREURS_DONNEES as e:
            self._ajouter_au_journal(f"Marché Lagune - {ref}: {e}")
            return None

    def _nettoyer_baobab_shop(self, brut: dict) -> Optional[Article]:
        sku = str(brut.get("sku", "?")).strip()
        try:
            pricing = brut.get("pricing") or {}
            prix_val = pricing.get("amount")
            if prix_val is None:
                raise ValueError("Montant de prix manquant (None)")

            frais_livr = self._nettoyer_nombre(pricing.get("delivery_fee", 0))
            prix_brut = self._nettoyer_nombre(prix_val)
            stock = int(brut.get("stock", 0))

            return Article(
                reference=sku,
                designation=str(brut.get("title", "")).strip(),
                enseigne=brut["enseigne"],
                prix_brut=prix_brut,
                frais_livraison=frais_livr,
                remise=0.0,
                disponible=stock > 0,
                note=self._nettoyer_note((brut.get("rating") or {}).get("average")),
                quantite=stock,
            )
        except ERREURS_DONNEES as e:
            self._ajouter_au_journal(f"Baobab Shop - {sku}: {e}")
            return None

    def _nettoyer_comptoir_ivoire(self, brut: dict) -> Optional[Article]:
        code = str(brut.get("Code", "?")).strip()
        try:
            quantite = int(brut.get("Quantité en rayon", 0))
            prix_brut = self._nettoyer_nombre(brut.get("Prix catalogue (FCFA)"))
            remise = self._nettoyer_remise(brut.get("Remise (%)"))
            designation = str(brut.get("Article", "")).strip()

            return Article(
                reference=code,
                designation=designation,
                enseigne=brut["enseigne"],
                prix_brut=prix_brut,
                frais_livraison=0.0,      # boutique physique, pas de livraison
                remise=remise,
                disponible=quantite > 0,
                note=None,                # pas d'avis chez Comptoir Ivoire
                quantite=quantite,
            )
        except ERREURS_DONNEES as e:
            self._ajouter_au_journal(f"Comptoir Ivoire - {code}: {e}")
            return None

    # --- Utilitaires de conversion ---
    def _nettoyer_nombre(self, valeur) -> float:
        """Nettoie une valeur numérique (chaîne, entier, float) en gérant séparateurs et espaces."""
        if valeur is None:
            raise ValueError("Valeur numérique manquante (None)")

        if isinstance(valeur, (int, float)):
            return float(valeur)

        texte = str(valeur).strip()
        if not texte:
            raise ValueError("Nombre vide")

        # Retirer la mention de devise et espaces (y compris insécables \u00a0, \u202f)
        texte = re.sub(r"(?i)\s*(?:fcfa|xof|cfa)\b", "", texte)
        texte = re.sub(r"[\s\xa0\u202f]", "", texte)

        # Si le texte contient à la fois '.' et ',' : ex "1.250,50" ou "1,250.50"
        if "." in texte and "," in texte:
            if texte.rfind(",") > texte.rfind("."):
                # Format européen 1.250,50 -> 1250.50
                texte = texte.replace(".", "").replace(",", ".")
            else:
                # Format américain 1,250.50 -> 1250.50
                texte = texte.replace(",", "")
        else:
            texte = texte.replace(",", ".")

        # Retirer tout caractère résiduel non numérique sauf '.' et '-'
        texte = re.sub(r"[^\d.-]", "", texte)
        if not texte or texte == "-":
            raise ValueError(f"Nombre invalide après nettoyage : {valeur!r}")

        return float(texte)

    def _nettoyer_note(self, valeur) -> Optional[float]:
        if valeur is None or str(valeur).strip().lower() in ("", "n/a", "none"):
            return None
        try:
            return self._nettoyer_nombre(valeur)
        except ValueError:
            return None

    def _nettoyer_remise(self, valeur) -> float:
        """Retourne la remise en pourcentage (10 = 10 %)."""
        if valeur is None or str(valeur).strip() == "":
            return 0.0

        if isinstance(valeur, (int, float)):
            remise = float(valeur)
            if 0 < remise < 1:
                remise *= 100
            return remise

        texte = str(valeur).replace("%", "").strip()
        remise = self._nettoyer_nombre(texte)
        if 0 < remise < 1:
            remise *= 100

        if not 0 <= remise <= 100:
            raise ValueError(f"Remise hors limites : {valeur!r}")
        return remise

    def _nettoyer_date(self, valeur) -> datetime.date:
        if isinstance(valeur, datetime.datetime):
            return valeur.date()
        if isinstance(valeur, datetime.date):
            return valeur

        texte = str(valeur).strip()
        # Tronquer l'heure éventuelle (ex: "2026-10-03 00:00:00" -> "2026-10-03")
        texte_date = texte[:10]
        for format_date in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.datetime.strptime(texte_date, format_date).date()
            except ValueError:
                continue
        raise ValueError(f"Date invalide : {texte!r}")

    def _ajouter_au_journal(self, message: str) -> None:
        self.journal.append(message)
        # Éviter tout crash UnicodeEncodeError sur console Windows standard
        prefixe = "[ATTENTION] "
        try:
            print(f"{prefixe}{message}")
        except UnicodeEncodeError:
            # Fallback en ASCII sécurisé si la console ne supporte pas certains caractères
            print(f"{prefixe}{message.encode('ascii', 'backslashreplace').decode('ascii')}")

    def _sauvegarder_journal(self) -> None:
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.journal_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.journal) + "\n")

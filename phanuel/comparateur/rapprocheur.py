import re
import unicodedata
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional

from ..models.article import Article
from ..models.offre import Offre
from ..models.produit import Produit

SEUIL = 0.80  # similarité minimale (0 à 1) pour accepter un rapprochement


# --- Fonctions de texte ---
def normaliser(nom: str) -> str:
    """'SAMSUNG GALAXY A15 (128GB)' -> 'samsung galaxy a15 128go'"""
    nom = nom.lower()

    # retire les accents : é -> e
    nom = unicodedata.normalize("NFD", nom)
    nom = "".join(c for c in nom if unicodedata.category(c) != "Mn")

    nom = re.sub(r"[^a-z0-9\s]", " ", nom)            # ponctuation -> espace
    nom = re.sub(r"(\d)\s*(?:go|gb)\b", r"\1go", nom)  # '128 go' / '128gb' -> '128go'
    nom = re.sub(r"\s+", " ", nom).strip()             # espaces multiples
    return nom


def extraire_code(nom_normalise: str) -> str:
    """Cherche un code modèle (lettre + 2 chiffres) : 'a15'. Retourne '' si absent."""
    trouve = re.search(r"\b[a-z]\d{2}\b", nom_normalise)
    return trouve.group() if trouve else ""


def extraire_capacite(nom_normalise: str) -> str:
    """Cherche une capacité : '128go'. Retourne '' si absente."""
    trouve = re.search(r"\b\d+go\b", nom_normalise)
    return trouve.group() if trouve else ""


def similarite(a: str, b: str) -> float:
    """Score entre 0 (rien en commun) et 1 (identiques)."""
    return SequenceMatcher(None, a, b).ratio()


# --- Rapprocheur ---
@dataclass(frozen=True)
class _EntreeCatalogue:
    produit: Produit
    nom: str
    code: str
    capacite: str


class Rapprocheur:
    """Rattache chaque Article à un Produit du catalogue et fabrique des Offre."""

    def __init__(self, produits: list[Produit], seuil: float = SEUIL):
        self.seuil = seuil
        # Le catalogue est préparé une seule fois
        self._index: list[_EntreeCatalogue] = []
        for produit in produits:
            nom = normaliser(produit.nom)
            self._index.append(_EntreeCatalogue(
                produit, nom, extraire_code(nom), extraire_capacite(nom)
            ))

    def rapprocher_un(self, article: Article) -> Optional[Offre]:
        nom = normaliser(article.designation)
        code = extraire_code(nom)
        capacite = extraire_capacite(nom)
        if not code:
            return None

        # Filtre strict : même code modèle ET même capacité
        candidats = [e for e in self._index if e.code == code and e.capacite == capacite]
        if not candidats:
            return None

        # Comparaison souple sur le nom
        meilleur = max(candidats, key=lambda e: similarite(nom, e.nom))
        if similarite(nom, meilleur.nom) < self.seuil:
            return None

        return Offre(
            produit_id=meilleur.produit.produit_id,
            enseigne=article.enseigne,
            prix_paye=article.prix_paye,
            disponible=article.disponible,
            note=article.note,
            quantite=article.quantite,
        )

    def rapprocher(self, articles: list[Article]) -> tuple[list[Offre], list[Article]]:
        """Retourne (offres rattachées, articles non rattachés à mettre dans le journal)."""
        offres, non_rattaches = [], []
        for article in articles:
            offre = self.rapprocher_un(article)
            if offre is None:
                non_rattaches.append(article)
            else:
                offres.append(offre)
        return offres, non_rattaches
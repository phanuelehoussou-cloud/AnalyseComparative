import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

from ..models.article import Article
from ..models.offre import Offre
from ..models.produit import Produit

SEUIL_ACCEPTATION = 0.28


def normaliser(texte: str) -> str:
    """Normalise une chaîne : minuscules, sans accents, synonymes FR/EN unifiés et unités harmonisées."""
    t = texte.lower()
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")

    # Unification du vocabulaire FR / EN / Argot
    remplacements = [
        (r"\bsamsun\b", "samsung"),
        (r"\bfridge\b", "refrigerateur"),
        (r"\bfrigo\b", "refrigerateur"),
        (r"\bblender\b", "mixeur"),
        (r"\bsteam iron\b", "fer repasser"),
        (r"\bfer a repasser\b", "fer repasser"),
        (r"\belectric kettle\b", "bouilloire"),
        (r"\bbouilloire electrique\b", "bouilloire"),
        (r"\bair conditioner\b", "climatiseur"),
        (r"\bclim\b", "climatiseur"),
        (r"\bwireless mouse\b", "souris sans fil"),
        (r"\bmonitor\b", "ecran"),
        (r"\blaptop\b", "pc portable"),
        (r"\bprinter\b", "imprimante"),
        (r"\bdd externe\b", "disque dur externe"),
        (r"\bventilo\b", "ventilateur"),
        (r"\bmicrowave\b", "micro ondes"),
        (r"\bmicro-ondes\b", "micro ondes"),
        (r"\bultra usb\b", "cle usb"),
        (r"\busb\b", "cle usb"),
        (r"\bexpansion\b", "disque dur externe"),
    ]
    for motif, repl in remplacements:
        t = re.sub(motif, repl, t)

    # Harmonisation des unités de mesure
    t = re.sub(r"(\d+)\s*(?:gb|go)\b", r"\1go", t)
    t = re.sub(r"(\d+)\s*(?:tb|to)\b", r"\1to", t)
    t = re.sub(r"(\d+)\s*(?:hp|cv)\b", r"\1cv", t)
    t = re.sub(r"(\d+)\s*(?:pouces|\"|'')\b", r"\1pouces", t)
    t = re.sub(
        r"(\d+[.,]\d+|\d+)\s*(?:l|litres)\b",
        lambda m: m.group(1).replace(",", ".") + "l",
        t,
    )

    # Ponctuation -> espaces
    t = re.sub(r"[^a-z0-9.]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


@dataclass(frozen=True)
class _EntreeCatalogue:
    produit: Produit
    tokens: set[str]
    nom_normalise: str


class Rapprocheur:
    """Rapproche chaque Article de magasin à un Produit du catalogue commun."""

    def __init__(self, produits: list[Produit], seuil: float = SEUIL_ACCEPTATION):
        self.seuil = seuil
        self._index: list[_EntreeCatalogue] = []
        for p in produits:
            texte_complet = f"{p.nom} {p.marque} {p.categorie}"
            norm = normaliser(texte_complet)
            tokens = set(norm.split())
            self._index.append(_EntreeCatalogue(produit=p, tokens=tokens, nom_normalise=norm))

    def rapprocher_un(self, article: Article) -> Optional[Offre]:
        a_norm = normaliser(f"{article.designation} {article.reference}")
        a_tokens = set(a_norm.split())

        meilleur_score = 0.0
        meilleure_entree: Optional[_EntreeCatalogue] = None

        for entree in self._index:
            inter = a_tokens.intersection(entree.tokens)
            if not inter:
                continue

            # Indice de Dice basé sur les jetons
            score = 2 * len(inter) / (len(a_tokens) + len(entree.tokens))

            # Bonus important si la marque correspond
            marque_norm = normaliser(entree.produit.marque)
            if marque_norm in a_tokens:
                score += 0.15

            if score > meilleur_score:
                meilleur_score = score
                meilleure_entree = entree

        if meilleure_entree is None or meilleur_score < self.seuil:
            return None

        return Offre(
            produit_id=meilleure_entree.produit.produit_id,
            enseigne=article.enseigne,
            prix_paye=article.prix_paye,
            disponible=article.disponible,
            note=article.note,
            quantite=article.quantite,
        )

    def rapprocher(self, articles: list[Article]) -> tuple[list[Offre], list[Article]]:
        """Retourne (offres rattachées, articles non rattachés)."""
        offres: list[Offre] = []
        non_rattaches: list[Article] = []

        for article in articles:
            offre = self.rapprocher_un(article)
            if offre is None:
                non_rattaches.append(article)
            else:
                offres.append(offre)

        return offres, non_rattaches

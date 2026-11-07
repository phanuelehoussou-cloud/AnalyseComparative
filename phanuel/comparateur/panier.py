from typing import Optional

from ..models.offre import Offre
from .comparateur_prix import ComparateurPrix


class Panier:
    """Calcule le coût d'un panier {produit_id: quantité} selon différentes stratégies."""

    def __init__(self, comparateur: ComparateurPrix):
        self.comparateur = comparateur

    @staticmethod
    def _utilisable(offre: Offre, quantite: int) -> bool:
        """Disponible, et assez de stock si la quantité est connue (None = inconnue)."""
        return offre.disponible and (offre.quantite is None or offre.quantite >= quantite)

    def _meilleure_pour(self, produit_id: str, quantite: int, enseigne: Optional[str] = None) -> Optional[Offre]:
        for offre in self.comparateur.offres_du_produit(produit_id):
            if enseigne is not None and offre.enseigne != enseigne:
                continue
            if self._utilisable(offre, quantite):
                return offre
        return None

    def total_par_enseigne(self, contenu: dict[str, int]) -> dict[str, Optional[float]]:
        """Total du panier acheté en entier chez UNE enseigne (None si elle ne peut pas tout fournir)."""
        enseignes = sorted({o.enseigne for o in self.comparateur.offres})
        totaux: dict[str, Optional[float]] = {}
        for enseigne in enseignes:
            total = 0.0
            for produit_id, quantite in contenu.items():
                offre = self._meilleure_pour(produit_id, quantite, enseigne)
                if offre is None:
                    total = None
                    break
                total += offre.prix_paye * quantite
            totaux[enseigne] = total
        return totaux

    def meilleure_enseigne_unique(self, contenu: dict[str, int]) -> Optional[tuple[str, float]]:
        complets = {e: t for e, t in self.total_par_enseigne(contenu).items() if t is not None}
        if not complets:
            return None
        enseigne = min(complets, key=complets.get)
        return enseigne, complets[enseigne]

    def panier_optimise(self, contenu: dict[str, int]) -> dict:
        """Meilleure offre disponible pour CHAQUE produit, quelle que soit l'enseigne."""
        lignes, introuvables, total = [], [], 0.0
        for produit_id, quantite in contenu.items():
            offre = self._meilleure_pour(produit_id, quantite)
            if offre is None:
                introuvables.append(produit_id)
                continue
            produit = self.comparateur.produits.get(produit_id)
            lignes.append({
                "produit": produit.nom if produit else produit_id,
                "enseigne": offre.enseigne,
                "prix_unitaire": offre.prix_paye,
                "quantite": quantite,
            })
            total += offre.prix_paye * quantite
        return {"lignes": lignes, "total": total, "introuvables": introuvables}

    def economie(self, contenu: dict[str, int]) -> Optional[float]:
        """Gain du panier optimisé par rapport à la meilleure enseigne unique."""
        unique = self.meilleure_enseigne_unique(contenu)
        optimise = self.panier_optimise(contenu)
        if unique is None or optimise["introuvables"]:
            return None
        return unique[1] - optimise["total"]
from collections import defaultdict
from typing import Optional

from ..models.offre import Offre
from ..models.produit import Produit


class ComparateurPrix:
    """Compare les offres des enseignes, produit par produit."""

    def __init__(self, produits: list[Produit], offres: list[Offre]):
        self.produits = {p.produit_id: p for p in produits}
        self.offres = offres
        self._par_produit: dict[str, list[Offre]] = defaultdict(list)
        for offre in offres:
            self._par_produit[offre.produit_id].append(offre)

    def offres_du_produit(self, produit_id: str) -> list[Offre]:
        """Toutes les offres, de la moins chère à la plus chère (à prix égal : meilleure note d'abord)."""
        offres = self._par_produit.get(produit_id, [])
        return sorted(offres, key=lambda o: (o.prix_paye, -(o.note or 0)))

    def meilleure_offre(self, produit_id: str) -> Optional[Offre]:
        """Offre DISPONIBLE la moins chère (None si tout est en rupture)."""
        for offre in self.offres_du_produit(produit_id):
            if offre.disponible:
                return offre
        return None

    def ecart_prix(self, produit_id: str) -> Optional[float]:
        """Écart entre l'offre la plus chère et la moins chère (None si moins de 2 offres)."""
        offres = self.offres_du_produit(produit_id)
        if len(offres) < 2:
            return None
        return offres[-1].prix_paye - offres[0].prix_paye

    def resume(self) -> list[dict]:
        """Une ligne par produit du catalogue."""
        lignes = []
        for produit_id, produit in self.produits.items():
            meilleure = self.meilleure_offre(produit_id)

            # écart en % entre l'offre disponible la plus chère et la moins chère
            disponibles = [o for o in self.offres_du_produit(produit_id) if o.disponible]
            ecart_pct = None
            if len(disponibles) >= 2:
                bas, haut = disponibles[0].prix_paye, disponibles[-1].prix_paye
                ecart_pct = (haut - bas) / bas * 100

            lignes.append({
                "produit_id": produit_id,
                "produit": produit.nom,
                "enseigne": meilleure.enseigne if meilleure else None,
                "prix": meilleure.prix_paye if meilleure else None,
                "ecart": self.ecart_prix(produit_id),
                "ecart_pct": ecart_pct,
                "nb_offres": len(self._par_produit.get(produit_id, [])),
            })
        return lignes
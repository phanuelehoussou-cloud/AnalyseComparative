from typing import Optional

from ..models.offre import Offre
from .comparateur_prix import ComparateurPrix

# Panier de rentrée spécifié dans le cahier des charges
PANIER_RENTREE: dict[str, int] = {
    "P04": 1,  # 1 Tecno Spark 20
    "P12": 1,  # 1 Lenovo IdeaPad 3
    "P14": 2,  # 2 clés USB SanDisk 64 Go
    "P15": 1,  # 1 disque dur Seagate 1 To
    "P28": 1,  # 1 micro-ondes Samsung 23 L
}


class Panier:
    """Calcule le coût d'un panier selon chaque enseigne et la stratégie de mélange optimisé."""

    def __init__(self, comparateur: ComparateurPrix):
        self.comparateur = comparateur

    @staticmethod
    def _utilisable(offre: Offre, quantite: int) -> bool:
        """L'offre doit être disponible et disposer d'un stock suffisant si connu."""
        return offre.disponible and (offre.quantite is None or offre.quantite >= quantite)

    def _meilleure_pour(
        self, produit_id: str, quantite: int, enseigne: Optional[str] = None
    ) -> Optional[Offre]:
        """Trouve la meilleure offre disponible répondant à la quantité demandée."""
        for offre in self.comparateur.offres_du_produit(produit_id, seulement_disponibles=True):
            if enseigne is not None and offre.enseigne != enseigne:
                continue
            if self._utilisable(offre, quantite):
                return offre
        return None

    def total_par_enseigne(self, contenu: dict[str, int]) -> dict[str, Optional[float]]:
        """Total du panier acheté en entier chez UNE enseigne (None si incomplète)."""
        totaux: dict[str, Optional[float]] = {}
        enseignes = ["Marché Lagune", "Baobab Shop", "Comptoir Ivoire"]

        for enseigne in enseignes:
            total = 0.0
            possible = True
            for produit_id, quantite in contenu.items():
                offre = self._meilleure_pour(produit_id, quantite, enseigne)
                if offre is None:
                    possible = False
                    break
                total += offre.prix_paye * quantite

            totaux[enseigne] = round(total, 2) if possible else None
        return totaux

    def detail_par_enseigne(self, contenu: dict[str, int]) -> dict[str, dict]:
        """Détail article par article du panier pour chaque enseigne."""
        details: dict[str, dict] = {}
        enseignes = ["Marché Lagune", "Baobab Shop", "Comptoir Ivoire"]

        for enseigne in enseignes:
            lignes = []
            total = 0.0
            possible = True
            for produit_id, quantite in contenu.items():
                offre = self._meilleure_pour(produit_id, quantite, enseigne)
                prod = self.comparateur.produits.get(produit_id)
                nom_prod = prod.nom if prod else produit_id

                if offre is None:
                    possible = False
                    lignes.append({
                        "produit_id": produit_id,
                        "nom": nom_prod,
                        "quantite": quantite,
                        "prix_unitaire": None,
                        "sous_total": None,
                        "disponible": False,
                    })
                else:
                    sous_total = offre.prix_paye * quantite
                    total += sous_total
                    lignes.append({
                        "produit_id": produit_id,
                        "nom": nom_prod,
                        "quantite": quantite,
                        "prix_unitaire": offre.prix_paye,
                        "sous_total": sous_total,
                        "disponible": True,
                    })

            details[enseigne] = {
                "total": round(total, 2) if possible else None,
                "possible": possible,
                "lignes": lignes,
            }
        return details

    def meilleure_enseigne_unique(self, contenu: dict[str, int]) -> Optional[tuple[str, float]]:
        """Identifie l'enseigne unique la moins chère capable de fournir tout le panier."""
        complets = {e: t for e, t in self.total_par_enseigne(contenu).items() if t is not None}
        if not complets:
            return None
        meilleure = min(complets, key=complets.get)
        return meilleure, complets[meilleure]

    def panier_optimise(self, contenu: dict[str, int]) -> dict:
        """Sélectionne l'offre disponible la moins chère pour CHAQUE article du panier."""
        lignes = []
        introuvables = []
        total = 0.0

        for produit_id, quantite in contenu.items():
            offre = self._meilleure_pour(produit_id, quantite)
            prod = self.comparateur.produits.get(produit_id)
            nom_prod = prod.nom if prod else produit_id

            if offre is None:
                introuvables.append(produit_id)
                continue

            sous_total = offre.prix_paye * quantite
            total += sous_total
            lignes.append({
                "produit_id": produit_id,
                "produit": nom_prod,
                "enseigne": offre.enseigne,
                "prix_unitaire": offre.prix_paye,
                "quantite": quantite,
                "sous_total": sous_total,
            })

        return {
            "lignes": lignes,
            "total": round(total, 2),
            "introuvables": introuvables,
        }

    def economie(self, contenu: dict[str, int]) -> Optional[dict]:
        """Gain absolu et pourcentage du mélange optimisé comparé à la meilleure enseigne unique."""
        unique = self.meilleure_enseigne_unique(contenu)
        optimise = self.panier_optimise(contenu)

        if unique is None or optimise["introuvables"]:
            return None

        gain_fcfa = round(unique[1] - optimise["total"], 2)
        gain_pct = round((gain_fcfa / unique[1] * 100), 2) if unique[1] > 0 else 0.0

        return {
            "meilleure_enseigne_unique": unique[0],
            "total_enseigne_unique": unique[1],
            "total_optimise": optimise["total"],
            "economie_fcfa": gain_fcfa,
            "economie_pct": gain_pct,
        }

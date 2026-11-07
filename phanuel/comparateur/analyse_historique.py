from collections import defaultdict
from typing import Optional

from ..models.historique import HistoriquePrix


class AnalyseHistorique:
    """Évolution des prix dans le temps, par produit et par source."""

    def __init__(self, historique: list[HistoriquePrix]):
        self._series: dict[tuple[str, str], list[HistoriquePrix]] = defaultdict(list)
        for ligne in historique:
            self._series[(ligne.produit_id, ligne.source)].append(ligne)
        for serie in self._series.values():
            serie.sort(key=lambda h: h.date)

    def statistiques(self, produit_id: str, source: str) -> Optional[dict]:
        serie = self._series.get((produit_id, source))
        if not serie:
            return None
        prix = [h.prix_fcfa for h in serie]
        premier, dernier = prix[0], prix[-1]
        return {
            "produit_id": produit_id,
            "source": source,
            "nb_points": len(prix),
            "date_debut": serie[0].date,
            "date_fin": serie[-1].date,
            "min": min(prix),
            "max": max(prix),
            "moyenne": sum(prix) / len(prix),
            "premier": premier,
            "dernier": dernier,
            "variation_pct": (dernier - premier) / premier * 100 if premier else None,
        }

    def statistiques_produit(self, produit_id: str) -> list[dict]:
        """Une ligne par source qui a un historique pour ce produit."""
        sources = sorted(s for (pid, s) in self._series if pid == produit_id)
        return [self.statistiques(produit_id, s) for s in sources]

    def plus_fortes_variations(self, n: int = 5) -> list[dict]:
        """Les n séries dont le prix a le plus bougé (hausse ou baisse) entre le début et la fin."""
        toutes = [self.statistiques(pid, src) for (pid, src) in self._series]
        valides = [s for s in toutes if s and s["variation_pct"] is not None]
        return sorted(valides, key=lambda s: abs(s["variation_pct"]), reverse=True)[:n]

    def ecart_vs_moyenne(self, produit_id: str, source: str, prix_actuel: float) -> Optional[float]:
        """Écart en % du prix actuel par rapport à la moyenne historique (négatif = bonne affaire)."""
        stats = self.statistiques(produit_id, source)
        if stats is None or not stats["moyenne"]:
            return None
        return (prix_actuel - stats["moyenne"]) / stats["moyenne"] * 100
import datetime
from collections import defaultdict
from typing import Optional

from ..models.historique import HistoriquePrix

DATE_BF_DEBUT = datetime.date(2025, 11, 24)
DATE_BF_FIN = datetime.date(2025, 11, 30)


class AnalyseHistorique:
    """Analyse temporelle des prix (20 876 relevés) et étude spécifique du Black Friday."""

    def __init__(self, historique: list[HistoriquePrix]):
        self.historique = historique
        self._series: dict[tuple[str, str], list[HistoriquePrix]] = defaultdict(list)
        self._par_source: dict[str, list[HistoriquePrix]] = defaultdict(list)

        for ligne in historique:
            self._series[(ligne.produit_id, ligne.source)].append(ligne)
            self._par_source[ligne.source].append(ligne)

        for serie in self._series.values():
            serie.sort(key=lambda h: h.date)

    def analyse_black_friday(self) -> list[dict]:
        """Compare, pour chaque enseigne, le prix moyen de la semaine du Black Friday

        (24 au 30 novembre 2025) au prix moyen de l'année.
        """
        resultats = []
        for source in sorted(self._par_source):
            releves_annee = [h.prix_fcfa for h in self._par_source[source]]
            releves_bf = [
                h.prix_fcfa
                for h in self._par_source[source]
                if DATE_BF_DEBUT <= h.date <= DATE_BF_FIN
            ]

            if not releves_annee or not releves_bf:
                continue

            moy_annee = sum(releves_annee) / len(releves_annee)
            moy_bf = sum(releves_bf) / len(releves_bf)
            ecart_fcfa = round(moy_bf - moy_annee, 2)
            ecart_pct = round((ecart_fcfa / moy_annee * 100), 2) if moy_annee > 0 else 0.0

            resultats.append({
                "enseigne": source,
                "nb_points_annee": len(releves_annee),
                "prix_moyen_annee": round(moy_annee, 2),
                "nb_points_bf": len(releves_bf),
                "prix_moyen_bf": round(moy_bf, 2),
                "ecart_fcfa": ecart_fcfa,
                "ecart_pct": ecart_pct,
                "est_bonne_affaire": ecart_fcfa < 0,
            })
        return resultats

    def statistiques(self, produit_id: str, source: str) -> Optional[dict]:
        serie = self._series.get((produit_id, source))
        if not serie:
            return None
        prix = [h.prix_fcfa for h in serie]
        premier, dernier = prix[0], prix[-1]
        moyenne = sum(prix) / len(prix)
        return {
            "produit_id": produit_id,
            "source": source,
            "nb_points": len(prix),
            "date_debut": serie[0].date,
            "date_fin": serie[-1].date,
            "min": min(prix),
            "max": max(prix),
            "moyenne": round(moyenne, 2),
            "premier": premier,
            "dernier": dernier,
            "variation_pct": (
                round((dernier - premier) / premier * 100, 2) if premier else None
            ),
        }

    def plus_fortes_variations(
        self, n: int = 5, noms_produits: Optional[dict[str, str]] = None
    ) -> list[dict]:
        """Les n séries ayant le plus varié entre le début et la fin de l'année."""
        toutes = [self.statistiques(pid, src) for (pid, src) in self._series]
        valides = [s for s in toutes if s and s["variation_pct"] is not None]
        tries = sorted(valides, key=lambda s: abs(s["variation_pct"]), reverse=True)[:n]

        # Résolution des noms lisibles
        if noms_produits:
            for s in tries:
                s["produit_nom"] = noms_produits.get(s["produit_id"], s["produit_id"])
        else:
            for s in tries:
                s["produit_nom"] = s["produit_id"]

        return tries

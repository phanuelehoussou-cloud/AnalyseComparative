import time
from contextlib import contextmanager

from ..models.produit import Produit


class Performances:
    """Chronomètre les étapes du traitement."""

    def __init__(self):
        self.mesures: list[tuple[str, float]] = []

    @contextmanager
    def mesurer(self, etape: str):
        debut = time.perf_counter()
        try:
            yield
        finally:
            self.mesures.append((etape, time.perf_counter() - debut))

    def total(self) -> float:
        return sum(duree for _, duree in self.mesures)

    def rapport(self) -> list[dict]:
        total = self.total() or 1e-12
        return [
            {"etape": etape, "secondes": duree, "part_pct": duree / total * 100}
            for etape, duree in self.mesures
        ]


def benchmark_recherche(produits: list[Produit], repetitions: int = 200) -> dict:
    """Compare la recherche d'un produit par son id : parcours de liste (O(n)) ou dictionnaire (O(1))."""
    if not produits:
        return {}
    ids = [p.produit_id for p in produits]
    index = {p.produit_id: p for p in produits}

    debut = time.perf_counter()
    for _ in range(repetitions):
        for produit_id in ids:
            next(p for p in produits if p.produit_id == produit_id)
    liste_s = time.perf_counter() - debut

    debut = time.perf_counter()
    for _ in range(repetitions):
        for produit_id in ids:
            index[produit_id]
    dict_s = time.perf_counter() - debut

    return {
        "nb_produits": len(produits),
        "liste_s": liste_s,
        "dict_s": dict_s,
        "facteur": liste_s / dict_s if dict_s else None,
    }
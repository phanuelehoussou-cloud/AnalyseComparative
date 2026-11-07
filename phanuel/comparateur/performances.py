import time
from contextlib import contextmanager

from ..models.historique import HistoriquePrix
from ..models.produit import Produit


class Performances:
    """Chronomètre chaque étape du traitement global."""

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
            {"etape": etape, "secondes": duree, "part_pct": (duree / total * 100)}
            for etape, duree in self.mesures
        ]


def benchmark_recherche_historique(
    historique: list[HistoriquePrix], repetitions: int = 500
) -> dict:
    """Mesure la recherche de prix dans l'historique de 20 876 lignes :

    Parcours séquentiel de liste O(N) vs Index dictionnaire O(1).
    Explique les choix de structures de données imposés par la volumétrie.
    """
    if not historique:
        return {}

    # Échantillon de clés à chercher
    pas = max(1, len(historique) // 50)
    echantillon = [(h.produit_id, h.date, h.source) for h in historique[::pas]]

    # 1. Recherche par index dictionnaire O(1)
    index = {(h.produit_id, h.date, h.source): h.prix_fcfa for h in historique}
    debut_dict = time.perf_counter()
    for _ in range(repetitions):
        for cle in echantillon:
            _ = index.get(cle)
    duree_dict = time.perf_counter() - debut_dict

    # 2. Recherche séquentielle dans la liste O(N)
    # Nombre d'itérations réduit pour la liste car O(N) est très lent sur 20 000 lignes
    reps_liste = max(1, repetitions // 20)
    debut_liste = time.perf_counter()
    for _ in range(reps_liste):
        for pid, dt, src in echantillon:
            for h in historique:
                if h.produit_id == pid and h.date == dt and h.source == src:
                    _ = h.prix_fcfa
                    break
    duree_liste_ajustee = (time.perf_counter() - debut_liste) * (repetitions / reps_liste)

    facteur = duree_liste_ajustee / duree_dict if duree_dict > 0 else 1.0

    return {
        "nb_lignes": len(historique),
        "nb_recherches": len(echantillon) * repetitions,
        "liste_s": duree_liste_ajustee,
        "dict_s": duree_dict,
        "facteur": facteur,
        "explication": (
            f"Sur {len(historique):,} lignes, la table de hachage O(1) est environ "
            f"{facteur:.0f}× plus rapide que le parcours linéaire O(N)."
        ),
    }

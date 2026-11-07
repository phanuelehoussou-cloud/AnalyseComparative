from collections import defaultdict
from statistics import mean
from typing import Optional

from .comparateur_prix import ComparateurPrix


class Synthese:
    """Bilan global : qui est le moins cher, qui est souvent en rupture, etc."""

    def __init__(self, comparateur: ComparateurPrix):
        self.comparateur = comparateur

    def par_enseigne(self) -> list[dict]:
        offres_nb = defaultdict(int)
        dispo_nb = defaultdict(int)
        notes = defaultdict(list)
        surcouts = defaultdict(list)   # en % par rapport à la meilleure offre disponible
        victoires = defaultdict(int)

        for offre in self.comparateur.offres:
            offres_nb[offre.enseigne] += 1
            if offre.disponible:
                dispo_nb[offre.enseigne] += 1
            if offre.note is not None:
                notes[offre.enseigne].append(offre.note)

        for produit_id in self.comparateur.produits:
            meilleure = self.comparateur.meilleure_offre(produit_id)
            if meilleure is None:
                continue
            victoires[meilleure.enseigne] += 1
            for offre in self.comparateur.offres_du_produit(produit_id):
                if not offre.disponible:
                    continue  # une offre en rupture n'est pas un vrai concurrent
                surcouts[offre.enseigne].append(
                    (offre.prix_paye - meilleure.prix_paye) / meilleure.prix_paye * 100
                )

        lignes = []
        for enseigne in sorted(offres_nb):
            lignes.append({
                "enseigne": enseigne,
                "offres": offres_nb[enseigne],
                "disponibles": dispo_nb[enseigne],
                "victoires": victoires[enseigne],
                "surcout_moyen_pct": mean(surcouts[enseigne]) if surcouts[enseigne] else None,
                "note_moyenne": mean(notes[enseigne]) if notes[enseigne] else None,
            })
        return lignes

    def enseigne_la_moins_chere(self) -> Optional[str]:
        """Enseigne qui remporte le plus de produits."""
        lignes = [l for l in self.par_enseigne() if l["victoires"] > 0]
        if not lignes:
            return None
        return max(lignes, key=lambda l: l["victoires"])["enseigne"]

    def produits_sans_offre_disponible(self) -> list[str]:
        """Noms des produits du catalogue que personne n'a en stock."""
        return [
            produit.nom
            for produit_id, produit in self.comparateur.produits.items()
            if self.comparateur.meilleure_offre(produit_id) is None
        ]
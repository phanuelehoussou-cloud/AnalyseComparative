from collections import defaultdict
from statistics import mean
from typing import Optional

from .comparateur_prix import ComparateurPrix


class Synthese:
    """Bilan global : victoires, surcoût moyen et top 3 des produits à comparer."""

    def __init__(self, comparateur: ComparateurPrix):
        self.comparateur = comparateur
        self._lignes_par_enseigne: Optional[list[dict]] = None

    def par_enseigne(self) -> list[dict]:
        """Calcule les statistiques d'offres, victoires et surcoût moyen pour chaque enseigne."""
        if self._lignes_par_enseigne is not None:
            return self._lignes_par_enseigne

        offres_nb = defaultdict(int)
        dispo_nb = defaultdict(int)
        notes = defaultdict(list)
        surcouts = defaultdict(list)
        victoires = defaultdict(int)

        # Offres brutes et notes
        for offre in self.comparateur.offres:
            offres_nb[offre.enseigne] += 1
            if offre.disponible:
                dispo_nb[offre.enseigne] += 1
            if offre.note is not None:
                notes[offre.enseigne].append(offre.note)

        # Comparatif multi-enseignes pour calculer les victoires et surcoûts
        comparatif = self.comparateur.comparatif_multi_enseignes()
        for ligne in comparatif:
            victoires[ligne["meilleure_enseigne"]] += 1
            bas = ligne["meilleur_prix"]
            for ens, prix_cle in [
                ("Marché Lagune", "prix_marche_lagune"),
                ("Baobab Shop", "prix_baobab_shop"),
                ("Comptoir Ivoire", "prix_comptoir_ivoire"),
            ]:
                prix = ligne.get(prix_cle)
                if prix is not None and bas > 0:
                    surcout_pct = (prix - bas) / bas * 100
                    surcouts[ens].append(surcout_pct)

        lignes = []
        for enseigne in sorted(offres_nb):
            lignes.append({
                "enseigne": enseigne,
                "offres": offres_nb[enseigne],
                "disponibles": dispo_nb[enseigne],
                "victoires": victoires[enseigne],
                "surcout_moyen_pct": mean(surcouts[enseigne]) if surcouts[enseigne] else 0.0,
                "note_moyenne": mean(notes[enseigne]) if notes[enseigne] else None,
            })

        self._lignes_par_enseigne = lignes
        return lignes

    def enseigne_la_moins_chere(self) -> Optional[str]:
        """Enseigne qui remporte le plus de victoires (avec surcoût moyen comme critère de départage)."""
        lignes = [l for l in self.par_enseigne() if l["victoires"] > 0]
        if not lignes:
            return None
        # En cas d'égalité de victoires, celle avec le plus faible surcoût moyen gagne
        return max(lignes, key=lambda l: (l["victoires"], -l["surcout_moyen_pct"]))["enseigne"]

    def top_produits_a_gagner(self, n: int = 3) -> list[dict]:
        """Les n produits où il y a le plus à gagner en comparant (triés par écart absolu en FCFA)."""
        comparatif = self.comparateur.comparatif_multi_enseignes()
        return sorted(comparatif, key=lambda l: l["ecart_fcfa"], reverse=True)[:n]

    def top_produits_a_gagner_pct(self, n: int = 3) -> list[dict]:
        """Les n produits où l'écart en pourcentage est le plus fort."""
        comparatif = self.comparateur.comparatif_multi_enseignes()
        return sorted(comparatif, key=lambda l: l["ecart_pct"], reverse=True)[:n]

    def produits_sans_offre_disponible(self) -> list[str]:
        """Produits du catalogue dont aucune offre disponible n'a été trouvée."""
        return [
            produit.nom
            for produit_id, produit in self.comparateur.produits.items()
            if self.comparateur.meilleure_offre(produit_id) is None
        ]

import csv
from collections import defaultdict
from pathlib import Path
from typing import Optional

from ..models.offre import Offre
from ..models.produit import Produit


class ComparateurPrix:
    """Compare les offres disponibles produit par produit, selon le cahier des charges."""

    def __init__(self, produits: list[Produit], offres: list[Offre]):
        self.produits = {p.produit_id: p for p in produits}
        self.offres = offres
        self._par_produit: dict[str, list[Offre]] = defaultdict(list)
        for offre in offres:
            self._par_produit[offre.produit_id].append(offre)

    def offres_du_produit(self, produit_id: str, seulement_disponibles: bool = False) -> list[Offre]:
        """Toutes les offres du produit, triées par prix croissant (puis meilleure note)."""
        offres = self._par_produit.get(produit_id, [])
        if seulement_disponibles:
            offres = [o for o in offres if o.disponible]
        return sorted(offres, key=lambda o: (o.prix_paye, -(o.note or 0)))

    def meilleure_offre(self, produit_id: str) -> Optional[Offre]:
        """Offre DISPONIBLE la moins chère. Aucun produit en rupture n'est retenu."""
        disponibles = self.offres_du_produit(produit_id, seulement_disponibles=True)
        return disponibles[0] if disponibles else None

    def comparatif_multi_enseignes(self) -> list[dict]:
        """Produits disponibles dans au moins 2 enseignes, avec prix chez chacune,

        enseigne la moins chère, écart en FCFA et en %.
        """
        lignes = []
        for produit_id, produit in self.produits.items():
            dispos = self.offres_du_produit(produit_id, seulement_disponibles=True)
            enseignes_dispos = {o.enseigne for o in dispos}
            if len(enseignes_dispos) < 2:
                continue

            # Meilleure offre par enseigne (au cas où il y aurait plusieurs offres)
            par_ens: dict[str, float] = {}
            for o in dispos:
                if o.enseigne not in par_ens or o.prix_paye < par_ens[o.enseigne]:
                    par_ens[o.enseigne] = o.prix_paye

            prix_tous = list(par_ens.values())
            bas = min(prix_tous)
            haut = max(prix_tous)
            ecart_fcfa = haut - bas
            ecart_pct = (ecart_fcfa / bas * 100) if bas > 0 else 0.0

            meilleure = dispos[0]  # Déjà trié par prix croissant

            lignes.append({
                "produit_id": produit_id,
                "nom": produit.nom,
                "categorie": produit.categorie,
                "marque": produit.marque,
                "prix_marche_lagune": par_ens.get("Marché Lagune"),
                "prix_baobab_shop": par_ens.get("Baobab Shop"),
                "prix_comptoir_ivoire": par_ens.get("Comptoir Ivoire"),
                "meilleure_enseigne": meilleure.enseigne,
                "meilleur_prix": bas,
                "prix_plus_eleve": haut,
                "ecart_fcfa": ecart_fcfa,
                "ecart_pct": ecart_pct,
                "nb_enseignes": len(par_ens),
            })
        return lignes

    def resume(self) -> list[dict]:
        """Synthèse générale pour l'ensemble des 30 produits du catalogue."""
        lignes = []
        for produit_id, produit in self.produits.items():
            dispos = self.offres_du_produit(produit_id, seulement_disponibles=True)
            meilleure = dispos[0] if dispos else None

            if len(dispos) >= 2:
                bas, haut = dispos[0].prix_paye, dispos[-1].prix_paye
                ecart_fcfa = haut - bas
                ecart_pct = (ecart_fcfa / bas * 100) if bas > 0 else 0.0
            else:
                ecart_fcfa = None
                ecart_pct = None

            lignes.append({
                "produit_id": produit_id,
                "produit": produit.nom,
                "enseigne": meilleure.enseigne if meilleure else None,
                "prix": meilleure.prix_paye if meilleure else None,
                "ecart": ecart_fcfa,
                "ecart_pct": ecart_pct,
                "nb_offres": len(self._par_produit.get(produit_id, [])),
                "nb_disponibles": len(dispos),
            })
        return lignes

    def exporter_comparatif_csv(self, chemin_fichier: Path) -> None:
        """Exporte le tableau comparatif des produits multi-enseignes en fichier CSV."""
        chemin_fichier.parent.mkdir(parents=True, exist_ok=True)
        lignes = self.comparatif_multi_enseignes()
        champs = [
            "produit_id",
            "nom",
            "categorie",
            "marque",
            "prix_marche_lagune",
            "prix_baobab_shop",
            "prix_comptoir_ivoire",
            "meilleure_enseigne",
            "meilleur_prix",
            "ecart_fcfa",
            "ecart_pct",
        ]
        with open(chemin_fichier, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=champs, delimiter=";", extrasaction="ignore")
            writer.writeheader()
            for ligne in lignes:
                writer.writerow(ligne)

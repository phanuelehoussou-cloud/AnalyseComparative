from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..comparateur.analyse_historique import AnalyseHistorique
from ..comparateur.chargeur import Chargeur
from ..comparateur.comparateur_prix import ComparateurPrix
from ..comparateur.nettoyeur import Nettoyeur
from ..comparateur.panier import Panier
from ..comparateur.performances import Performances, benchmark_recherche
from ..comparateur.rapprocheur import Rapprocheur
from ..comparateur.synthese import Synthese
from ..models.article import Article
from ..models.enseigne import ENSEIGNES_PAR_NOM
from ..models.offre import Offre
from ..models.produit import Produit

FICHIER_CATALOGUE = "catalogue_reference.csv"
FICHIER_HISTORIQUE = "historique_prix.csv"


@dataclass
class ResultatsAnalyse:
    produits: list[Produit]
    offres: list[Offre]
    non_rattaches: list[Article]
    resume: list[dict]
    synthese: list[dict]
    meilleure_enseigne: Optional[str]
    produits_sans_offre: list[str]
    contenu_panier: dict[str, int]
    totaux_panier: dict[str, Optional[float]]
    panier_optimise: dict
    economie_panier: Optional[float]
    variations_historique: list[dict]
    performances: list[dict]
    benchmark: dict


class ComparateurController:
    """Chef d'orchestre : enchaîne les étapes, ne calcule rien lui-même."""

    def __init__(self, data_dir: Path, output_dir: Path):
        self.data_dir = data_dir
        self.output_dir = output_dir

    def executer(self, contenu_panier: Optional[dict[str, int]] = None) -> ResultatsAnalyse:
        perf = Performances()
        chargeur = Chargeur(self.data_dir)
        nettoyeur = Nettoyeur(self.output_dir / "journal.txt")

        # 1. Charger
        with perf.mesurer("Chargement"):
            bruts = {
                "marche_lagune": chargeur.charger_marche_lagune(ENSEIGNES_PAR_NOM["Marché Lagune"].fichier),
                "baobab_shop": chargeur.charger_baobab_shop(ENSEIGNES_PAR_NOM["Baobab Shop"].fichier),
                "comptoir_ivoire": chargeur.charger_comptoir_ivoire(ENSEIGNES_PAR_NOM["Comptoir Ivoire"].fichier),
            }
            catalogue_brut = chargeur.charger_catalogue(FICHIER_CATALOGUE)
            historique_brut = chargeur.charger_historique(FICHIER_HISTORIQUE)

        # 2. Nettoyer
        with perf.mesurer("Nettoyage"):
            articles = nettoyeur.nettoyer_tout(bruts)
            produits = nettoyeur.nettoyer_catalogue(catalogue_brut)
            historique = nettoyeur.nettoyer_historique(historique_brut)

        # 3. Rapprocher
        with perf.mesurer("Rapprochement"):
            offres, non_rattaches = Rapprocheur(produits).rapprocher(articles)
            self._ecrire_non_rattaches(non_rattaches)

        # 4. Comparer, synthétiser, calculer le panier
        with perf.mesurer("Comparaison"):
            comparateur = ComparateurPrix(produits, offres)
            resume = comparateur.resume()
            synthese = Synthese(comparateur)
            lignes_synthese = synthese.par_enseigne()

        with perf.mesurer("Panier"):
            # Par défaut : 1 exemplaire de chaque produit disponible quelque part
            contenu = contenu_panier or {l["produit_id"]: 1 for l in resume if l["prix"] is not None}
            panier = Panier(comparateur)
            totaux = panier.total_par_enseigne(contenu)
            optimise = panier.panier_optimise(contenu)
            economie = panier.economie(contenu)

        # 5. Historique
        with perf.mesurer("Historique"):
            variations = AnalyseHistorique(historique).plus_fortes_variations(5)

        return ResultatsAnalyse(
            produits=produits,
            offres=offres,
            non_rattaches=non_rattaches,
            resume=resume,
            synthese=lignes_synthese,
            meilleure_enseigne=synthese.enseigne_la_moins_chere(),
            produits_sans_offre=synthese.produits_sans_offre_disponible(),
            contenu_panier=contenu,
            totaux_panier=totaux,
            panier_optimise=optimise,
            economie_panier=economie,
            variations_historique=variations,
            performances=perf.rapport(),
            benchmark=benchmark_recherche(produits),
        )

    def _ecrire_non_rattaches(self, non_rattaches: list[Article]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        lignes = [f"{a.enseigne} | {a.reference} | {a.designation}" for a in non_rattaches]
        (self.output_dir / "non_rattaches.txt").write_text("\n".join(lignes), encoding="utf-8")
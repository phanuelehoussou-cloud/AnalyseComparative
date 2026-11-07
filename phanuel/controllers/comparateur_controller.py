from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..comparateur.analyse_historique import AnalyseHistorique
from ..comparateur.chargeur import Chargeur
from ..comparateur.comparateur_prix import ComparateurPrix
from ..comparateur.nettoyeur import Nettoyeur
from ..comparateur.panier import PANIER_RENTREE, Panier
from ..comparateur.performances import Performances, benchmark_recherche_historique
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
    comparatif_multi_enseignes: list[dict]
    resume_general: list[dict]
    synthese_enseignes: list[dict]
    meilleure_enseigne: Optional[str]
    top_3_gains_fcfa: list[dict]
    top_3_gains_pct: list[dict]
    panier_rentree_contenu: dict[str, int]
    panier_totaux: dict[str, Optional[float]]
    panier_details: dict[str, dict]
    panier_optimise: dict
    panier_economie: Optional[dict]
    black_friday: list[dict]
    variations_historique: list[dict]
    performances: list[dict]
    benchmark_complexite: dict
    chemin_csv_comparatif: Path


class ComparateurController:
    """Orchestre la collecte, le nettoyage, le rapprochement et les analyses comparatives."""

    def __init__(self, data_dir: Path, output_dir: Path):
        self.data_dir = data_dir
        self.output_dir = output_dir

    def executer(
        self, panier_personnalise: Optional[dict[str, int]] = None
    ) -> ResultatsAnalyse:
        perf = Performances()
        chargeur = Chargeur(self.data_dir)
        nettoyeur = Nettoyeur(self.output_dir / "journal.txt")

        # 1. Chargement des sources (CSV, JSON, Excel) dans une même structure de données
        with perf.mesurer("1. Chargement"):
            bruts = chargeur.charger_toutes_enseignes()
            catalogue_brut = chargeur.charger_catalogue(FICHIER_CATALOGUE)
            historique_brut = chargeur.charger_historique(FICHIER_HISTORIQUE)

        # 2. Nettoyage et validation des données
        with perf.mesurer("2. Nettoyage"):
            articles = nettoyeur.nettoyer_tout(bruts)
            produits = nettoyeur.nettoyer_catalogue(catalogue_brut)
            historique = nettoyeur.nettoyer_historique(historique_brut)

        # 3. Rapprochement avec le catalogue commun
        with perf.mesurer("3. Rapprochement"):
            offres, non_rattaches = Rapprocheur(produits).rapprocher(articles)
            self._ecrire_non_rattaches(non_rattaches)

        # 4. Comparatif multi-enseignes et export CSV
        with perf.mesurer("4. Comparatif & Export CSV"):
            comparateur = ComparateurPrix(produits, offres)
            comparatif = comparateur.comparatif_multi_enseignes()
            resume = comparateur.resume()
            csv_path = self.output_dir / "comparatif.csv"
            comparateur.exporter_comparatif_csv(csv_path)

        # 5. Synthèse globale & Top 3 des produits à comparer
        with perf.mesurer("5. Synthèse & Top Gains"):
            synthese = Synthese(comparateur)
            lignes_synthese = synthese.par_enseigne()
            meilleure_ens = synthese.enseigne_la_moins_chere()
            top_fcfa = synthese.top_produits_a_gagner(3)
            top_pct = synthese.top_produits_a_gagner_pct(3)

        # 6. Panier de rentrée
        with perf.mesurer("6. Panier de rentrée"):
            contenu_panier = panier_personnalise or PANIER_RENTREE
            panier = Panier(comparateur)
            totaux_panier = panier.total_par_enseigne(contenu_panier)
            details_panier = panier.detail_par_enseigne(contenu_panier)
            optimise = panier.panier_optimise(contenu_panier)
            economie = panier.economie(contenu_panier)

        # 7. Historique & Semaine du Black Friday
        with perf.mesurer("7. Historique & Black Friday"):
            noms_map = {p.produit_id: p.nom for p in produits}
            analyse_hist = AnalyseHistorique(historique)
            analyse_bf = analyse_hist.analyse_black_friday()
            variations = analyse_hist.plus_fortes_variations(5, noms_produits=noms_map)

        # 8. Mesure de complexité O(1) vs O(N) sur l'historique
        with perf.mesurer("8. Benchmark Complexité"):
            bench = benchmark_recherche_historique(historique)

        return ResultatsAnalyse(
            produits=produits,
            offres=offres,
            non_rattaches=non_rattaches,
            comparatif_multi_enseignes=comparatif,
            resume_general=resume,
            synthese_enseignes=lignes_synthese,
            meilleure_enseigne=meilleure_ens,
            top_3_gains_fcfa=top_fcfa,
            top_3_gains_pct=top_pct,
            panier_rentree_contenu=contenu_panier,
            panier_totaux=totaux_panier,
            panier_details=details_panier,
            panier_optimise=optimise,
            panier_economie=economie,
            black_friday=analyse_bf,
            variations_historique=variations,
            performances=perf.rapport(),
            benchmark_complexite=bench,
            chemin_csv_comparatif=csv_path,
        )

    def _ecrire_non_rattaches(self, non_rattaches: list[Article]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if not non_rattaches:
            lignes = ["Aucun article non rattaché : tous les articles ont été associés avec succès."]
        else:
            lignes = [f"{a.enseigne} | {a.reference} | {a.designation}" for a in non_rattaches]
        (self.output_dir / "non_rattaches.txt").write_text("\n".join(lignes), encoding="utf-8")

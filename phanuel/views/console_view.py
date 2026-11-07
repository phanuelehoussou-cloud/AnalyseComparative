from typing import Optional

from rich.console import Console
from rich.table import Table

from ..controllers.comparateur_controller import ResultatsAnalyse


def _fcfa(valeur: Optional[float]) -> str:
    if valeur is None:
        return "-"
    return f"{valeur:,.0f}".replace(",", " ") + " FCFA"


def _pct(valeur: Optional[float], signe: bool = False) -> str:
    if valeur is None:
        return "-"
    return f"{valeur:+.1f} %" if signe else f"{valeur:.1f} %"


class ConsoleView:
    def __init__(self):
        self.console = Console()

    def afficher_erreur(self, message: str) -> None:
        self.console.print(f"[bold red]Erreur :[/bold red] {message}")

    def afficher_tout(self, r: ResultatsAnalyse) -> None:
        self.afficher_resume(r)
        self.afficher_synthese(r)
        self.afficher_panier(r)
        self.afficher_historique(r)
        self.afficher_non_rattaches(r)
        self.afficher_performances(r)

    def afficher_resume(self, r: ResultatsAnalyse) -> None:
        table = Table(title="Meilleure offre par produit")
        for colonne in ("Produit", "Enseigne", "Prix payé", "Écart max", "Offres"):
            table.add_column(colonne)
        for ligne in r.resume:
            table.add_row(
                ligne["produit"],
                ligne["enseigne"] or "[red]rupture partout[/red]",
                _fcfa(ligne["prix"]),
                _fcfa(ligne["ecart"]),
                str(ligne["nb_offres"]),
            )
        self.console.print(table)

    def afficher_synthese(self, r: ResultatsAnalyse) -> None:
        table = Table(title="Synthèse par enseigne")
        for colonne in ("Enseigne", "Offres", "Dispo", "Produits gagnés", "Surcoût moyen", "Note moy."):
            table.add_column(colonne)
        for ligne in r.synthese:
            note = f"{ligne['note_moyenne']:.1f}" if ligne["note_moyenne"] is not None else "-"
            table.add_row(
                ligne["enseigne"], str(ligne["offres"]), str(ligne["disponibles"]),
                str(ligne["victoires"]), _pct(ligne["surcout_moyen_pct"]), note,
            )
        self.console.print(table)
        if r.meilleure_enseigne:
            self.console.print(f"Enseigne la moins chère : [bold green]{r.meilleure_enseigne}[/bold green]")
        if r.produits_sans_offre:
            self.console.print("Sans offre disponible : " + ", ".join(r.produits_sans_offre))

    def afficher_panier(self, r: ResultatsAnalyse) -> None:
        table = Table(title=f"Panier ({len(r.contenu_panier)} produits)")
        table.add_column("Stratégie")
        table.add_column("Total", justify="right")
        for enseigne, total in r.totaux_panier.items():
            table.add_row(f"Tout chez {enseigne}", _fcfa(total) if total is not None else "[red]incomplet[/red]")
        table.add_row("[bold]Meilleur mélange[/bold]", f"[bold]{_fcfa(r.panier_optimise['total'])}[/bold]")
        self.console.print(table)
        if r.economie_panier is not None:
            self.console.print(f"Économie du mélange : [green]{_fcfa(r.economie_panier)}[/green]")
        if r.panier_optimise["introuvables"]:
            self.console.print("Introuvables : " + ", ".join(r.panier_optimise["introuvables"]))

    def afficher_historique(self, r: ResultatsAnalyse) -> None:
        table = Table(title="Plus fortes variations de prix")
        for colonne in ("Produit", "Source", "Premier", "Dernier", "Variation"):
            table.add_column(colonne)
        for s in r.variations_historique:
            table.add_row(s["produit_id"], s["source"], _fcfa(s["premier"]), _fcfa(s["dernier"]),
                            _pct(s["variation_pct"], signe=True))
        self.console.print(table)

    def afficher_non_rattaches(self, r: ResultatsAnalyse, limite: int = 10) -> None:
        total = len(r.non_rattaches)
        self.console.print(f"\nArticles non rattachés au catalogue : [bold]{total}[/bold] "
                            f"(liste complète dans output/non_rattaches.txt)")
        for a in r.non_rattaches[:limite]:
            self.console.print(f"  - {a.enseigne} : {a.designation}")

    def afficher_performances(self, r: ResultatsAnalyse) -> None:
        table = Table(title="Performances")
        table.add_column("Étape")
        table.add_column("Durée", justify="right")
        table.add_column("Part", justify="right")
        for ligne in r.performances:
            table.add_row(ligne["etape"], f"{ligne['secondes'] * 1000:.1f} ms", _pct(ligne["part_pct"]))
        self.console.print(table)
        b = r.benchmark
        if b and b.get("facteur"):
            self.console.print(f"Recherche par id ({b['nb_produits']} produits) : le dictionnaire est "
                                f"{b['facteur']:.1f}× plus rapide que le parcours de liste.")
import os
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from ..controllers.comparateur_controller import ResultatsAnalyse

# =====================================================================
# PALETTE DE COULEURS VIBRANTES SANS AUCUNE COULEUR BLANCHE
# =====================================================================
C_PRIMARY = "bright_cyan"          # Cyan éclatant
C_SECONDARY = "dodger_blue1"       # Bleu vif
C_ACCENT = "bright_yellow"         # Jaune vif
C_GOLD = "gold1"                   # Or
C_SUCCESS = "spring_green3"        # Vert vif (prix min, économies, victoires)
C_ORANGE = "dark_orange"           # Orange (Baobab Shop, alertes)
C_MAGENTA = "bright_magenta"       # Magenta / Violet (Comptoir Ivoire, pourcentages)
C_BLUE = "deep_sky_blue1"          # Bleu ciel (écarts, montants)
C_MUTED = "steel_blue"             # Bleu acier doux (descriptions)
C_ALERT = "red1"                   # Rouge (anomalies)


def _fcfa(valeur: Optional[float]) -> str:
    if valeur is None:
        return "-"
    return f"{valeur:,.0f}".replace(",", " ") + " FCFA"


def _pct(valeur: Optional[float], signe: bool = False) -> str:
    if valeur is None:
        return "-"
    return f"{valeur:+.1f} %" if signe else f"{valeur:.1f} %"


class RichConsoleView:
    """Vue console interactive propulsée par Rich.

    Utilise exclusivement une palette colorée riche (cyan, vert, jaune, magenta, bleu, orange)
    sans aucune couleur blanche.
    """

    def __init__(self, resultats: ResultatsAnalyse):
        self.r = resultats
        self.console = Console()

    def demarrer(self) -> None:
        """Boucle interactive principale du menu console Rich."""
        while True:
            self._afficher_banniere_menu()
            choix = Prompt.ask(
                f"[{C_ACCENT}]Entrez votre choix (1 à 7, ou 0 pour quitter)[/{C_ACCENT}]",
                choices=["1", "2", "3", "4", "5", "6", "7", "g", "G", "0", "q", "Q"],
                default="1",
                console=self.console,
            ).strip().lower()

            if choix in ("0", "q"):
                self.console.print(
                    f"\n[{C_GOLD}]👋 Merci d'avoir utilisé le Comparateur de Marché. Au revoir ![/{C_GOLD}]\n"
                )
                break
            elif choix == "1":
                self.afficher_comparatif()
            elif choix == "2":
                self.afficher_synthese()
            elif choix == "3":
                self.afficher_panier()
            elif choix == "4":
                self.afficher_historique()
            elif choix == "5":
                self.afficher_journal()
            elif choix == "6":
                self.afficher_performances()
            elif choix in ("7", "g"):
                self.lancer_tkinter()

    def _afficher_banniere_menu(self) -> None:
        """Affiche l'en-tête et la table des options du menu principal."""
        self.console.print()
        banniere = Panel(
            f"[{C_ACCENT} bold]ANALYSE COMPARATIVE DE MARCHÉ — ABIDJAN (DA PYTHON L2)[/{C_ACCENT} bold]\n"
            f"[{C_PRIMARY}]Marché Lagune (CSV) · Baobab Shop (JSON) · Comptoir Ivoire (Excel)[/{C_PRIMARY}]",
            border_style=C_PRIMARY,
            padding=(1, 2),
        )
        self.console.print(banniere)

        menu = Table(
            title=f"[{C_GOLD} bold]MENU PRINCIPAL INTERACTIF[/{C_GOLD} bold]",
            border_style=C_SECONDARY,
            header_style=f"bold {C_GOLD}",
        )
        menu.add_column("Option", style=f"bold {C_ACCENT}", justify="center", width=8)
        menu.add_column("Rubrique d'analyse", style=f"bold {C_SUCCESS}", width=34)
        menu.add_column("Description du traitement", style=C_MUTED, width=44)

        menu.add_row("[1]", "Comparatif multi-enseignes", "23 produits disponibles chez ≥ 2 enseignes & export CSV")
        menu.add_row("[2]", "Synthèse des enseignes & Top Gains", "Victoires, surcoût moyen et les 3 produits à comparer")
        menu.add_row("[3]", "Panier de rentrée (5 articles)", "Coût par enseigne, mélange optimisé et économie")
        menu.add_row("[4]", "Historique & Black Friday", "Semaine du Black Friday vs Année (Quand acheter ?)")
        menu.add_row("[5]", "Journal de nettoyage", "Anomalies, formats textes, doublons et prix aberrants")
        menu.add_row("[6]", "Performances & Complexité", "Chronométrage des étapes et benchmark O(1) vs O(N)")
        menu.add_row("[7]", "Lancer l'Interface Graphique (Tkinter)", "Ouvrir la fenêtre graphique Dark Slate")
        menu.add_row("[0]", "Quitter l'application", "Fermer le programme")

        self.console.print(menu)
        self.console.print()

    def _pause(self) -> None:
        """Marque une pause conviviale avant de revenir au menu."""
        self.console.print()
        Prompt.ask(
            f"[{C_PRIMARY}]➜ Appuyez sur [bold {C_ACCENT}]Entrée[/bold {C_ACCENT}] pour revenir au menu principal[/{C_PRIMARY}]",
            default="",
            show_default=False,
            console=self.console,
        )

    # ------------------------------------------------------------- 1. COMPARATIF
    def afficher_comparatif(self) -> None:
        """[1] Affiche le tableau comparatif des 23 produits multi-enseignes."""
        total = len(self.r.comparatif_multi_enseignes)
        self.console.print()

        titre = f"[{C_GOLD} bold]1. COMPARATIF DES PRIX MULTI-ENSEIGNES ({total} PRODUITS DISPONIBLES CHEZ ≥ 2 ENSEIGNES)[/{C_GOLD} bold]"
        tableau = Table(title=titre, border_style=C_SECONDARY, header_style=f"bold {C_GOLD}")

        tableau.add_column("ID", style=C_ACCENT, justify="center", width=5)
        tableau.add_column("Désignation Produit", style=C_PRIMARY, width=28)
        tableau.add_column("Marché Lagune", style=C_SUCCESS, justify="right", width=14)
        tableau.add_column("Baobab Shop", style=C_ORANGE, justify="right", width=14)
        tableau.add_column("Comptoir Ivoire", style=C_MAGENTA, justify="right", width=14)
        tableau.add_column("Moins cher", style=f"bold {C_SUCCESS}", width=15)
        tableau.add_column("Prix min", style=f"bold {C_GOLD}", justify="right", width=13)
        tableau.add_column("Écart FCFA", style=C_BLUE, justify="right", width=13)
        tableau.add_column("Écart %", style=C_MAGENTA, justify="right", width=10)

        for l in self.r.comparatif_multi_enseignes:
            tableau.add_row(
                l["produit_id"],
                l["nom"],
                _fcfa(l["prix_marche_lagune"]),
                _fcfa(l["prix_baobab_shop"]),
                _fcfa(l["prix_comptoir_ivoire"]),
                l["meilleure_enseigne"],
                _fcfa(l["meilleur_prix"]),
                _fcfa(l["ecart_fcfa"]),
                _pct(l["ecart_pct"]),
            )

        self.console.print(tableau)

        export_panel = Panel(
            f"[{C_SUCCESS} bold]✓ Fichier exporté avec succès :[/{C_SUCCESS} bold] "
            f"[{C_ACCENT}]{self.r.chemin_csv_comparatif.resolve()}[/{C_ACCENT}]\n"
            f"[{C_MUTED}]Séparateur : ';' | Encodage : UTF-8 avec BOM (compatible Excel)[/{C_MUTED}]",
            border_style=C_SUCCESS,
        )
        self.console.print(export_panel)
        self._pause()

    # ------------------------------------------------------------- 2. SYNTHÈSE
    def afficher_synthese(self) -> None:
        """[2] Affiche le bilan par enseigne et le Top 3 des gains."""
        self.console.print()

        t_bilan = Table(
            title=f"[{C_GOLD} bold]2. SYNTHÈSE PAR ENSEIGNE (23 PRODUITS COMPARABLES)[/{C_GOLD} bold]",
            border_style=C_SECONDARY,
            header_style=f"bold {C_GOLD}",
        )
        t_bilan.add_column("Enseigne", style=C_PRIMARY, width=18)
        t_bilan.add_column("Offres", style=C_ACCENT, justify="right", width=10)
        t_bilan.add_column("Disponibles", style=C_SUCCESS, justify="right", width=12)
        t_bilan.add_column("Victoires (Moins cher)", style=f"bold {C_GOLD}", justify="right", width=22)
        t_bilan.add_column("Surcoût moyen %", style=C_BLUE, justify="right", width=16)
        t_bilan.add_column("Note moyenne", style=C_ORANGE, justify="right", width=14)

        for l in self.r.synthese_enseignes:
            note_str = f"{l['note_moyenne']:.2f}" if l["note_moyenne"] is not None else "-"
            t_bilan.add_row(
                l["enseigne"],
                str(l["offres"]),
                str(l["disponibles"]),
                str(l["victoires"]),
                _pct(l["surcout_moyen_pct"]),
                note_str,
            )

        self.console.print(t_bilan)

        if self.r.meilleure_enseigne:
            p_gagnant = Panel(
                f"[{C_GOLD} bold]🏆 ENSEIGNE LA MOINS CHÈRE GLOBALEMENT :[/{C_GOLD} bold] "
                f"[{C_SUCCESS} bold]{self.r.meilleure_enseigne}[/{C_SUCCESS} bold]\n"
                f"[{C_MUTED}]Remporte le plus de produits au prix le plus bas avec le surcoût moyen le plus modéré.[/{C_MUTED}]",
                border_style=C_GOLD,
            )
            self.console.print(p_gagnant)

        # Top 3 des gains
        t_top = Table(
            title=f"[{C_ACCENT} bold]TOP 3 DES PRODUITS OÙ IL Y A LE PLUS À GAGNER EN COMPARANT[/{C_ACCENT} bold]",
            border_style=C_PRIMARY,
            header_style=f"bold {C_ACCENT}",
        )
        t_top.add_column("Rang", style=C_ACCENT, justify="center", width=6)
        t_top.add_column("Produit", style=C_PRIMARY, width=32)
        t_top.add_column("Meilleur prix", style=C_SUCCESS, justify="right", width=22)
        t_top.add_column("Prix le plus élevé", style=C_ALERT, justify="right", width=18)
        t_top.add_column("Économie FCFA", style=f"bold {C_GOLD}", justify="right", width=16)
        t_top.add_column("Écart %", style=C_MAGENTA, justify="right", width=10)

        for i, l in enumerate(self.r.top_3_gains_fcfa):
            t_top.add_row(
                f"#{i+1}",
                l["nom"],
                f"{_fcfa(l['meilleur_prix'])} ({l['meilleure_enseigne']})",
                _fcfa(l["prix_plus_eleve"]),
                _fcfa(l["ecart_fcfa"]),
                _pct(l["ecart_pct"]),
            )

        self.console.print(t_top)
        self._pause()

    # ------------------------------------------------------------- 3. PANIER
    def afficher_panier(self) -> None:
        """[3] Affiche le panier de rentrée et le mélange optimisé."""
        self.console.print()

        p_info = Panel(
            f"[{C_ACCENT} bold]COMPOSITION DU PANIER DE RENTRÉE (5 ARTICLES IMPOSÉS) :[/{C_ACCENT} bold]\n"
            f"[{C_PRIMARY}]• 1 Tecno Spark 20 (P04)  • 1 Lenovo IdeaPad 3 (P12)  • 2 Clés SanDisk 64Go (P14)\n"
            f"• 1 DD Seagate 1To (P15)  • 1 Micro-ondes Samsung 23L (P28)[/{C_PRIMARY}]",
            border_style=C_ACCENT,
        )
        self.console.print(p_info)

        t_totaux = Table(
            title=f"[{C_GOLD} bold]3. COÛT TOTAL PAR ENSEIGNE DU PANIER DE RENTRÉE[/{C_GOLD} bold]",
            border_style=C_SECONDARY,
            header_style=f"bold {C_GOLD}",
        )
        t_totaux.add_column("Stratégie d'achat", style=C_PRIMARY, width=44)
        t_totaux.add_column("Total du panier", style=f"bold {C_SUCCESS}", justify="right", width=20)
        t_totaux.add_column("Observation", style=C_MUTED, width=26)

        t_totaux.add_row(
            "Marché Lagune (achat complet chez cette enseigne)",
            _fcfa(self.r.panier_totaux.get("Marché Lagune")),
            f"[{C_ALERT}]Pénalisé par anomalie Spark 20[/{C_ALERT}]",
        )
        t_totaux.add_row(
            "Baobab Shop (achat complet chez cette enseigne)",
            _fcfa(self.r.panier_totaux.get("Baobab Shop")),
            f"[{C_ORANGE}]Très compétitif[/{C_ORANGE}]",
        )
        t_totaux.add_row(
            "Comptoir Ivoire (achat complet chez cette enseigne)",
            _fcfa(self.r.panier_totaux.get("Comptoir Ivoire")),
            f"[{C_GOLD} bold]Meilleure enseigne unique[/{C_GOLD} bold]",
        )
        t_totaux.add_row(
            "★ Panier Optimisé (achat au moins cher par produit)",
            _fcfa(self.r.panier_optimise["total"]),
            f"[{C_SUCCESS} bold]Stratégie la plus économique[/{C_SUCCESS} bold]",
        )

        self.console.print(t_totaux)

        eco = self.r.panier_economie
        if eco:
            p_eco = Panel(
                f"[{C_GOLD} bold]💡 ÉCONOMIE DU MÉLANGE OPTIMISÉ :[/{C_GOLD} bold] "
                f"[{C_SUCCESS} bold]{_fcfa(eco['economie_fcfa'])} ({eco['economie_pct']} %)[/{C_SUCCESS} bold]\n"
                f"[{C_PRIMARY}]Économisés par rapport à la meilleure boutique unique ([bold]{eco['meilleure_enseigne_unique']}[/bold]) ![/{C_PRIMARY}]",
                border_style=C_SUCCESS,
            )
            self.console.print(p_eco)

        # Détail du mélange
        t_opt = Table(
            title=f"[{C_PRIMARY} bold]DÉTAIL DES ACHATS DU PANIER OPTIMISÉ[/{C_PRIMARY} bold]",
            border_style=C_PRIMARY,
            header_style=f"bold {C_PRIMARY}",
        )
        t_opt.add_column("Produit", style=C_PRIMARY, width=30)
        t_opt.add_column("Quantité", style=C_ACCENT, justify="center", width=10)
        t_opt.add_column("Enseigne retenue", style=C_SUCCESS, width=18)
        t_opt.add_column("Prix unitaire", style=C_BLUE, justify="right", width=16)
        t_opt.add_column("Sous-total", style=f"bold {C_GOLD}", justify="right", width=16)

        for l in self.r.panier_optimise["lignes"]:
            t_opt.add_row(
                l["produit"],
                f"x {l['quantite']}",
                l["enseigne"],
                _fcfa(l["prix_unitaire"]),
                _fcfa(l["sous_total"]),
            )

        self.console.print(t_opt)
        self._pause()

    # ------------------------------------------------------------- 4. HISTORIQUE
    def afficher_historique(self) -> None:
        """[4] Affiche l'analyse Black Friday et les plus fortes variations."""
        self.console.print()

        t_bf = Table(
            title=f"[{C_GOLD} bold]4. ANALYSE DU BLACK FRIDAY (SEMAINE DU 24 AU 30 NOV. 2025 VS ANNÉE)[/{C_GOLD} bold]",
            border_style=C_SECONDARY,
            header_style=f"bold {C_GOLD}",
        )
        t_bf.add_column("Enseigne", style=C_PRIMARY, width=18)
        t_bf.add_column("Prix moyen annuel", style=C_BLUE, justify="right", width=18)
        t_bf.add_column("Prix Black Friday", style=f"bold {C_GOLD}", justify="right", width=18)
        t_bf.add_column("Variation %", style=C_MAGENTA, justify="right", width=14)
        t_bf.add_column("Constat & Comportement", style=C_SUCCESS, width=32)

        for b in self.r.black_friday:
            constat = (
                f"[{C_SUCCESS}]✓ Vraie promotion en ligne[/{C_SUCCESS}]"
                if b["est_bonne_affaire"]
                else f"[{C_ALERT}]✗ Pas de baisse (boutique physique)[/{C_ALERT}]"
            )
            t_bf.add_row(
                b["enseigne"],
                _fcfa(b["prix_moyen_annee"]),
                _fcfa(b["prix_moyen_bf"]),
                _pct(b["ecart_pct"], signe=True),
                constat,
            )

        self.console.print(t_bf)

        # Réponse explicite à "Quand fallait-il acheter ?"
        p_verdict = Panel(
            f"[{C_GOLD} bold]💡 RÉPONSE À LA CONSIGNE : QUAND FALLAIT-IL ACHETER ?[/{C_GOLD} bold]\n\n"
            f"[{C_SUCCESS} bold]• Chez Baobab Shop (-11.59 %) & Marché Lagune (-11.16 %) :[/{C_SUCCESS} bold]\n"
            f"  [{C_PRIMARY}]OUI, il fallait acheter impérativement pendant la semaine du Black Friday (24 au 30 nov. 2025) !\n"
            f"  C'est le minimum historique de toute l'année, juste avant le pic des fêtes de Noël en décembre.[/{C_PRIMARY}]\n\n"
            f"[{C_ALERT} bold]• Chez Comptoir Ivoire (+3.72 %) :[/{C_ALERT} bold]\n"
            f"  [{C_PRIMARY}]NON, il ne fallait SURTOUT PAS acheter au Black Friday (novembre étant son mois le plus cher).\n"
            f"  La boutique d'Adjamé ne fait pas de Black Friday ; son meilleur moment était en septembre-octobre 2026.[/{C_PRIMARY}]",
            border_style=C_GOLD,
        )
        self.console.print(p_verdict)

        # Plus fortes variations
        t_var = Table(
            title=f"[{C_ACCENT} bold]TOP 5 DES PLUS FORTES VARIATIONS ANNUELLES DE PRIX[/{C_ACCENT} bold]",
            border_style=C_PRIMARY,
            header_style=f"bold {C_ACCENT}",
        )
        t_var.add_column("Produit", style=C_PRIMARY, width=32)
        t_var.add_column("Enseigne", style=C_ORANGE, width=16)
        t_var.add_column("Prix début (Nov 2025)", style=C_BLUE, justify="right", width=20)
        t_var.add_column("Prix fin (Oct 2026)", style=C_GOLD, justify="right", width=20)
        t_var.add_column("Variation %", style=C_MAGENTA, justify="right", width=14)

        for s in self.r.variations_historique:
            t_var.add_row(
                s["produit_nom"],
                s["source"],
                _fcfa(s["premier"]),
                _fcfa(s["dernier"]),
                _pct(s["variation_pct"], signe=True),
            )

        self.console.print(t_var)
        self._pause()

    # ------------------------------------------------------------- 5. JOURNAL
    def afficher_journal(self) -> None:
        """[5] Affiche le journal des anomalies de nettoyage."""
        self.console.print()

        journal_path = os.path.join("output", "journal.txt")
        contenu = ""
        if os.path.exists(journal_path):
            with open(journal_path, encoding="utf-8") as f:
                contenu = f.read().strip()

        p_journal = Panel(
            f"[{C_GOLD} bold]5. JOURNAL DE NETTOYAGE & QUALITÉ DES DONNÉES (output/journal.txt)[/{C_GOLD} bold]\n\n"
            f"[{C_PRIMARY}]{contenu or 'Aucune anomalie enregistrée.'}[/{C_PRIMARY}]\n\n"
            f"[{C_SUCCESS}]✓ Toutes les anomalies ont été traitées proprement sans faire planter le programme.[/{C_SUCCESS}]",
            border_style=C_ORANGE,
        )
        self.console.print(p_journal)
        self._pause()

    # ------------------------------------------------------------- 6. PERFORMANCES
    def afficher_performances(self) -> None:
        """[6] Affiche les temps d'exécution et le benchmark de complexité."""
        self.console.print()

        t_perf = Table(
            title=f"[{C_GOLD} bold]6. CHRONOMÉTRAGE DU PIPELINE DE TRAITEMENT[/{C_GOLD} bold]",
            border_style=C_SECONDARY,
            header_style=f"bold {C_GOLD}",
        )
        t_perf.add_column("Étape du pipeline", style=C_PRIMARY, width=32)
        t_perf.add_column("Durée d'exécution", style=f"bold {C_GOLD}", justify="right", width=18)
        t_perf.add_column("Part du temps total", style=C_MAGENTA, justify="right", width=20)

        for l in self.r.performances:
            t_perf.add_row(
                l["etape"],
                f"{l['secondes'] * 1000:.1f} ms",
                _pct(l["part_pct"]),
            )

        self.console.print(t_perf)

        b = self.r.benchmark_complexite
        if b:
            p_bench = Panel(
                f"[{C_GOLD} bold]JUSTIFICATION DES CHOIX DE STRUCTURES DE DONNÉES ({b['nb_lignes']:,} RELEVÉS) :[/{C_GOLD} bold]\n\n"
                f"[{C_PRIMARY}]• Volume historique traité : [bold]{b['nb_lignes']:,} lignes[/bold]\n"
                f"• Parcours linéaire séquentiel O(N) sur liste : [{C_ALERT} bold]{b['liste_s'] * 1000:.1f} ms[/{C_ALERT} bold]\n"
                f"• Recherche par table de hachage O(1) (dictionnaire clé composite) : [{C_SUCCESS} bold]{b['dict_s'] * 1000:.2f} ms[/{C_SUCCESS} bold]\n\n"
                f"[{C_GOLD} bold]✓ Accélération obtenue : le dictionnaire est environ {b['facteur']:.0f}× plus rapide que la liste ![/{C_GOLD} bold][/{C_PRIMARY}]",
                border_style=C_SUCCESS,
            )
            self.console.print(p_bench)

        self._pause()

    # ------------------------------------------------------------- 7. TKINTER
    def lancer_tkinter(self) -> None:
        """[7] Lance l'interface graphique Tkinter depuis la console."""
        from .console_view import TkView

        self.console.print(
            f"\n[{C_SUCCESS} bold]🖥 Lancement de l'interface graphique Tkinter (Thème Dark Slate)...[/{C_SUCCESS} bold]"
        )
        self.console.print(
            f"[{C_MUTED}]Fermez la fenêtre Tkinter pour revenir automatiquement au menu console Rich.[/{C_MUTED}]\n"
        )

        try:
            fenetre = TkView(self.r)
            fenetre.mainloop()
        except Exception as e:
            self.console.print(f"[{C_ALERT} bold]Erreur lors de l'ouverture de Tkinter : {e}[/{C_ALERT} bold]")

        self.console.print(f"[{C_PRIMARY}]✓ Retour au menu console Rich.[/{C_PRIMARY}]")

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional, Sequence

from ..controllers.comparateur_controller import ResultatsAnalyse


def _fcfa(valeur: Optional[float]) -> str:
    if valeur is None:
        return "-"
    return f"{valeur:,.0f}".replace(",", " ") + " FCFA"


def _pct(valeur: Optional[float], signe: bool = False) -> str:
    if valeur is None:
        return "-"
    return f"{valeur:+.1f} %" if signe else f"{valeur:.1f} %"


class TkView(tk.Tk):
    def __init__(self, resultats: ResultatsAnalyse):
        super().__init__()
        self.r = resultats
        self.title("Comparateur de prix")
        self.geometry("1000x600")
        self.minsize(800, 480)

        self._entrees: list[tuple[str, str, Callable[[], None]]] = [
            ("1", "Meilleure offre par produit", self.afficher_resume),
            ("2", "Synthèse par enseigne", self.afficher_synthese),
            ("3", "Panier", self.afficher_panier),
            ("4", "Historique : plus fortes variations", self.afficher_historique),
            ("5", "Articles non rattachés", self.afficher_non_rattaches),
            ("6", "Performances", self.afficher_performances),
        ]

        self._style()
        self._construire_menu_barre()
        self._construire_interface()
        self.afficher_resume()

    # ------------------------------------------------------------------ UI
    def _style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Titre.TLabel", font=("Segoe UI", 15, "bold"))
        style.configure("Info.TLabel", font=("Segoe UI", 10))
        style.configure("Bon.TLabel", font=("Segoe UI", 10, "bold"), foreground="#1a7f37")
        style.configure("Menu.TButton", font=("Segoe UI", 10), padding=8, anchor="w")
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _construire_menu_barre(self) -> None:
        barre = tk.Menu(self)

        fichier = tk.Menu(barre, tearoff=False)
        fichier.add_command(label="Quitter", accelerator="Ctrl+Q", command=self.destroy)
        barre.add_cascade(label="Fichier", menu=fichier)

        affichage = tk.Menu(barre, tearoff=False)
        for numero, libelle, action in self._entrees:
            affichage.add_command(label=libelle, accelerator=f"Ctrl+{numero}", command=action)
            self.bind(f"<Control-Key-{numero}>", lambda _e, a=action: a())
        barre.add_cascade(label="Affichage", menu=affichage)

        aide = tk.Menu(barre, tearoff=False)
        aide.add_command(
            label="À propos",
            command=lambda: messagebox.showinfo(
                "À propos", "Comparateur de prix\nInterface Tkinter", parent=self
            ),
        )
        barre.add_cascade(label="Aide", menu=aide)

        self.bind("<Control-q>", lambda _e: self.destroy())
        self.config(menu=barre)

    def _construire_interface(self) -> None:
        # Panneau latéral
        lateral = ttk.Frame(self, padding=10)
        lateral.pack(side="left", fill="y")
        ttk.Label(lateral, text="MENU", style="Titre.TLabel").pack(anchor="w", pady=(0, 10))
        for _numero, libelle, action in self._entrees:
            ttk.Button(lateral, text=libelle, style="Menu.TButton", command=action).pack(
                fill="x", pady=2
            )
        ttk.Separator(lateral).pack(fill="x", pady=10)
        ttk.Button(lateral, text="Quitter", style="Menu.TButton", command=self.destroy).pack(fill="x")

        # Zone de contenu
        self.contenu = ttk.Frame(self, padding=15)
        self.contenu.pack(side="left", fill="both", expand=True)

        # Barre de statut
        self.statut = tk.StringVar()
        ttk.Label(self, textvariable=self.statut, relief="sunken", anchor="w", padding=3).pack(
            side="bottom", fill="x"
        )

    # ------------------------------------------------------------- Helpers
    def _vider(self, titre: str) -> None:
        for widget in self.contenu.winfo_children():
            widget.destroy()
        ttk.Label(self.contenu, text=titre, style="Titre.TLabel").pack(anchor="w", pady=(0, 10))
        self.statut.set(titre)

    def _tableau(
        self,
        colonnes: Sequence[str],
        lignes: Sequence[Sequence[str]],
        droite: Sequence[str] = (),
        hauteur: Optional[int] = None,
    ) -> ttk.Treeview:
        cadre = ttk.Frame(self.contenu)
        cadre.pack(fill="both", expand=True)

        arbre = ttk.Treeview(cadre, columns=colonnes, show="headings", height=hauteur or 10)
        for col in colonnes:
            arbre.heading(col, text=col)
            arbre.column(col, anchor="e" if col in droite else "w", width=120, stretch=True)
        arbre.tag_configure("pair", background="#f3f6fa")

        for i, ligne in enumerate(lignes):
            arbre.insert("", "end", values=list(ligne), tags=("pair",) if i % 2 == 0 else ())

        vs = ttk.Scrollbar(cadre, orient="vertical", command=arbre.yview)
        hs = ttk.Scrollbar(cadre, orient="horizontal", command=arbre.xview)
        arbre.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        arbre.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        cadre.rowconfigure(0, weight=1)
        cadre.columnconfigure(0, weight=1)
        return arbre

    def _info(self, texte: str, style: str = "Info.TLabel") -> None:
        ttk.Label(self.contenu, text=texte, style=style, wraplength=700, justify="left").pack(
            anchor="w", pady=(8, 0)
        )

    # ------------------------------------------------------------- Écrans
    def afficher_erreur(self, message: str) -> None:
        messagebox.showerror("Erreur", message)

    def afficher_resume(self) -> None:
        self._vider("Meilleure offre par produit")
        lignes = [
            (
                l["produit"],
                l["enseigne"] or "rupture partout",
                _fcfa(l["prix"]),
                _pct(l["ecart_pct"]),
            )
            for l in self.r.resume
        ]
        self._tableau(("Produit", "Meilleur", "Prix", "Écart %"), lignes, droite=("Prix", "Écart %"))

    def afficher_synthese(self) -> None:
        self._vider("Synthèse par enseigne")
        lignes = []
        for l in self.r.synthese:
            note = f"{l['note_moyenne']:.1f}" if l["note_moyenne"] is not None else "-"
            lignes.append(
                (
                    l["enseigne"],
                    l["offres"],
                    l["disponibles"],
                    l["victoires"],
                    _pct(l["surcout_moyen_pct"]),
                    note,
                )
            )
        colonnes = ("Enseigne", "Offres", "Dispo", "Produits gagnés", "Surcoût moyen", "Note moy.")
        self._tableau(colonnes, lignes, droite=colonnes[1:])
        if self.r.meilleure_enseigne:
            self._info(f"Enseigne la moins chère : {self.r.meilleure_enseigne}", "Bon.TLabel")
        if self.r.produits_sans_offre:
            self._info("Sans offre disponible : " + ", ".join(self.r.produits_sans_offre))

    def afficher_panier(self) -> None:
        self._vider(f"Panier ({len(self.r.contenu_panier)} produits)")
        lignes = [
            (
                f"Tout chez {enseigne}",
                _fcfa(total) if total is not None else "incomplet",
            )
            for enseigne, total in self.r.totaux_panier.items()
        ]
        lignes.append(("Meilleur mélange", _fcfa(self.r.panier_optimise["total"])))
        self._tableau(("Stratégie", "Total"), lignes, droite=("Total",))
        if self.r.economie_panier is not None:
            self._info(f"Économie du mélange : {_fcfa(self.r.economie_panier)}", "Bon.TLabel")
        if self.r.panier_optimise["introuvables"]:
            self._info("Introuvables : " + ", ".join(self.r.panier_optimise["introuvables"]))

    def afficher_historique(self) -> None:
        self._vider("Plus fortes variations de prix")
        lignes = [
            (
                s["produit_id"],
                s["source"],
                _fcfa(s["premier"]),
                _fcfa(s["dernier"]),
                _pct(s["variation_pct"], signe=True),
            )
            for s in self.r.variations_historique
        ]
        colonnes = ("Produit", "Source", "Premier", "Dernier", "Variation")
        self._tableau(colonnes, lignes, droite=("Premier", "Dernier", "Variation"))

    def afficher_non_rattaches(self) -> None:
        total = len(self.r.non_rattaches)
        self._vider("Articles non rattachés")
        self._info(f"Articles non rattachés au catalogue : {total} "
                    f"(liste complète dans output/non_rattaches.txt)")
        lignes = [(a.enseigne, a.designation) for a in self.r.non_rattaches]
        self._tableau(("Enseigne", "Désignation"), lignes)

    def afficher_performances(self) -> None:
        self._vider("Performances")
        lignes = [
            (l["etape"], f"{l['secondes'] * 1000:.1f} ms", _pct(l["part_pct"]))
            for l in self.r.performances
        ]
        self._tableau(("Étape", "Durée", "Part"), lignes, droite=("Durée", "Part"))
        b = self.r.benchmark
        if b and b.get("facteur"):
            self._info(
                f"Recherche par id ({b['nb_produits']} produits) : le dictionnaire est "
                f"{b['facteur']:.1f}× plus rapide que le parcours de liste."
            )
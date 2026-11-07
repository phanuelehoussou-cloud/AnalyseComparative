import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable, Optional, Sequence

from ..controllers.comparateur_controller import ResultatsAnalyse

# =====================================================================
# PALETTE DE COULEURS MODERNE : DARK SLATE & NEON ACCENTS
# =====================================================================
BG_DARK = "#0f172a"          # Arrière-plan principal (Slate 900)
CARD_BG = "#1e293b"          # Arrière-plan des cartes et tableaux (Slate 800)
SURFACE_ALT = "#334155"      # Éléments surélevés / En-têtes (Slate 700)
BORDER_COLOR = "#475569"     # Bordures et séparateurs (Slate 600)
TEXT_PRIMARY = "#f8fafc"     # Texte principal blanc pur (Slate 50)
TEXT_MUTED = "#94a3b8"       # Texte secondaire / Muted (Slate 400)
ACCENT_CYAN = "#38bdf8"      # Accent principal cyan éclatant (Sky 400)
ACCENT_INDIGO = "#6366f1"    # Accent d'action indigo (Indigo 500)
SUCCESS_EMERALD = "#34d399"  # Vert émeraude (victoires, économies)
WARNING_AMBER = "#fbbf24"    # Ambre doux (alertes légères)
DANGER_ROSE = "#f87171"      # Rouge corail doux (anomalies)
ROW_ALT = "#172337"          # Alternance de lignes dans les tableaux


def _fcfa(valeur: Optional[float]) -> str:
    if valeur is None:
        return "-"
    return f"{valeur:,.0f}".replace(",", " ") + " FCFA"


def _pct(valeur: Optional[float], signe: bool = False) -> str:
    if valeur is None:
        return "-"
    return f"{valeur:+.1f} %" if signe else f"{valeur:.1f} %"


class TkView(tk.Tk):
    """Interface graphique avec thème sombre moderne (Dark Slate & Cyan/Emerald)

    et navigation fluide par page dédiée au menu.
    """

    def __init__(self, resultats: ResultatsAnalyse):
        super().__init__()
        self.r = resultats
        self.title("Analyse Comparative de Marché — Abidjan (DA Python L2)")
        self.geometry("1140x730")
        self.minsize(920, 560)
        self.configure(bg=BG_DARK)

        # Mapping des choix du menu : numéro -> (titre, description, méthode)
        self.menu_options: dict[str, tuple[str, str, Callable[[], None]]] = {
            "1": (
                "Comparatif multi-enseignes",
                "Prix payé chez chaque enseigne (≥ 2 enseignes), moins cher et écarts (export CSV).",
                self.afficher_comparatif,
            ),
            "2": (
                "Synthèse des enseignes & Top 3 des gains",
                "Victoires par enseigne, surcoût moyen et les 3 produits où comparer rapporte le plus.",
                self.afficher_synthese,
            ),
            "3": (
                "Panier de rentrée (5 articles)",
                "Coût chez chaque enseigne, meilleur mélange optimisé et calcul des économies.",
                self.afficher_panier,
            ),
            "4": (
                "Historique des prix & Black Friday",
                "Impact de la semaine du Black Friday (24-30 nov. 2025) vs année et plus fortes variations.",
                self.afficher_historique,
            ),
            "5": (
                "Journal de nettoyage & Qualité des données",
                "Anomalies repérées et traitées (formats textes, doublons, prix aberrants).",
                self.afficher_journal,
            ),
            "6": (
                "Performances & Analyse de Complexité",
                "Temps d'exécution des étapes et benchmark O(1) vs O(N) sur les 20 876 relevés.",
                self.afficher_performances,
            ),
        }

        self._style()
        self._construire_menu_barre()

        # Cadre conteneur principal
        self.conteneur = ttk.Frame(self, style="Dark.TFrame")
        self.conteneur.pack(fill="both", expand=True)

        # Barre de statut inférieure
        self.statut = tk.StringVar(value="Prêt")
        self.barre_statut = tk.Label(
            self,
            textvariable=self.statut,
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor="w",
            padx=10,
            pady=5,
            relief="flat",
        )
        self.barre_statut.pack(side="bottom", fill="x")

        # Raccourci Échap pour revenir au menu
        self.bind("<Escape>", lambda _e: self.afficher_menu_principal())

        # Au démarrage : Affichage de la page dédiée au menu
        self.afficher_menu_principal()

    # ------------------------------------------------------------------ Styles
    def _style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Configuration globale des cadres
        style.configure("Dark.TFrame", background=BG_DARK)
        style.configure("Card.TFrame", background=CARD_BG)
        style.configure("Surface.TFrame", background=SURFACE_ALT)

        # Configuration des labels
        style.configure("Dark.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Segoe UI", 9))
        style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT_PRIMARY, font=("Segoe UI", 9))
        style.configure("TitrePrincipal.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY, font=("Segoe UI", 16, "bold"))
        style.configure("SousTitrePrincipal.TLabel", background=BG_DARK, foreground=TEXT_MUTED, font=("Segoe UI", 10))
        style.configure("TitrePage.TLabel", background=BG_DARK, foreground=ACCENT_CYAN, font=("Segoe UI", 13, "bold"))
        style.configure("SectionTitre.TLabel", background=BG_DARK, foreground=ACCENT_CYAN, font=("Segoe UI", 11, "bold"))
        style.configure("Info.TLabel", background=BG_DARK, foreground=TEXT_MUTED, font=("Segoe UI", 9))
        style.configure("Bon.TLabel", background=BG_DARK, foreground=SUCCESS_EMERALD, font=("Segoe UI", 10, "bold"))
        style.configure("Alerte.TLabel", background=BG_DARK, foreground=DANGER_ROSE, font=("Segoe UI", 10, "bold"))

        # Cadres de groupe
        style.configure("TLabelframe", background=CARD_BG, bordercolor=BORDER_COLOR)
        style.configure("TLabelframe.Label", background=CARD_BG, foreground=ACCENT_CYAN, font=("Segoe UI", 10, "bold"))

        # Boutons
        style.configure(
            "MenuCard.TButton",
            background=CARD_BG,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 10, "bold"),
            padding=10,
            borderwidth=1,
            relief="solid",
        )
        style.map(
            "MenuCard.TButton",
            background=[("active", SURFACE_ALT), ("pressed", ACCENT_INDIGO)],
            foreground=[("active", ACCENT_CYAN)],
        )

        style.configure(
            "Action.TButton",
            background=ACCENT_INDIGO,
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            padding=(10, 6),
            borderwidth=0,
        )
        style.map(
            "Action.TButton",
            background=[("active", "#4f46e5"), ("pressed", "#4338ca")],
        )

        style.configure(
            "Retour.TButton",
            background=SURFACE_ALT,
            foreground=TEXT_PRIMARY,
            font=("Segoe UI", 9, "bold"),
            padding=(12, 6),
            borderwidth=0,
        )
        style.map(
            "Retour.TButton",
            background=[("active", BORDER_COLOR), ("pressed", ACCENT_CYAN)],
            foreground=[("active", ACCENT_CYAN)],
        )

        # Séparateurs
        style.configure("TSeparator", background=BORDER_COLOR)

        # Tableaux Treeview
        style.configure(
            "Treeview",
            background=CARD_BG,
            fieldbackground=CARD_BG,
            foreground=TEXT_PRIMARY,
            rowheight=28,
            font=("Segoe UI", 9),
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=SURFACE_ALT,
            foreground=ACCENT_CYAN,
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padding=5,
        )
        style.map(
            "Treeview.Heading",
            background=[("active", BORDER_COLOR)],
            foreground=[("active", "#ffffff")],
        )

        # Scrollbars
        style.configure(
            "Vertical.TScrollbar",
            background=SURFACE_ALT,
            troughcolor=BG_DARK,
            bordercolor=BG_DARK,
            arrowcolor=TEXT_MUTED,
        )
        style.configure(
            "Horizontal.TScrollbar",
            background=SURFACE_ALT,
            troughcolor=BG_DARK,
            bordercolor=BG_DARK,
            arrowcolor=TEXT_MUTED,
        )

    def _construire_menu_barre(self) -> None:
        barre = tk.Menu(self, bg=CARD_BG, fg=TEXT_PRIMARY, activebackground=SURFACE_ALT, activeforeground=ACCENT_CYAN)

        fichier = tk.Menu(barre, tearoff=False, bg=CARD_BG, fg=TEXT_PRIMARY, activebackground=SURFACE_ALT, activeforeground=ACCENT_CYAN)
        fichier.add_command(label="Menu Principal", accelerator="Échap", command=self.afficher_menu_principal)
        fichier.add_command(label="Ouvrir le dossier output", command=self._ouvrir_dossier_output)
        fichier.add_separator()
        fichier.add_command(label="Quitter", accelerator="Ctrl+Q", command=self.destroy)
        barre.add_cascade(label="Fichier", menu=fichier)

        navigation = tk.Menu(barre, tearoff=False, bg=CARD_BG, fg=TEXT_PRIMARY, activebackground=SURFACE_ALT, activeforeground=ACCENT_CYAN)
        for num, (titre, _, action) in self.menu_options.items():
            navigation.add_command(label=f"[{num}] {titre}", command=action)
        barre.add_cascade(label="Navigation", menu=navigation)

        aide = tk.Menu(barre, tearoff=False, bg=CARD_BG, fg=TEXT_PRIMARY, activebackground=SURFACE_ALT, activeforeground=ACCENT_CYAN)
        aide.add_command(
            label="À propos du sujet",
            command=lambda: messagebox.showinfo(
                "À propos",
                "Analyse comparative de marché\nDA Python · L2 Computer Science · Séance 3\n"
                "Comparateur Marché Lagune, Baobab Shop & Comptoir Ivoire.",
                parent=self,
            ),
        )
        barre.add_cascade(label="Aide", menu=aide)

        self.bind("<Control-q>", lambda _e: self.destroy())
        self.bind("<Control-Q>", lambda _e: self.destroy())
        self.config(menu=barre)

    def _ouvrir_dossier_output(self) -> None:
        dossier = os.path.abspath("output")
        if os.name == "nt":
            os.startfile(dossier)
        else:
            subprocess.run(["xdg-open", dossier], check=False)

    def _vider_conteneur(self) -> None:
        for widget in self.conteneur.winfo_children():
            widget.destroy()

    # -------------------------------------------------- PAGE DÉDIÉE AU MENU
    def afficher_menu_principal(self) -> None:
        """Page d'accueil dédiée au menu avec choix par saisie ou par clic."""
        self._vider_conteneur()
        self.statut.set("Menu Principal — Entrez votre choix (1 à 6) ou cliquez sur une option.")

        cadre_menu = ttk.Frame(self.conteneur, style="Dark.TFrame", padding=30)
        cadre_menu.pack(fill="both", expand=True)

        # En-tête
        ttk.Label(
            cadre_menu,
            text="📊 ANALYSE COMPARATIVE DE MARCHÉ — ABIDJAN",
            style="TitrePrincipal.TLabel",
        ).pack(anchor="center", pady=(0, 4))

        ttk.Label(
            cadre_menu,
            text="Marché Lagune (CSV) · Baobab Shop (JSON) · Comptoir Ivoire (Excel) | DA Python L2",
            style="SousTitrePrincipal.TLabel",
        ).pack(anchor="center", pady=(0, 20))

        ttk.Separator(cadre_menu).pack(fill="x", pady=(0, 16))

        # Cadre de saisie du choix
        cadre_saisie = ttk.LabelFrame(cadre_menu, text="  Saisie directe de votre choix  ", padding=14)
        cadre_saisie.pack(fill="x", pady=(0, 16))

        ttk.Label(
            cadre_saisie,
            text="Entrez le numéro de votre choix (1 à 6, ou 0 pour quitter) :",
            style="Card.TLabel",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left", padx=(8, 12))

        self.var_choix = tk.StringVar()
        entree_choix = tk.Entry(
            cadre_saisie,
            textvariable=self.var_choix,
            width=6,
            font=("Segoe UI", 12, "bold"),
            bg=BG_DARK,
            fg=ACCENT_CYAN,
            insertbackground=ACCENT_CYAN,
            relief="solid",
            bd=1,
            justify="center",
        )
        entree_choix.pack(side="left", padx=(0, 12))
        entree_choix.focus_set()

        def valider_choix(_event=None):
            choix = self.var_choix.get().strip()
            if choix == "0":
                self.destroy()
            elif choix in self.menu_options:
                _, _, action = self.menu_options[choix]
                action()
            else:
                messagebox.showwarning(
                    "Choix invalide",
                    f"Le choix '{choix}' est invalide.\nVeuillez saisir un numéro entre 1 et 6 (ou 0 pour quitter).",
                    parent=self,
                )
                self.var_choix.set("")
                entree_choix.focus_set()

        entree_choix.bind("<Return>", valider_choix)
        btn_valider = ttk.Button(cadre_saisie, text="➜ Accéder", style="Action.TButton", command=valider_choix)
        btn_valider.pack(side="left")

        # Liste des options présentées sous forme de cartes cliquables
        cadre_options = ttk.Frame(cadre_menu, style="Dark.TFrame")
        cadre_options.pack(fill="both", expand=True)

        for num, (titre, desc, action) in self.menu_options.items():
            cadre_carte = ttk.Frame(cadre_options, style="Dark.TFrame", padding=(0, 4))
            cadre_carte.pack(fill="x")

            btn = ttk.Button(
                cadre_carte,
                text=f"  [{num}]  {titre}",
                style="MenuCard.TButton",
                command=action,
            )
            btn.pack(side="left", fill="x", expand=True)

            ttk.Label(
                cadre_carte,
                text=desc,
                style="Info.TLabel",
            ).pack(side="left", padx=(15, 0))

        # Ligne d'action inférieure
        cadre_bas = ttk.Frame(cadre_menu, style="Dark.TFrame", padding=(0, 16))
        cadre_bas.pack(fill="x")

        ttk.Button(
            cadre_bas,
            text="📁 Ouvrir le dossier des résultats (output/)",
            style="Action.TButton",
            command=self._ouvrir_dossier_output,
        ).pack(side="left")

        ttk.Button(
            cadre_bas,
            text="✖ Quitter l'application [0]",
            style="Retour.TButton",
            command=self.destroy,
        ).pack(side="right")

    # ------------------------------------------------- BANDEAU DE NAVIGATION
    def _creer_entete_page(self, titre: str, sous_titre: str = "") -> ttk.Frame:
        """Bandeau de navigation présent en haut de chaque page de résultat."""
        cadre_entete = ttk.Frame(self.conteneur, style="Dark.TFrame", padding=(16, 12, 16, 6))
        cadre_entete.pack(fill="x")

        btn_retour = ttk.Button(
            cadre_entete,
            text="⬅ Menu Principal [Échap]",
            style="Retour.TButton",
            command=self.afficher_menu_principal,
        )
        btn_retour.pack(side="left", padx=(0, 15))

        cadre_titres = ttk.Frame(cadre_entete, style="Dark.TFrame")
        cadre_titres.pack(side="left", fill="x", expand=True)

        ttk.Label(cadre_titres, text=titre, style="TitrePage.TLabel").pack(anchor="w")
        if sous_titre:
            ttk.Label(cadre_titres, text=sous_titre, style="Info.TLabel").pack(anchor="w")

        btn_dossier = ttk.Button(
            cadre_entete,
            text="📁 output/",
            style="Action.TButton",
            command=self._ouvrir_dossier_output,
        )
        btn_dossier.pack(side="right")

        ttk.Separator(self.conteneur).pack(fill="x", padx=16, pady=(6, 10))

        cadre_page = ttk.Frame(self.conteneur, style="Dark.TFrame", padding=(16, 0, 16, 12))
        cadre_page.pack(fill="both", expand=True)
        return cadre_page

    def _tableau(
        self,
        parent: ttk.Frame,
        colonnes: Sequence[str],
        lignes: Sequence[Sequence[str]],
        droite: Sequence[str] = (),
        largeurs: Optional[dict[str, int]] = None,
        hauteur: Optional[int] = None,
    ) -> ttk.Treeview:
        cadre = ttk.Frame(parent, style="Dark.TFrame")
        cadre.pack(fill="both", expand=True)

        arbre = ttk.Treeview(cadre, columns=colonnes, show="headings", height=hauteur or 10)
        largeurs = largeurs or {}
        for col in colonnes:
            arbre.heading(col, text=col)
            lar = largeurs.get(col, 130)
            align = "e" if col in droite else "w"
            arbre.column(col, anchor=align, width=lar, minwidth=60, stretch=True)

        # Alternance de lignes subtile sur thème sombre
        arbre.tag_configure("pair", background=ROW_ALT)

        for i, ligne in enumerate(lignes):
            arbre.insert("", "end", values=list(ligne), tags=("pair",) if i % 2 == 0 else ())

        vs = ttk.Scrollbar(cadre, orient="vertical", command=arbre.yview, style="Vertical.TScrollbar")
        hs = ttk.Scrollbar(cadre, orient="horizontal", command=arbre.xview, style="Horizontal.TScrollbar")
        arbre.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        arbre.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        cadre.rowconfigure(0, weight=1)
        cadre.columnconfigure(0, weight=1)
        return arbre

    # ------------------------------------------------------------- PAGES DE RÉSULTATS
    def afficher_comparatif(self) -> None:
        """[1] Comparatif des prix multi-enseignes."""
        self._vider_conteneur()
        total_comp = len(self.r.comparatif_multi_enseignes)
        self.statut.set(f"Option 1 : Comparatif multi-enseignes — {total_comp} produits analysés.")

        page = self._creer_entete_page(
            "1. Comparatif des prix multi-enseignes",
            f"Produits disponibles dans au moins 2 enseignes ({total_comp} produits) avec prix, gagnant et écarts.",
        )

        lignes = [
            (
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
            for l in self.r.comparatif_multi_enseignes
        ]
        colonnes = (
            "ID",
            "Produit",
            "Marché Lagune",
            "Baobab Shop",
            "Comptoir Ivoire",
            "Moins cher",
            "Prix min",
            "Écart FCFA",
            "Écart %",
        )
        largeurs = {
            "ID": 50,
            "Produit": 240,
            "Marché Lagune": 120,
            "Baobab Shop": 120,
            "Comptoir Ivoire": 120,
            "Moins cher": 120,
            "Prix min": 110,
            "Écart FCFA": 110,
            "Écart %": 85,
        }
        self._tableau(
            page,
            colonnes,
            lignes,
            droite=(
                "Marché Lagune",
                "Baobab Shop",
                "Comptoir Ivoire",
                "Prix min",
                "Écart FCFA",
                "Écart %",
            ),
            largeurs=largeurs,
        )

        ttk.Label(
            page,
            text=f"✓ Tableau exporté au format CSV : {self.r.chemin_csv_comparatif.name} "
            f"(disponible dans le dossier output)",
            style="Bon.TLabel",
        ).pack(anchor="w", pady=(8, 0))

    def afficher_synthese(self) -> None:
        """[2] Synthèse par enseigne et Top 3 des gains."""
        self._vider_conteneur()
        self.statut.set("Option 2 : Synthèse des enseignes et Top 3 des opportunités de comparaison.")

        page = self._creer_entete_page(
            "2. Synthèse par enseigne & Top 3 des gains",
            "Nombre de victoires, surcoût moyen et produits où la comparaison génère les plus fortes économies.",
        )

        # 1. Bilan par enseigne
        lignes = []
        for l in self.r.synthese_enseignes:
            note = f"{l['note_moyenne']:.2f}" if l["note_moyenne"] is not None else "-"
            lignes.append((
                l["enseigne"],
                l["offres"],
                l["disponibles"],
                l["victoires"],
                _pct(l["surcout_moyen_pct"]),
                note,
            ))
        colonnes = (
            "Enseigne",
            "Offres totales",
            "Disponibles",
            "Victoires (moins chère)",
            "Surcoût moyen %",
            "Note moyenne",
        )
        self._tableau(
            page,
            colonnes,
            lignes,
            droite=colonnes[1:],
            largeurs={"Enseigne": 160, "Victoires (moins chère)": 150},
            hauteur=4,
        )

        if self.r.meilleure_enseigne:
            ttk.Label(
                page,
                text=f"🏆 Enseigne la moins chère globalement : {self.r.meilleure_enseigne} "
                f"(remporte le plus de victoires avec le plus faible surcoût moyen)",
                style="Bon.TLabel",
            ).pack(anchor="w", pady=(10, 4))

        # 2. Top 3 des gains
        ttk.Label(
            page,
            text="Top 3 des produits où il y a le plus à gagner en comparant :",
            style="SectionTitre.TLabel",
        ).pack(anchor="w", pady=(12, 4))

        lignes_top = [
            (
                f"#{i+1}",
                l["nom"],
                _fcfa(l["meilleur_prix"]) + f" ({l['meilleure_enseigne']})",
                _fcfa(l["prix_plus_eleve"]),
                _fcfa(l["ecart_fcfa"]),
                _pct(l["ecart_pct"]),
            )
            for i, l in enumerate(self.r.top_3_gains_fcfa)
        ]
        self._tableau(
            page,
            ("Rang", "Produit", "Meilleur prix", "Prix max", "Économie FCFA", "Écart %"),
            lignes_top,
            droite=("Meilleur prix", "Prix max", "Économie FCFA", "Écart %"),
            largeurs={"Rang": 50, "Produit": 250, "Économie FCFA": 130},
            hauteur=4,
        )

    def afficher_panier(self) -> None:
        """[3] Panier de rentrée."""
        self._vider_conteneur()
        self.statut.set("Option 3 : Panier de rentrée — Comparaison des stratégies d'achat.")

        page = self._creer_entete_page(
            "3. Panier de rentrée (Cahier des charges)",
            "1 Tecno Spark 20 (P04), 1 Lenovo IdeaPad 3 (P12), 2 Clés SanDisk 64Go (P14), 1 DD Seagate (P15), 1 Micro-ondes Samsung (P28).",
        )

        # Totaux par enseigne
        lignes_totaux = [
            ("Marché Lagune (achat complet chez cette enseigne)", _fcfa(self.r.panier_totaux.get("Marché Lagune"))),
            ("Baobab Shop (achat complet chez cette enseigne)", _fcfa(self.r.panier_totaux.get("Baobab Shop"))),
            ("Comptoir Ivoire (achat complet chez cette enseigne)", _fcfa(self.r.panier_totaux.get("Comptoir Ivoire"))),
            (
                "★ Panier Optimisé (achat au moins cher par produit)",
                _fcfa(self.r.panier_optimise["total"]),
            ),
        ]
        self._tableau(
            page,
            ("Stratégie d'achat", "Total du panier"),
            lignes_totaux,
            droite=("Total du panier",),
            largeurs={"Stratégie d'achat": 340, "Total du panier": 160},
            hauteur=5,
        )

        eco = self.r.panier_economie
        if eco:
            ttk.Label(
                page,
                text=f"💡 Économie du mélange : {_fcfa(eco['economie_fcfa'])} ({eco['economie_pct']} %) "
                f"par rapport à la meilleure enseigne unique ({eco['meilleure_enseigne_unique']}) !",
                style="Bon.TLabel",
            ).pack(anchor="w", pady=(10, 6))

        # Détail du panier optimisé
        ttk.Label(
            page,
            text="Détail des achats recommandés (panier optimisé) :",
            style="SectionTitre.TLabel",
        ).pack(anchor="w", pady=(10, 4))

        lignes_opt = [
            (
                l["produit"],
                f"x {l['quantite']}",
                l["enseigne"],
                _fcfa(l["prix_unitaire"]),
                _fcfa(l["sous_total"]),
            )
            for l in self.r.panier_optimise["lignes"]
        ]
        self._tableau(
            page,
            ("Produit", "Quantité", "Enseigne retenue", "Prix unitaire", "Sous-total"),
            lignes_opt,
            droite=("Prix unitaire", "Sous-total"),
            largeurs={"Produit": 250, "Quantité": 80, "Enseigne retenue": 150},
            hauteur=6,
        )

    def afficher_historique(self) -> None:
        """[4] Historique et Black Friday."""
        self._vider_conteneur()
        self.statut.set("Option 4 : Historique des prix et analyse de la semaine du Black Friday.")

        page = self._creer_entete_page(
            "4. Historique des prix & Semaine du Black Friday",
            "Quand fallait-il acheter ? Comparaison semaine du Black Friday (24-30 nov. 2025) vs moyenne annuelle.",
        )

        # 1. Analyse Black Friday
        lignes_bf = [
            (
                b["enseigne"],
                _fcfa(b["prix_moyen_annee"]),
                _fcfa(b["prix_moyen_bf"]),
                _pct(b["ecart_pct"], signe=True),
                "✓ Vraie promotion Black Friday" if b["est_bonne_affaire"] else "✗ Pas de baisse (boutique physique)",
            )
            for b in self.r.black_friday
        ]
        self._tableau(
            page,
            ("Enseigne", "Prix moyen annuel", "Prix Black Friday", "Variation %", "Constat"),
            lignes_bf,
            droite=("Prix moyen annuel", "Prix Black Friday", "Variation %"),
            largeurs={"Enseigne": 160, "Constat": 240},
            hauteur=4,
        )

        # Conclusion stratégique répondant directement à "Quand fallait-il acheter ?"
        cadre_verdict = ttk.LabelFrame(
            page, text=" 💡 Réponse à la consigne : Quand fallait-il acheter ? ", padding=10
        )
        cadre_verdict.pack(fill="x", pady=(10, 2))

        texte_verdict = (
            "• En ligne (Baobab Shop & Marché Lagune) : OUI, il fallait acheter impérativement pendant la semaine du Black Friday !\n"
            "  Les prix y atteignaient leur minimum annuel (-11.6 % et -11.2 % sous la moyenne), juste avant le pic de décembre.\n"
            "• En boutique (Comptoir Ivoire) : NON, il ne fallait pas acheter au Black Friday (+3.7 % plus cher que sa moyenne).\n"
            "  La boutique d'Adjamé ne fait pas de Black Friday ; son moment le moins cher était en septembre-octobre 2026."
        )
        ttk.Label(
            cadre_verdict,
            text=texte_verdict,
            style="Card.TLabel",
            font=("Segoe UI", 9),
            justify="left",
        ).pack(anchor="w")

        # 2. Plus fortes variations
        ttk.Label(
            page,
            text="Top 5 des plus fortes variations annuelles de prix :",
            style="SectionTitre.TLabel",
        ).pack(anchor="w", pady=(14, 4))

        lignes_var = [
            (
                s["produit_nom"],
                s["source"],
                _fcfa(s["premier"]),
                _fcfa(s["dernier"]),
                _pct(s["variation_pct"], signe=True),
            )
            for s in self.r.variations_historique
        ]
        self._tableau(
            page,
            ("Produit", "Enseigne", "Prix initial (Nov 2025)", "Prix final (Oct 2026)", "Variation %"),
            lignes_var,
            droite=("Prix initial (Nov 2025)", "Prix final (Oct 2026)", "Variation %"),
            largeurs={"Produit": 260, "Enseigne": 150},
            hauteur=6,
        )

    def afficher_journal(self) -> None:
        """[5] Journal de nettoyage."""
        self._vider_conteneur()
        self.statut.set("Option 5 : Journal de nettoyage — Traitement des données et anomalies.")

        page = self._creer_entete_page(
            "5. Journal de nettoyage & Qualité des données",
            "Anomalies repérées et corrigées dans les 3 sources (consignées dans output/journal.txt).",
        )

        cadre_texte = ttk.Frame(page, style="Dark.TFrame")
        cadre_texte.pack(fill="both", expand=True, pady=(5, 0))

        texte = tk.Text(
            cadre_texte,
            wrap="word",
            font=("Consolas", 10),
            padx=12,
            pady=12,
            bg=CARD_BG,
            fg="#e2e8f0",
            insertbackground=ACCENT_CYAN,
            relief="solid",
            bd=1,
        )
        scrollbar = ttk.Scrollbar(cadre_texte, orient="vertical", command=texte.yview, style="Vertical.TScrollbar")
        texte.configure(yscrollcommand=scrollbar.set)

        journal_path = os.path.join("output", "journal.txt")
        if os.path.exists(journal_path):
            with open(journal_path, encoding="utf-8") as f:
                contenu_journal = f.read()
            texte.insert("1.0", contenu_journal)
        else:
            texte.insert("1.0", "Aucune entrée dans le journal.")

        texte.configure(state="disabled")
        texte.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def afficher_performances(self) -> None:
        """[6] Performances et Complexité."""
        self._vider_conteneur()
        self.statut.set("Option 6 : Mesures de performance et benchmark de complexité algorithmique.")

        page = self._creer_entete_page(
            "6. Performances & Justification de la complexité",
            "Chronométrage des étapes et benchmark O(1) vs O(N) sur l'historique de plus de 20 000 lignes.",
        )

        # Tableau des étapes
        lignes = [
            (l["etape"], f"{l['secondes'] * 1000:.1f} ms", _pct(l["part_pct"]))
            for l in self.r.performances
        ]
        self._tableau(
            page,
            ("Étape du traitement", "Durée", "Part du temps total"),
            lignes,
            droite=("Durée", "Part du temps total"),
            largeurs={"Étape du traitement": 280, "Durée": 120, "Part du temps total": 140},
            hauteur=8,
        )

        # Explication et benchmark
        b = self.r.benchmark_complexite
        if b:
            ttk.Label(
                page,
                text="Justification des choix de structures de données (20 876 relevés) :",
                style="SectionTitre.TLabel",
            ).pack(anchor="w", pady=(12, 4))

            texte_complexite = (
                f"• Volume traité : {b['nb_lignes']:,} relevés temporels.\n"
                f"• Parcours linéaire O(N) sur liste : {b['liste_s'] * 1000:.1f} ms.\n"
                f"• Recherche par table de hachage O(1) (clé composite (produit, date, source)) : "
                f"{b['dict_s'] * 1000:.2f} ms.\n"
                f"✓ Gain d'accélération : le dictionnaire est environ {b['facteur']:.0f}× plus rapide !"
            )
            ttk.Label(
                page,
                text=texte_complexite,
                style="Bon.TLabel",
                wraplength=800,
                justify="left",
            ).pack(anchor="w", pady=(4, 0))

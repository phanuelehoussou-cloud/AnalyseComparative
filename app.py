import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from phanuel.controllers.comparateur_controller import ComparateurController
from phanuel.views.console_view import TkView


def main() -> None:
    racine = Path(__file__).parent
    controleur = ComparateurController(racine / "data", racine / "output")
    try:
        resultats = controleur.executer()
    except ValueError as erreur:  # fichier manquant ou illisible
        cache = tk.Tk()
        cache.withdraw()
        messagebox.showerror("Erreur", str(erreur))
        cache.destroy()
        return

    TkView(resultats).mainloop()


if __name__ == "__main__":
    main()
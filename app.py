import sys
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
    except Exception as erreur:
        print(f"[ERREUR] Échec de l'analyse : {erreur}", file=sys.stderr)
        try:
            cache = tk.Tk()
            cache.withdraw()
            messagebox.showerror("Erreur Critique", f"Impossible d'exécuter l'analyse :\n{erreur}")
            cache.destroy()
        except Exception:
            pass
        return

    app = TkView(resultats)
    app.mainloop()


if __name__ == "__main__":
    main()

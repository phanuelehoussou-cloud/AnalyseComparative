from pathlib import Path

from phanuel.controllers.comparateur_controller import ComparateurController
from phanuel.views.console_view import ConsoleView


def main() -> None:
    racine = Path(__file__).parent
    controleur = ComparateurController(racine / "data", racine / "output")
    vue = ConsoleView()
    try:
        resultats = controleur.executer()
    except ValueError as erreur:  # fichier manquant ou illisible
        vue.afficher_erreur(str(erreur))
        return
    vue.afficher_tout(resultats)


if __name__ == "__main__":
    main()
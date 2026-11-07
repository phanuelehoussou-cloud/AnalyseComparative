import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from phanuel.controllers.comparateur_controller import ComparateurController
from phanuel.views.console_view import TkView
from phanuel.views.rich_console_view import RichConsoleView


def main() -> None:
    console = Console()
    racine = Path(__file__).parent

    # 1. Exécution du pipeline de traitement
    try:
        controleur = ComparateurController(racine / "data", racine / "output")
        resultats = controleur.executer()
    except Exception as erreur:
        console.print(
            f"[bold red1]✖ Erreur critique lors de l'exécution du pipeline : {erreur}[/bold red1]",
            file=sys.stderr,
        )
        return

    # 2. Écran d'accueil et choix du mode d'affichage
    banniere = Panel(
        "[bold bright_yellow]ANALYSE COMPARATIVE DE MARCHÉ — ABIDJAN[/bold bright_yellow]\n"
        "[bright_cyan]DA Python · L2 Computer Science · Séance 3[/bright_cyan]\n"
        "[spring_green3]Marché Lagune (CSV) · Baobab Shop (JSON) · Comptoir Ivoire (Excel)[/spring_green3]",
        border_style="bright_cyan",
        padding=(1, 2),
    )
    console.print()
    console.print(banniere)

    console.print("[bold gold1]Choisissez votre mode d'interaction :[/bold gold1]")
    console.print("  [bold bright_yellow][1][/bold bright_yellow] [spring_green3]Menu Console Interactif (Terminal Rich)[/spring_green3]")
    console.print("  [bold bright_yellow][2][/bold bright_yellow] [deep_sky_blue1]Interface Graphique (Fenêtre Tkinter Dark Slate)[/deep_sky_blue1]")
    console.print("  [bold bright_yellow][0][/bold bright_yellow] [steel_blue]Quitter l'application[/steel_blue]")
    console.print()

    choix = Prompt.ask(
        "[bright_cyan]Votre choix[/bright_cyan]",
        choices=["1", "2", "0", "q", "Q"],
        default="1",
        console=console,
    ).strip().lower()

    if choix in ("0", "q"):
        console.print("[gold1]Au revoir ![/gold1]")
        return
    elif choix == "1":
        # Mode Console Rich interactif (permet aussi de basculer vers Tkinter via l'option 7)
        vue_rich = RichConsoleView(resultats)
        vue_rich.demarrer()
    elif choix == "2":
        # Mode Graphique Tkinter direct
        try:
            app_tk = TkView(resultats)
            app_tk.mainloop()
        except Exception as e:
            console.print(f"[bold red1]Impossible de lancer Tkinter : {e}[/bold red1]")


if __name__ == "__main__":
    main()

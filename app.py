from phanuel.comparateur.nettoyeur import Nettoyeur
from pathlib import Path


n = Nettoyeur(Path("journal.txt"))
print(n._nettoyer_note("N/A"), n._nettoyer_note("n/a"), n._nettoyer_note("4,5"))
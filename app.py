from pathlib import Path
from phanuel.comparateur.chargeur import charger_csv

articles = charger_csv(Path("data/marche_lagune.csv"))
print(len(articles), "articles")
print(articles[0])
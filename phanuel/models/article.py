from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Article:
    """Ligne nettoyée d'une enseigne, pas encore rapprochée du catalogue."""
    reference: str
    designation: str
    enseigne: str
    prix_brut: float
    frais_livraison: float
    remise: float                    # en pourcentage (10 = 10 %)
    disponible: bool
    note: Optional[float] = None     
    quantite: Optional[int] = None 

    @property
    def prix_paye(self) -> float:
        """Prix après remise, puis ajout des frais de livraison."""
        return round(self.prix_brut * (1 - self.remise / 100) + self.frais_livraison, 2)
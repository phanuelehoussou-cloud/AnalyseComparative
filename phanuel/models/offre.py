from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Offre:
    """Article rapproché d'un produit du catalogue, prêt à être comparé."""
    produit_id: str
    enseigne: str
    prix_paye: float
    disponible: bool
    note: Optional[float] = None
    quantite: Optional[int] = None   
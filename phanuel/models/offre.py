from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Offre:
    produit_id: str
    enseigne: str                
    prix_paye: Optional[float]   
    disponible: bool
    note: Optional[float] = None  
    quantite: int = 0
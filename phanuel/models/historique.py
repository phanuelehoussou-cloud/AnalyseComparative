from dataclasses import dataclass
import datetime 

@dataclass(frozen=True)
class HistoriquePrix:
    date: datetime.date
    source: str
    produit_id: str
    prix_fcfa: float
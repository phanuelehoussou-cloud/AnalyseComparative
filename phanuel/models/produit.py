from dataclasses import dataclass


@dataclass(frozen=True)
class Produit:
    produit_id: str
    nom: str
    categorie: str
    marque: str 
    

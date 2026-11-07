# Analyse Comparative de Marché — Abidjan

**Projet DA Python · L2 Computer Science · Séance 3**

## 1. Présentation du projet

Ce projet consiste à développer une application Python permettant de comparer les prix de produits électroniques et électroménagers proposés par trois enseignes à Abidjan (Côte d'Ivoire).

L'application automatise la collecte, le nettoyage, le rapprochement des produits, la comparaison des prix et l'analyse historique du marché.

Elle dispose de deux modes d'interaction :
- Une interface graphique **Tkinter** avec un thème Dark Slate & Cyber Cyan/Emerald.
- Une interface console interactive utilisant **Rich**.

### Sources de données

| Enseigne | Format | Particularité |
|---|---|---|
| Marché Lagune | CSV | Livraison incluse |
| Baobab Shop | JSON | Prix + frais de livraison |
| Comptoir Ivoire | Excel | Prix après remise, retrait en magasin |

Le catalogue de référence contient 30 produits (P01 à P30). L'historique comprend 20 876 relevés de prix sur une année, du 01/11/2025 au 31/10/2026.

---

## 2. Installation et configuration

### Prérequis
- Python 3.10 ou supérieur.
- Git (facultatif).

### Récupération du projet

```bash
cd "chemin/vers/AnalyseComparative"
```

### Création de l'environnement virtuel

```bash
python -m venv venv
```

### Activation

**Windows PowerShell :**
```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloque l'exécution :

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1
```

**Windows CMD :**
```cmd
venv\Scripts\activate.bat
```

**Linux / macOS :**
```bash
source venv/bin/activate
```

### Installation des dépendances

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Principales bibliothèques :
- `openpyxl` : lecture des fichiers Excel.
- `rich` : interface console.
- `markdown-it-py` et `pygments` : formatage et affichage.

---

## 3. Lancement de l'application

```bash
python app.py
```

L'application propose deux modes :

| Option | Description |
|---|---|
| 1 | Menu console interactif avec Rich |
| 2 | Interface graphique Tkinter |
| 0 | Quitter |

**Interface Tkinter :**
- Navigation par cartes et clavier.
- Thème sombre moderne.
- Retour au menu principal avec la touche Échap.
- Accès direct au dossier `output/`.

**Console Rich :**
- Tableaux colorés.
- Navigation par numéros.
- Possibilité de basculer vers Tkinter.

---

## 4. Architecture du projet

Le projet adopte une architecture organisée autour du modèle MVC.

```text
AnalyseComparative/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── catalogue_reference.csv
│   ├── marche_lagune.csv
│   ├── baobab_shop.json
│   ├── comptoir_ivoire.xlsx
│   └── historique_prix.csv
│
├── output/
│   ├── comparatif.csv
│   ├── journal.txt
│   └── non_rattaches.txt
│
└── phanuel/
    ├── controllers/
    │   └── comparateur_controller.py
    │
    ├── models/
    │   ├── article.py
    │   ├── enseigne.py
    │   ├── historique.py
    │   ├── offre.py
    │   └── produit.py
    │
    ├── comparateur/
    │   ├── chargeur.py
    │   ├── nettoyeur.py
    │   ├── rapprocheur.py
    │   ├── comparateur_prix.py
    │   ├── synthese.py
    │   ├── panier.py
    │   ├── analyse_historique.py
    │   └── performances.py
    │
    └── views/
        ├── console_view.py
        └── rich_console_view.py
```

### Rôle des principaux modules

| Module | Responsabilité |
|---|---|
| `chargeur.py` | Lecture CSV, JSON et Excel |
| `nettoyeur.py` | Nettoyage et validation des données |
| `rapprocheur.py` | Correspondance entre articles et catalogue |
| `comparateur_prix.py` | Comparaison et export CSV |
| `synthese.py` | Statistiques et classement des enseignes |
| `panier.py` | Calcul du panier optimal |
| `analyse_historique.py` | Étude de l'évolution des prix |
| `performances.py` | Benchmark algorithmique |
| `comparateur_controller.py` | Orchestration du traitement |
| `views/` | Interfaces utilisateur |

---

## 5. Fonctionnalités principales

### 5.1. Chargement multi-sources
- Lecture des fichiers CSV, JSON et XLSX.
- Détection automatique du séparateur CSV.
- Gestion des encodages et des fichiers Excel.
- Uniformisation des données dans des dictionnaires Python.

### 5.2. Nettoyage et validation
- Normalisation des nombres et des devises FCFA/XOF.
- Gestion des espaces et des virgules décimales.
- Détection des prix manquants et des doublons.
- Signalement des valeurs aberrantes.
- Génération d'un journal des anomalies.

### 5.3. Rapprochement sémantique

Le moteur de rapprochement permet d'associer les articles des différentes enseignes aux 30 produits de référence.

Il utilise :
- La normalisation Unicode et la suppression des accents.
- Un dictionnaire d'équivalences français/anglais.
- La reconnaissance des abréviations et expressions locales.
- L'harmonisation des unités (Go, To, pouces, litres, CV).
- La similarité par chevauchement de jetons pondéré (Dice Token Matcher).
- Un bonus de correspondance sur les marques.

**Résultat : 73 offres nettoyées et 100 % de rattachements réussis.**

### 5.4. Comparaison des prix
- Comparaison des trois enseignes.
- Prise en compte des frais de livraison et des remises.
- Exclusion des produits indisponibles.
- Conservation des produits présents dans au moins deux enseignes.
- Export automatique vers `output/comparatif.csv`.

### 5.5. Synthèse et panier optimisé
- Nombre de victoires par enseigne.
- Calcul des surcoûts moyens en pourcentage et en FCFA.
- Identification des trois produits présentant les plus grands écarts.
- Comparaison des stratégies d'achat.
- Optimisation du panier en combinant les enseignes.

### 5.6. Analyse historique
Étude de 20 876 relevés de prix pour :
- Comparer les prix moyens annuels.
- Analyser la semaine du Black Friday (24 au 30 novembre 2025).
- Identifier les périodes les plus avantageuses.
- Étudier les variations tarifaires par enseigne.

### 5.7. Benchmark algorithmique

Comparaison de deux méthodes de recherche :
- Parcours séquentiel dans une liste : **O(N)**.
- Recherche dans un dictionnaire Python : **O(1)** en moyenne.

La recherche par dictionnaire est environ **4 400 fois plus rapide** dans le benchmark réalisé.

---

## 6. Résultats obtenus

### 6.1. Bilan du pipeline

| Indicateur | Résultat |
|---|---:|
| Produits de référence | 30 |
| Offres rattachées | 73 |
| Articles non rattachés | 0 |
| Produits comparables | 23 |
| Taux de rattachement | 100 % |

### 6.2. Victoires et surcoûts moyens

| Enseigne | Victoires | Surcoût moyen |
|---|---:|---:|
| Baobab Shop | 9 | +4,67 % |
| Comptoir Ivoire | 8 | +2,81 % |
| Marché Lagune | 6 | +52,99 % brut |

Le surcoût de Marché Lagune est fortement influencé par une valeur aberrante concernant le Tecno Spark 20. Hors cette anomalie, il descend à **+3,79 %**.

### 6.3. Top 3 des écarts de prix

| Produit | Écart constaté |
|---|---:|
| Tecno Spark 20 | 704 000 FCFA |
| HP 250 G9 | 52 800 FCFA |
| Apple iPhone 13 | 26 500 FCFA |

### 6.4. Panier de rentrée optimisé

| Stratégie | Coût total |
|---|---:|
| Tout chez Marché Lagune | 1 205 400 FCFA |
| Tout chez Baobab Shop | 491 500 FCFA |
| Tout chez Comptoir Ivoire | 484 075 FCFA |
| **Panier optimisé** | **477 575 FCFA** |

<ins>Économie réalisée : 6 500 FCFA (environ 1,3 %).</ins>

### 6.5. Analyse du Black Friday

Comparaison du prix moyen annuel avec celui de la semaine du Black Friday.

| Enseigne | Prix moyen annuel | Black Friday | Écart |
|---|---:|---:|---:|
| Baobab Shop | 140 913 | 124 579 | -11,59 % |
| Marché Lagune | 161 978 | 143 894 | -11,16 % |
| Comptoir Ivoire | 154 843 | 160 605 | +3,72 % |

**Conclusion :**
- Baobab Shop et Marché Lagune proposent leurs prix moyens les plus avantageux pendant la semaine du Black Friday.
- Comptoir Ivoire présente une tendance différente, avec des prix plus élevés pendant cette période.
- Septembre et octobre 2026 constituent la meilleure période identifiée pour Comptoir Ivoire.

---

## 7. Fichiers générés

Les résultats sont enregistrés automatiquement dans le dossier `output/` :

| Fichier | Contenu |
|---|---|
| `comparatif.csv` | Comparaison des prix par produit |
| `journal.txt` | Anomalies détectées pendant le nettoyage |
| `non_rattaches.txt` | Articles non associés au catalogue |

---

## Conclusion

Ce projet met en œuvre les principales étapes d'un système de traitement et d'analyse de données en Python : chargement multi-formats, nettoyage, rapprochement sémantique, comparaison, optimisation et analyse temporelle.

Il combine également les notions de programmation orientée objet, d'architecture MVC, de structures de données et de complexité algorithmique dans une application disposant d'interfaces console et graphique.

*Projet réalisé dans le cadre du module DA Python — L2 Computer Science.*
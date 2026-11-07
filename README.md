# Analyse Comparative de Marché — Abidjan
**Projet DA Python · L2 Computer Science · Séance 3**

Ce projet implémente un système complet de collecte, de nettoyage, de rapprochement de catalogue, d'analyse comparative de prix, de calcul de panier d'achat et d'analyse temporelle historique sur des données de marché à Abidjan (Côte d'Ivoire).

L'application intègre un pipeline de traitement de données rigoureux et une interface graphique interactive **Tkinter** dotée d'une page d'accueil dédiée au menu et d'un thème moderne **Dark Slate & Cyber Cyan/Emerald**.

---

## Sommaire
1. [Contexte du Projet](#contexte-du-projet)
2. [Guide d'Installation et Configuration Pas à Pas](#guide-dinstallation-et-configuration-pas-à-pas)
   - [Prérequis](#prérequis)
   - [1. Cloner ou télécharger le dépôt](#1-cloner-ou-télécharger-le-dépôt)
   - [2. Créer l'environnement virtuel](#2-créer-lenvironnement-virtuel)
   - [3. Activer l'environnement virtuel](#3-activer-lenvironnement-virtuel)
   - [4. Installer les dépendances](#4-installer-les-dépendances)
3. [Lancement et Utilisation](#lancement-et-utilisation)
4. [Arborescence et Description des Fichiers](#arborescence-et-description-des-fichiers)
5. [Fonctionnalités et Cahier des Charges](#fonctionnalités-et-cahier-des-charges)
   - [1. Chargement multi-sources](#1-chargement-multi-sources)
   - [2. Nettoyage et journal d'anomalies](#2-nettoyage-et-journal-danomalies)
   - [3. Algorithme de Rapprochement sémantique](#3-algorithme-de-rapprochement-sémantique)
   - [4. Comparatif multi-enseignes & Export CSV](#4-comparatif-multi-enseignes--export-csv)
   - [5. Synthèse par enseigne & Top 3 des gains](#5-synthèse-par-enseigne--top-3-des-gains)
   - [6. Panier de rentrée optimisé](#6-panier-de-rentrée-optimisé)
   - [7. Analyse temporelle & Black Friday : Quand fallait-il acheter ?](#7-analyse-temporelle--black-friday--quand-fallait-il-acheter-)
   - [8. Benchmark de Complexité algorithmique](#8-benchmark-de-complexité-algorithmique)
6. [Résultats Obtenus](#résultats-obtenus)

---

## Contexte du Projet

Un client souhaite acquérir des équipements électroniques et électroménagers à Abidjan et hésite entre trois enseignes aux modèles de distribution distincts :

| Enseigne | Type de commerce | Fichier source | Format | Particularité tarifaire |
| :--- | :--- | :--- | :--- | :--- |
| **Marché Lagune** | Site marchand en ligne | `marche_lagune.csv` | CSV (séparateur `;`) | La livraison est incluse dans le prix affiché. |
| **Baobab Shop** | Application mobile | `baobab_shop.json` | JSON (API mobile) | Prix payé = `amount` + `delivery_fee` (frais de livraison). |
| **Comptoir Ivoire** | Boutique physique (Adjamé) | `comptoir_ivoire.xlsx` | Excel (`.xlsx`) | Prix payé = Prix catalogue diminué de la remise. Retrait en magasin. |

Un catalogue de référence commun (`catalogue_reference.csv`) liste **30 produits cibles** (de `P01` à `P30`). Chaque enseigne ayant sa propre manière de désigner les articles (titres anglais, abréviations, fautes de frappe), le système automatise la mise en correspondance.

De plus, un fichier chronologique de **20 876 relevés quotidiens** (`historique_prix.csv`) permet d'étudier l'évolution des prix sur une année complète (du 01/11/2025 au 31/10/2026).

---

## Guide d'Installation et Configuration Pas à Pas

### Prérequis
* **Python 3.10 ou supérieur** installé sur votre machine.
  * Vérifiez votre version dans un terminal :
    ```bash
    python --version
    ```

---

### 1. Cloner ou télécharger le dépôt
Ouvrez un terminal (PowerShell sur Windows, ou Bash sous Linux/macOS) et positionnez-vous dans le répertoire du projet :
```bash
cd "c:\Users\AHIBO\Documents\IIT_school\PYTHON\AnalyseComparative"
```

---

### 2. Créer l'environnement virtuel
L'environnement virtuel isole les bibliothèques du projet du reste de votre système d'exploitation.

* **Sous Windows (PowerShell ou Invite de commandes) :**
  ```powershell
  python -m venv venv
  ```
* **Sous macOS / Linux :**
  ```bash
  python3 -m venv venv
  ```
Un dossier `venv/` est alors créé à la racine du projet.

---

### 3. Activer l'environnement virtuel

* **Sous Windows avec PowerShell :**
  ```powershell
  .\venv\Scripts\Activate.ps1
  ```
  > **Note de sécurité PowerShell :** Si vous rencontrez l'erreur `L'exécution de scripts est désactivée sur ce système`, autorisez les scripts pour votre session locale avec la commande suivante :
  > ```powershell
  > Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  > .\venv\Scripts\Activate.ps1
  > ```

* **Sous Windows avec l'Invite de commandes classique (cmd.exe) :**
  ```cmd
  venv\Scripts\activate.bat
  ```

* **Sous macOS / Linux :**
  ```bash
  source venv/bin/activate
  ```

Une fois activé, le préfixe `(venv)` apparaît devant votre invite de commande.

---

### 4. Installer les dépendances
Mettez à jour le gestionnaire de paquets `pip` puis installez les dépendances déclarées dans `requirements.txt` :

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Le fichier `requirements.txt` installe :
* `openpyxl>=3.1.0` : Nécessaire pour la lecture haute performance du classeur Excel `comptoir_ivoire.xlsx`.
* `rich>=13.0.0`, `markdown-it-py`, `pygments` : Bibliothèques d'affichage et de formatage.

---

## Lancement et Utilisation

Pour lancer l'application, exécutez la commande :
```bash
python app.py
```
*(ou directement avec l'interpréteur de l'environnement virtuel : `.\venv\Scripts\python.exe app.py`)*

### Double Mode d'Interaction : Console Rich ou Interface Tkinter
Dès le démarrage, l'application vous propose de choisir votre mode d'affichage préféré :

```text
Choisissez votre mode d'interaction :
  [1] Menu Console Interactif (Terminal Rich)
  [2] Interface Graphique (Fenêtre Tkinter Dark Slate)
  [0] Quitter l'application
```

#### Mode 1 : Menu Console Interactif (Rich)
* Conçu entièrement avec la bibliothèque **`rich`**, sans aucune couleur blanche monotone (palette éclatante : Cyan, Or, Vert émeraude, Orange, Magenta, Bleu ciel).
* Navigation fluide par saisie de numéro (`1` à `6`) pour afficher les tableaux colorés, le panier, l'historique et le benchmark.
* **Option `[7]` dans la console** : Permet de basculer à tout moment vers l'interface graphique Tkinter ! Lorsque vous fermez la fenêtre Tkinter, vous revenez automatiquement dans le menu console Rich.

#### Mode 2 : Interface Graphique (Tkinter Dark Slate)
* Page d'accueil dédiée au menu principal avec saisie au clavier (`1` à `6`) ou clic sur les cartes d'options.
* Thème sombre raffiné **Dark Slate & Cyber Cyan/Emerald**.
* Bouton **`⬅ Menu Principal [Échap]`** en haut de chaque écran pour revenir au menu d'un clic ou par la touche `Échap`.
* Bouton direct **`📁 output/`** pour ouvrir le dossier contenant le fichier `comparatif.csv` et le journal.

---

## Arborescence et Description des Fichiers

```text
AnalyseComparative/
├── app.py                      # Point d'entrée principal de l'application
├── requirements.txt            # Liste des dépendances Python requises
├── README.md                   # Documentation exhaustive du projet
│
├── data/                       # Données sources brutes fournies pour l'exercice
│   ├── catalogue_reference.csv # 30 produits de référence (P01 à P30)
│   ├── marche_lagune.csv       # Catalogue Marché Lagune (CSV séparateur ;)
│   ├── baobab_shop.json        # Catalogue Baobab Shop (JSON API mobile)
│   ├── comptoir_ivoire.xlsx    # Catalogue Comptoir Ivoire (Feuille Excel)
│   └── historique_prix.csv     # 20 876 relevés quotidiens de prix sur 1 an
│
├── output/                     # Résultats et rapports générés automatiquement
│   ├── comparatif.csv          # Export CSV du tableau comparatif multi-enseignes
│   ├── journal.txt             # Journal des anomalies détectées au nettoyage
│   └── non_rattaches.txt       # Articles non associés (vide si 100% rattachés)
│
└── phanuel/                    # Code source du package applicatif (Architecture MVC)
    ├── __init__.py
    ├── controllers/
    │   ├── __init__.py
    │   └── comparateur_controller.py # Orchestrateur général du pipeline
    ├── models/
    │   ├── __init__.py
    │   ├── article.py          # Modèle d'article nettoyé avant rapprochement
    │   ├── enseigne.py         # Métadonnées des enseignes et formats de fichiers
    │   ├── historique.py       # Modèle pour un relevé de prix temporel
    │   ├── offre.py            # Offre disponible rattachée au catalogue
    │   └── produit.py          # Produit issu du catalogue de référence
    ├── comparateur/
    │   ├── __init__.py
    │   ├── chargeur.py         # Lecture multi-formats (CSV, JSON, XLSX)
    │   ├── nettoyeur.py        # Nettoyage, validation et détection d'anomalies
    │   ├── rapprocheur.py      # Moteur de rapprochement sémantique FR/EN
    │   ├── comparateur_prix.py # Logique de comparaison et export CSV
    │   ├── synthese.py         # Agrégation, victoires, surcoûts et top gains
    │   ├── panier.py           # Calculs de panier (spécifique et optimisé)
    │   ├── analyse_historique.py # Analyse temporelle & semaine Black Friday
    │   └── performances.py     # Chronométrage et benchmark O(1) vs O(N)
    └── views/
        ├── __init__.py
        ├── console_view.py           # Interface graphique Tkinter (Thème Dark Slate)
        └── rich_console_view.py      # Menu interactif console Rich (Sans couleur blanche)
```

---

## Fonctionnalités et Cahier des Charges

### 1. Chargement multi-sources
* `Chargeur` lit les trois formats dans des listes uniformes de dictionnaires Python.
* **Auto-détection du délimiteur CSV** (séparateur `;` ou `,`) avec `utf-8-sig` pour gérer les encodages Excel avec BOM.
* **Extraction JSON** robuste via le module `json`.
* **Lecture Excel streaming** via `openpyxl` en mode `read_only=True` et `data_only=True`, avec détection dynamique de la feuille active en cas de mise à jour du nom de l'onglet.

### 2. Nettoyage et journal d'anomalies
Les fichiers sources réels comportent des défauts qui sont tous identifiés, traités et consignés dans `output/journal.txt` sans interrompre l'exécution :
* **Nombres et devises** : Gestion des espaces insécables (`\u202f`, `\u00a0`), suppression des suffixes `FCFA` et `XOF`, et normalisation des virgules décimales européennes (`1.250,50` ou `279 300`).
* **Lignes incomplètes ou sans prix** :
  * `ML-1119` (Écran Samsung 24") : `Prix sur demande` (rejeté et consigné).
  * `ML-1168` (Mixeur Moulinex 1.5L) : Prix vide (rejeté et consigné).
  * `BB27999` (Fer à repasser Philips) : `amount: None` (rejeté et consigné).
* **Dédoublonnage strict** : Élimination des références dupliquées dans Marché Lagune (`ML-1000` Galaxy A15 et `ML-1147` TV Hisense 32").
* **Détection de valeur aberrante** : `ML-1021` (Tecno Spark 20) est affiché à **779 000 FCFA** (alors que son ancien prix était de 88 700 FCFA). L'anomalie est signalée dans le journal.
* **Sécurisation console Windows** : Aucune exception `UnicodeEncodeError` lors de l'écriture en console sous encodage `cp1252`.

### 3. Algorithme de Rapprochement sémantique
Pour associer chaque article au bon produit parmi les 30 du catalogue, `Rapprocheur` intègre :
1. **Désaccentuation et normalisation** via `unicodedata` (NFKD).
2. **Dictionnaire d'équivalences bilingue et argotique** :
   * Anglais $\rightarrow$ Français : *Fridge* $\rightarrow$ Réfrigérateur, *Blender* $\rightarrow$ Mixeur, *Steam Iron* $\rightarrow$ Fer à repasser, *Electric Kettle* $\rightarrow$ Bouilloire, *Air Conditioner* $\rightarrow$ Climatiseur, *Wireless Mouse* $\rightarrow$ Souris sans fil, *Laptop* $\rightarrow$ PC Portable, *Monitor* $\rightarrow$ Écran.
   * Argot / Abréviations $\rightarrow$ Standard : *Clim* $\rightarrow$ Climatiseur, *Frigo* $\rightarrow$ Réfrigérateur, *Ventilo* $\rightarrow$ Ventilateur, *DD externe* $\rightarrow$ Disque dur externe, *Samsun* $\rightarrow$ Samsung.
3. **Harmonisation universelle des unités** :
   * Stockage : `128GB`, `128 Go`, `128go` $\rightarrow$ `128go` ; `1TB`, `1 To` $\rightarrow$ `1to`.
   * Puissance : `1HP`, `1CV`, `1 CV` $\rightarrow$ `1cv` ; `1.5HP`, `1.5CV` $\rightarrow$ `1.5cv`.
   * Diagonales : `43"`, `43 pouces` $\rightarrow$ `43pouces`.
   * Volumes : `1.5L`, `1,5 L` $\rightarrow$ `1.5l` ; `205L` $\rightarrow$ `205l`.
4. **Similarité par chevauchement de jetons pondéré (Dice Token Matcher)** avec bonus de marque.
* **Résultat : 100 % des 73 offres nettoyées sont rattachées sans aucune erreur d'attribution.**

### 4. Comparatif multi-enseignes & Export CSV
* Seuls les produits disponibles chez **au moins deux enseignes** sont retenus (soit **23 produits**).
* Conformément aux consignes : un produit en rupture de stock n'est jamais retenu comme le moins cher.
* Le tableau complet est automatiquement généré et exporté dans `output/comparatif.csv` (délimiteur `;`, encodage `utf-8-sig` compatible avec Excel).

### 5. Synthèse par enseigne & Top 3 des gains

#### A. Nombre de victoires (combien de fois chaque enseigne est-elle la moins chère ?)
* **Baobab Shop** : **9 victoires** (enseigne qui remporte le plus de produits au prix le plus bas).
* **Comptoir Ivoire** : **8 victoires**.
* **Marché Lagune** : **6 victoires**.
*(Total : 23 produits disponibles chez au moins 2 enseignes).*

#### B. Écart moyen de chaque enseigne par rapport au prix le plus bas (Surcoût moyen)
Pour chaque produit comparable $i$, si $P_{\text{min}}(i)$ est le prix le plus bas disponible et $P_E(i)$ est le prix de l'enseigne $E$, le surcoût relatif en pourcentage est calculé selon la formule :
$$\text{Surcoût \%} = \frac{P_E(i) - P_{\text{min}}(i)}{P_{\text{min}}(i)} \times 100$$
*(Si l'enseigne est la moins chère pour ce produit, son surcoût vaut $0.0\%$.)*

Voici les résultats calculés sur les 23 produits :

| Enseigne | Écart moyen en % (Surcoût moyen) | Écart moyen en FCFA | Observation & Analyse |
| :--- | :---: | :---: | :--- |
| **Comptoir Ivoire** | **+2,81 %** | **+6 667 FCFA** | **L'enseigne la plus proche du prix le plus bas en moyenne !** Ses remises en boutique sont très avantageuses. |
| **Baobab Shop** | **+4,67 %** | **+2 702 FCFA** | **Très compétitive** : remporte le plus grand nombre de produits (9 victoires) avec un surcoût moyen très faible. |
| **Marché Lagune** | **+52,99 %** *(brut)*<br>*(ou **+3,79 %** corrigé)* | **+44 671 FCFA** | **Impacté par une valeur aberrante** : la référence `ML-1021` (Tecno Spark 20) est affichée à 779 000 FCFA au lieu de ~75 000 FCFA (+938,7 % à elle seule !). Hors cette anomalie, l'écart moyen réel est de **+3,79 %**. |

> **Implémentation dans le code :**
> * Calculé dans [`phanuel/comparateur/synthese.py` (méthode `par_enseigne()`)](file:///c:/Users/AHIBO/Documents/IIT_school/PYTHON/AnalyseComparative/phanuel/comparateur/synthese.py#L17-L48).
> * Orchestré par [`phanuel/controllers/comparateur_controller.py`](file:///c:/Users/AHIBO/Documents/IIT_school/PYTHON/AnalyseComparative/phanuel/controllers/comparateur_controller.py#L76).
> * Accessible dans l'interface Tkinter via l'écran **`[2] Synthèse`** (colonne *Surcoût moyen %*).
> * Accessible dans le menu console Rich via l'option **`[2] Synthèse`**.

#### C. Top 3 des produits où il y a le plus à gagner à comparer
1. **Tecno Spark 20 (P04)** : Écart de **704 000 FCFA** (938.7 %) entre Baobab Shop (75 000 FCFA) et Marché Lagune (779 000 FCFA).
2. **HP 250 G9 (P11)** : Écart de **52 800 FCFA** (14.9 %) entre Baobab Shop (354 200 FCFA) et Comptoir Ivoire (407 000 FCFA).
3. **Apple iPhone 13 (P09)** : Écart de **26 500 FCFA** (6.4 %) entre Baobab Shop (417 200 FCFA) et Comptoir Ivoire (443 700 FCFA).

### 6. Panier de rentrée optimisé
Le panier imposé par le sujet se compose de :
* 1 Tecno Spark 20 (`P04`)
* 1 Lenovo IdeaPad 3 (`P12`)
* 2 clés USB SanDisk 64 Go (`P14`)
* 1 disque dur Seagate 1 To (`P15`)
* 1 micro-ondes Samsung 23 L (`P28`)

**Résultats des stratégies d'achat :**
* Tout chez Marché Lagune : **1 205 400 FCFA**
* Tout chez Baobab Shop : **491 500 FCFA**
* Tout chez Comptoir Ivoire : **484 075 FCFA** *(Meilleure enseigne unique)*
* **Panier Optimisé (Meilleur mélange) : 477 575 FCFA**
* **Gain / Économie réalisée : 6 500 FCFA** par rapport à la meilleure boutique unique.

### 7. Analyse temporelle & Black Friday : Quand fallait-il acheter ?
Le sujet pose une question stratégique directe : **« Quand fallait-il acheter ? Comparez pour chaque enseigne les prix de la semaine du Black Friday (24 au 30 novembre 2025) au prix moyen de l'année. »**

L'analyse des 20 876 relevés chronologiques fournit une réponse très claire selon le canal de distribution :

| Enseigne | Type de canal | Prix moyen annuel | Prix semaine Black Friday | Écart % | Faut-il acheter au Black Friday ? | Meilleure période d'achat sur l'année |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baobab Shop** | Application mobile | 140 913 FCFA | **124 579 FCFA** | **-11.59 %** | **OUI, absolument !** | Semaine du Black Friday (fin novembre 2025) |
| **Marché Lagune** | Site web e-commerce | 161 978 FCFA | **143 894 FCFA** | **-11.16 %** | **OUI, absolument !** | Semaine du Black Friday (fin novembre 2025) |
| **Comptoir Ivoire** | Boutique physique (Adjamé) | 154 843 FCFA | **160 605 FCFA** | **+3.72 %** | **NON, surtout pas !** | Septembre / Octobre 2026 (fin d'année scolaire) |

#### Recommandations pour l'acheteur :
1. **Chez les e-commerçants (Baobab Shop & Marché Lagune) :**
   * **Il fallait acheter impérativement pendant la semaine du Black Friday (24 au 30 novembre 2025)**. Leurs prix y atteignent le **minimum historique de toute l'année**.
   * Les baisses sont particulièrement fortes sur la téléphonie et le gros électroménager (ex: Climatiseur Hisense 1.5CV à **-14.2 %**, Infinix Hot 40i à **-13.0 %**, Xiaomi Redmi Note 13 à **-12.7 %**).
   * **Piège à éviter** : Attendre décembre. Dès le 1er décembre, les prix s'envolent pour les fêtes de fin d'année et atteignent le pic le plus cher de l'année (moyenne de 145 984 FCFA chez Baobab et 168 527 FCFA chez Marché Lagune).

2. **Chez la boutique physique (Comptoir Ivoire) :**
   * **Il ne fallait SURTOUT PAS acheter au Black Friday**. La boutique d'Adjamé n'applique pas les soldes en ligne importées d'Occident ; au contraire, le mois de novembre 2025 correspondait à son mois le plus cher de l'année (160 978 FCFA en moyenne).
   * **Le meilleur moment pour acheter chez Comptoir Ivoire** se situe en **septembre et octobre 2026** (147 781 FCFA en moyenne, soit une baisse de plus de 8 % par rapport à novembre 2025).

### 8. Benchmark de Complexité algorithmique
Pour interroger l'historique de **20 876 lignes**, deux approches sont comparées :
* **Recherche séquentielle dans une liste $O(N)$** : Nécessite de parcourir l'ensemble des éléments un par un.
* **Indexation par table de hachage $O(1)$** : Dictionnaire Python avec clé composite `(produit_id, date, source)`.
* **Résultat du benchmark :** La table de hachage est environ **4 400 fois plus rapide** que le parcours linéaire, réduisant le temps de recherche cumulé de plusieurs secondes à quelques millisecondes.

---

## Résultats Obtenus

```text
=== SUCCÈS DU PIPELINE ===
Produits catalogue          : 30
Offres rattachées           : 73
Articles non rattachés      : 0
Produits multi-enseignes    : 23
Fichier CSV exporté         : output/comparatif.csv

Victoires par enseigne      :
  • Baobab Shop             : 9 victoires (surcoût moyen : 4.67 %)
  • Comptoir Ivoire         : 8 victoires (surcoût moyen : 2.81 %)
  • Marché Lagune           : 6 victoires (surcoût moyen : 52.99 %)

Panier de rentrée :
  • Marché Lagune           : 1 205 400 FCFA
  • Baobab Shop             : 491 500 FCFA
  • Comptoir Ivoire         : 484 075 FCFA (Meilleure enseigne unique)
  • Mélange optimisé        : 477 575 FCFA
  • Économie                : 6 500 FCFA (1.3 %)

Semaine du Black Friday vs Année :
  • Baobab Shop             : -11.59 % (Vraie baisse de prix)
  • Marché Lagune           : -11.16 % (Vraie baisse de prix)
  • Comptoir Ivoire         : +3.72 % (Pas de promotion en boutique)

Accélération dictionnaire O(1) vs O(N) : ~4 400× plus rapide
```

---
*Projet réalisé dans le cadre du module DA Python · L2 Computer Science.*

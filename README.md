# Optimisation — Surveillance par Capteurs

> Projet IUT Nord Franche-Comté — Techniques d'optimisation  
> Résolution d'un problème d'ordonnancement adaptatif de capteurs vidéo via programmation linéaire.

---

## Table des matières

1. [Présentation du problème](#présentation-du-problème)
2. [Structure du projet](#structure-du-projet)
3. [Prérequis & Installation](#prérequis--installation)
4. [Utilisation](#utilisation)
5. [Instances de test](#instances-de-test)
6. [Heuristiques implémentées](#heuristiques-implémentées)
7. [Description des fichiers](#description-des-fichiers)

---

## Présentation du problème

On dispose de **N capteurs vidéo** déployés sur un territoire pour surveiller **M zones**.  
Chaque capteur `sᵢ` couvre un sous-ensemble de zones et possède une durée de vie limitée `Tᵢ`.

Une **configuration élémentaire** est un sous-ensemble *minimal* de capteurs couvrant toutes les zones (retirer un capteur laisse au moins une zone non couverte).

On cherche à **maximiser la durée de vie totale du réseau** en résolvant le programme linéaire :

```
max   Σ tₖ
s.c.  Σ{k : i ∈ cₖ} tₖ ≤ Tᵢ   ∀ capteur i
      tₖ ≥ 0                    ∀ configuration k
```

---

## Structure du projet

```
optimisation/
│
├── main.py            # Point d'entrée — interface CLI
├── data.py            # Classe Instance + lecture/génération des données
├── configs.py         # Génération de configurations élémentaires
├── solver.py          # Écriture du .lp et résolution via PuLP
├── experiences.py     # Parties 4 & 5 : expériences + graphiques
│
├── instances/
│   ├── instance_moyen.txt    # Instance moyenne (10 capteurs, 10 zones)
│   ├── moyen_test_2.txt      # Instance moyenne (20 capteurs, 10 zones)
│   ├── gros_test_1.txt       # Grande instance
│   └── maxi_test_1.txt       # Très grande instance
│
└── projet-plcapteurs-2024.pdf  # Sujet original
```

---

## Prérequis & Installation

### Python
Version **3.8+** requise.

```bash
python3 --version
```

### Dépendances Python

```bash
pip install pulp matplotlib
```

### Solveur GLPK (optionnel mais recommandé)

Le code fonctionne sans GLPK (fallback automatique sur HiGHS ou CBC), mais GLPK est recommandé pour être conforme au sujet.

```bash
# Debian/Ubuntu
sudo apt install glpk-utils

# Vérification
glpsol --version
```

---

## Utilisation

### 1. Résoudre l'exemple du sujet (défaut)

```bash
python3 main.py
```

Affiche l'instance, les configurations élémentaires trouvées, et la solution optimale.

---

### 2. Charger une instance depuis un fichier texte

```bash
python3 main.py --fichier-txt instances/instance_moyen.txt
python3 main.py --fichier-txt instances/moyen_test_2.txt
python3 main.py --fichier-txt instances/gros_test_1.txt
```

---

### 3. Générer une instance aléatoire

```bash
# M zones, N capteurs
python3 main.py --aleatoire 5 8
python3 main.py --aleatoire 10 15
```

---

### 4. Saisie interactive au clavier

```bash
python3 main.py --clavier
```

Le programme demande le nombre de zones, de capteurs, puis les zones couvertes et la durée de vie de chaque capteur.

---

### 5. Choisir la méthode de génération de configurations

```bash
# Glouton aléatoire (défaut)
python3 main.py --methode glouton_aleatoire

# Glouton trié par couverture décroissante
python3 main.py --methode glouton_trie

# Énumération exhaustive (toutes les configs élémentaires)
python3 main.py --methode enumeration

# Combiner toutes les méthodes
python3 main.py --methode toutes
```

Contrôle du nombre de configurations générées :

```bash
python3 main.py --methode glouton_aleatoire --nb-configs 20
```

---

### 6. Lancer toutes les expériences (Parties 4 & 5)

```bash
python3 main.py --experiences
```

Cela exécute :
- **Partie 4** : résolution sur l'exemple du sujet + instances aléatoires, tableau récapitulatif
- **Partie 5** : comparaison des heuristiques + influence du nombre de configurations, **graphiques** `.png`

---

### Combinaisons d'options

```bash
# Fichier texte + méthode glouton trié
python3 main.py --fichier-txt instances/instance_moyen.txt --methode glouton_trie

# Instance aléatoire + énumération
python3 main.py --aleatoire 4 6 --methode enumeration

# Fichier + nombre de configs personnalisé
python3 main.py --fichier-txt instances/moyen_test_2.txt --methode glouton_aleatoire --nb-configs 30
```

---

## Instances de test

### Format du fichier texte

```
N                   ← nombre de capteurs
M                   ← nombre de zones
T1 T2 ... TN        ← durées de vie (séparées par espaces)
z1 z2 ...           ← zones couvertes par capteur 1 (numérotées à partir de 1)
z1 z2 ...           ← zones couvertes par capteur 2
...                 ← (N lignes au total)
```

### Instances disponibles

| Fichier | Capteurs | Zones | Résultat |
|---|---|---|---|
| `instance_moyen.txt` | 10 | 10 | **395** unités de temps |
| `moyen_test_2.txt` | 20 | 10 | **104** unités de temps |
| `gros_test_1.txt` | — | — | **2290** unités de temps |
| `maxi_test_1.txt` | 1000 | 500 | **17173** unités de temps |

---

## Heuristiques implémentées

### Heuristique 1 — Glouton aléatoire
Construit des configurations en ajoutant des capteurs dans un ordre **aléatoire** (seulement ceux qui apportent de nouvelles zones), puis réduit la configuration en configuration élémentaire. Répète jusqu'à obtenir `nb_configs` configurations distinctes.

- ✅ Diversité garantie
- ⚠️ Peut produire des doublons sur des petites instances

### Heuristique 2 — Glouton trié
À chaque étape, sélectionne le capteur qui couvre le **maximum de zones non encore couvertes**. Applique une perturbation aléatoire pour diversifier les résultats.

- ✅ Configurations de petite taille (proches du minimum)
- ⚠️ Moins diversifiée sans perturbation

### Heuristique 3 — Énumération exhaustive (backtracking)
Explore toutes les combinaisons de capteurs par backtracking avec élagage : on n'ajoute un capteur que s'il couvre au moins une zone nouvelle. Vérifie la minimalité de chaque configuration trouvée.

- ✅ Garantit toutes les configurations élémentaires
- ⚠️ Exponentiel en N — limité à 200 résultats par défaut

---

## Description des fichiers

### `data.py`
| Fonction / Classe | Rôle |
|---|---|
| `Instance` | Classe encapsulant les données (M, N, zones, durées de vie) |
| `lire_depuis_fichier_texte(chemin)` | Lecture d'une instance depuis un fichier texte |
| `saisir_au_clavier()` | Saisie interactive |
| `generer_aleatoire(M, N, ...)` | Génération aléatoire reproductible (seed) |
| `instance_exemple()` | Instance de l'exemple exact du sujet |

### `configs.py`
| Fonction | Rôle |
|---|---|
| `couvre_tout(config, instance)` | Vérifie la couverture complète |
| `est_elementaire(config, instance)` | Vérifie la minimalité |
| `reduire_en_elementaire(config, instance)` | Réduit une config valide en élémentaire |
| `heuristique_glouton_aleatoire(...)` | Heuristique 1 — glouton aléatoire |
| `heuristique_glouton_trie(...)` | Heuristique 2 — glouton trié |
| `heuristique_enumeration(...)` | Heuristique 3 — exhaustive |
| `generer_configurations(instance, methode, ...)` | Interface principale |
| `afficher_configurations(configs, instance)` | Affichage formaté |

### `solver.py`
| Fonction | Rôle |
|---|---|
| `ecrire_lp(instance, configs, chemin)` | Génère le fichier `.lp` au format CPLEX |
| `resoudre_pulp(instance, configs, ...)` | Résout le PL via PuLP (GLPK → HiGHS → CBC) |
| `resoudre(instance, configs, ...)` | Interface principale (génère .lp + résout) |
| `afficher_solution(instance, solution)` | Affiche la solution optimale formatée |

### `experiences.py`
| Fonction | Rôle |
|---|---|
| `partie4(instances)` | Résout toutes les instances, tableau récapitulatif |
| `partie5(instances)` | Comparaison heuristiques + influence nb_configs + graphiques |
| `lancer_experiences()` | Point d'entrée des Parties 4 & 5 |

---

## Solveur utilisé

Le code tente les solveurs dans cet ordre :

1. **GLPK** (`glpsol`) — recommandé par le sujet
2. **HiGHS** — solveur libre hautes performances
3. **CBC** — solveur par défaut de PuLP

Un message `[INFO] Solveur utilisé : GLPK/HiGHS/CBC` est affiché à chaque résolution.

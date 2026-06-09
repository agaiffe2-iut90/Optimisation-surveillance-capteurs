# Explication du problème et des méthodes

## 1. Le problème en termes simples

On a **N capteurs** (batteries), chacun avec une durée de vie `T_i`.
On a **M zones** à surveiller en permanence.
Chaque capteur couvre un sous-ensemble de zones.

**Objectif** : garder TOUTES les zones couvertes le plus longtemps possible,
en éteignant et rallumant les capteurs intelligemment pour ménager les batteries.

---

## 2. C'est quoi une configuration élémentaire ?

### Définition intuitive
Une **configuration** = un groupe de capteurs allumés simultanément qui couvre TOUTES les zones.

Une configuration est **élémentaire** (minimale) si :
- Elle couvre toutes les zones ✓
- Si on retire n'importe quel capteur → au moins une zone n'est plus couverte ✗

### Exemple concret (instance du sujet)
3 zones : z1, z2, z3  
4 capteurs : s1={z1,z2}, s2={z2,z3}, s3={z3}, s4={z1,z3}  
Durées de vie : T1=6, T2=3, T3=2, T4=6

| Ensemble | Couvre tout ? | Élémentaire ? | Raison |
|----------|--------------|---------------|--------|
| {s1, s2} | ✓ {z1,z2,z3} | ✓ OUI | retirer s1 → manque z1, retirer s2 → manque z3 |
| {s1, s3} | ✓ {z1,z2,z3} | ✓ OUI | retirer s1 → manque z1, retirer s3 → manque z3 |
| {s2, s4} | ✓ {z1,z2,z3} | ✓ OUI | retirer s2 → manque z2, retirer s4 → manque z1 |
| {s1,s2,s3}| ✓           | ✗ NON | s3 est inutile (s2 couvre déjà z3) |

Ces configs élémentaires sont les **"tours de garde"** possibles.

---

## 3. Comment on calcule la durée de vie ?

Une fois qu'on a nos tours de garde (configs), on résout un **programme linéaire** :

```
Maximiser  : t₁ + t₂ + t₃   (durée de vie totale = somme des durées de chaque tour)

Contraintes : pour chaque capteur, sa batterie ne doit pas être dépassée :
  s1 (dans u1 et u2) : t₁ + t₂  ≤ 6   (T1 = 6)
  s2 (dans u1 et u3) : t₁ + t₃  ≤ 3   (T2 = 3)
  s3 (dans u2)       : t₂        ≤ 2   (T3 = 2)
  s4 (dans u3)       : t₃        ≤ 6   (T4 = 6)
  tₖ ≥ 0
```

Le solveur (CBC) trouve : t₁=3, t₂=2, t₃=0  → durée de vie = **8.5** unités de temps

### Résumé visuel

```
Temps →   0    3    5   8.5
Tour 1 :  [u1={s1,s2}  ]           (3 unités)
Tour 2 :       [u2={s1,s3}]        (2 unités)
Tour 3 :            [u3={s2,s4}]   (pas utilisé ici)
```

> **En résumé :**
> - **Configs élémentaires** = les combinaisons de capteurs qui peuvent couvrir toutes les zones
> - **Durée de vie (résultat)** = la durée totale maximale qu'on peut tenir en alternant entre ces configs

---

## 4. Pourquoi la qualité des configs est importante ?

Si on génère de "mauvaises" configs (peu diversifiées), le LP ne peut pas bien répartir les durées de vie.  
De "bonnes" configs exploitent mieux les batteries complémentaires.

**C'est là qu'interviennent les méthodes de recherche locale.**

---

## 5. Méthode de descente (hill climbing)

**Idée** : partir d'un ensemble de configs, essayer des voisins, prendre le meilleur.

```
Solution courante = {C1, C2, C3, ...}    (ensemble de configs)
Voisin            = remplacer Ci par Cj  (une nouvelle config)
Valeur            = durée de vie donnée par le LP

Algorithme :
  1. Générer une solution initiale (greedy)
  2. Explorer des voisins (tirage aléatoire dans le voisinage)
  3. Aller au meilleur voisin si il améliore la valeur courante
  4. Répéter jusqu'à ce qu'aucun voisin n'améliore → OPTIMUM LOCAL
```

**Problème** : on peut se retrouver bloqué dans un optimum local.

---

## 6. Recherche tabou

**Idée** : comme la descente, mais on se SOUVIENT des derniers mouvements
pour ne pas revenir en arrière. On peut alors traverser des zones moins bonnes.

```
Liste tabou = mémoire des K derniers mouvements interdits

Algorithme :
  1. Générer une solution initiale
  2. Explorer des voisins
  3. Prendre le MEILLEUR voisin non-tabou
     (même si ce voisin est moins bon que la solution courante !)
  4. Ajouter le mouvement effectué à la liste tabou
  5. Critère d'aspiration : si un mouvement tabou donne le meilleur résultat GLOBAL, l'accepter quand même
  6. Répéter jusqu'à max_iter ou patience épuisée
```

**Avantage** : on peut sortir des optima locaux car on accepte des dégradations temporaires.

### Illustration

```
Valeur
  ↑
  |        ★ meilleure solution trouvée
  |       /
  |      / ← tabou permet de descendre puis remonter
  |  /\/
  |/
  +------------------→ Itérations
   Descente s'arrête ici
```

---

## 7. Voisinage utilisé dans notre implémentation

**Swap de configuration** :  
Retirer une config de l'ensemble courant, en ajouter une nouvelle (depuis un pool pré-généré).

```
Avant : {C1, C2, C3, C4}
Après : {C1, C2, C4, C_nouvelle}   ← C3 retirée, C_nouvelle ajoutée
```

La config retirée est mise en **tabou** pendant `tenure` itérations.

**Aspiration** : si même le meilleur mouvement tabou dépasse la meilleure valeur globale, on l'accepte.

---

## 8. Utilisation en ligne de commande

```bash
# Méthode de descente sur un fichier
python main.py --fichier-txt instances/instance_moyen.txt --descente

# Recherche tabou sur un fichier
python main.py --fichier-txt instances/instance_moyen.txt --tabou

# Comparer toutes les méthodes
python main.py --fichier-txt instances/instance_moyen.txt --comparer

# Paramètres tabou personnalisés
python main.py --fichier-txt instances/instance_moyen.txt --tabou --tenure 15 --max-iter 300
```

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

## 4. Les deux heuristiques pour générer les configurations

### Heuristique 1 — Glouton aléatoire

On tire les capteurs dans un **ordre aléatoire** et on n'ajoute un capteur que
s'il couvre au moins une zone nouvelle. On répète cela plusieurs fois pour obtenir
des configs variées.

```
Répéter K fois :
  1. Mélanger les capteurs dans un ordre aléatoire
  2. Parcourir l'ordre : ajouter le capteur seulement s'il apporte de nouvelles zones
  3. Réduire la config obtenue pour la rendre élémentaire (retirer les capteurs superflus)
```

✅ Avantage : configurations très diversifiées  
⚠️ Inconvénient : peut rater certaines bonnes combinaisons

### Heuristique 2 — Glouton trié (intelligent)

À chaque étape, on choisit le capteur qui couvre le **maximum de zones non encore couvertes**.

```
Répéter K fois (avec une légère perturbation aléatoire) :
  1. Tant qu'il reste des zones à couvrir :
       - Choisir le capteur qui couvre le plus de zones restantes
       - L'ajouter à la configuration
  2. Réduire en configuration élémentaire
```

✅ Avantage : configurations de petite taille, proches du minimum  
⚠️ Inconvénient : moins diversifiées

---

## 5. Utilisation en ligne de commande

```bash
# Exemple du sujet (par défaut)
python main.py

# Saisie manuelle au clavier
python main.py --clavier

# Depuis un fichier texte
python main.py --fichier-txt instances/instance_moyen.txt

# Instance aléatoire (5 zones, 8 capteurs)
python main.py --aleatoire 5 8

# Changer la méthode de génération
python main.py --fichier-txt instances/instance_moyen.txt --methode glouton_trie
python main.py --fichier-txt instances/instance_moyen.txt --methode enumeration
python main.py --fichier-txt instances/instance_moyen.txt --methode toutes

# Contrôler le nombre de configurations générées
python main.py --fichier-txt instances/instance_moyen.txt --nb-configs 30

# Lancer les expériences (Parties 4 & 5)
python main.py --experiences
```

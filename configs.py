"""
configs.py - Génération de configurations élémentaires

Une configuration est un ensemble de capteurs qui couvre toutes les zones.
Une configuration est ÉLÉMENTAIRE si elle est minimale : retirer n'importe quel
capteur laisse au moins une zone non couverte.

Trois heuristiques proposées :
  1. Greedy aléatoire   - construction gloutonne avec tirage aléatoire
  2. Greedy trié        - construction gloutonne triée par couverture décroissante
  3. Enum backtracking  - énumération exhaustive (toutes les configs élémentaires)
"""

import random
from itertools import combinations


# ── Utilitaires ──────────────────────────────────────────────────────────────

def couvre_tout(config, instance):
    """Vérifie qu'un ensemble de capteurs couvre toutes les zones."""
    couvertes = set()
    for i in config:
        couvertes |= instance.zones[i]
    return couvertes == set(range(instance.M))


def est_elementaire(config, instance):
    """Vérifie qu'une configuration est minimale (aucun capteur superflu)."""
    config = list(config)
    for i in config:
        sans_i = [c for c in config if c != i]
        if couvre_tout(sans_i, instance):
            return False
    return True


def reduire_en_elementaire(config, instance):
    """Réduit une configuration valide en configuration élémentaire."""
    config = list(config)
    random.shuffle(config)
    i = 0
    while i < len(config):
        sans_i = config[:i] + config[i+1:]
        if couvre_tout(sans_i, instance):
            config = sans_i  # on retire le capteur superflu
        else:
            i += 1
    return frozenset(config)


# ── Heuristique 1 : Greedy aléatoire ────────────────────────────────────────

def heuristique_greedy_aleatoire(instance, nb_configs=None, seed=None):
    """
    Construit des configurations en ajoutant des capteurs tirés aléatoirement
    jusqu'à couvrir toutes les zones, puis réduit en config élémentaire.

    Avantage  : diversité des configs générées
    Inconvénient : peut produire des doublons si peu de capteurs
    """
    if seed is not None:
        random.seed(seed)

    if nb_configs is None:
        nb_configs = instance.N * 3

    configs = set()
    tentatives = 0
    max_tentatives = nb_configs * 20

    while len(configs) < nb_configs and tentatives < max_tentatives:
        tentatives += 1
        ordre = list(range(instance.N))
        random.shuffle(ordre)
        selectionnes = set()
        zones_couvertes = set()
        for i in ordre:
            if zones_couvertes < set(range(instance.M)):
                apport = instance.zones[i] - zones_couvertes
                if apport:
                    selectionnes.add(i)
                    zones_couvertes |= instance.zones[i]
        if couvre_tout(selectionnes, instance):
            configs.add(reduire_en_elementaire(selectionnes, instance))

    return list(configs)


# ── Heuristique 2 : Greedy trié par couverture ──────────────────────────────

def heuristique_greedy_trie(instance, nb_configs=None):
    """
    Construit des configurations en ajoutant les capteurs selon leur apport
    marginal décroissant à chaque étape (greedy déterministe avec perturbation).

    Avantage  : configs de petite taille (proches du minimum)
    Inconvénient : peu diversifiées sans perturbation
    """
    if nb_configs is None:
        nb_configs = instance.N * 2

    configs = set()

    for perturbation in range(nb_configs * 5):
        zones_restantes = set(range(instance.M))
        selectionnes = set()
        capteurs_dispo = list(range(instance.N))

        # légère perturbation pour diversifier
        random.shuffle(capteurs_dispo)

        while zones_restantes and capteurs_dispo:
            # Choisir le capteur qui couvre le plus de zones restantes
            # (avec brisure d'égalité aléatoire)
            meilleur_score = -1
            meilleur_i = None
            random.shuffle(capteurs_dispo)
            for i in capteurs_dispo:
                score = len(instance.zones[i] & zones_restantes)
                if score > meilleur_score:
                    meilleur_score = score
                    meilleur_i = i
            if meilleur_score == 0:
                break
            selectionnes.add(meilleur_i)
            zones_restantes -= instance.zones[meilleur_i]
            capteurs_dispo.remove(meilleur_i)

        if couvre_tout(selectionnes, instance):
            configs.add(reduire_en_elementaire(selectionnes, instance))

        if len(configs) >= nb_configs:
            break

    return list(configs)


# ── Heuristique 3 : Énumération exhaustive ──────────────────────────────────

def heuristique_enumeration(instance, limite=200):
    """
    Énumère toutes les configurations élémentaires par backtracking.
    Garantit l'optimalité de l'ensemble de configs mais coûteux pour N grand.

    Paramètre limite : nombre max de configs retournées (pour éviter explosion)
    """
    toutes = []
    N = instance.N
    M = instance.M
    zones_list = instance.zones

    def backtrack(start, config_courante, zones_couvertes):
        if zones_couvertes == set(range(M)):
            c = frozenset(config_courante)
            if est_elementaire(c, instance):
                toutes.append(c)
            return
        if len(toutes) >= limite:
            return
        for i in range(start, N):
            apport = zones_list[i] - zones_couvertes
            if apport:  # élagage : inutile d'ajouter un capteur sans apport
                config_courante.append(i)
                backtrack(i + 1, config_courante, zones_couvertes | zones_list[i])
                config_courante.pop()

    backtrack(0, [], set())
    return toutes


# ── Interface principale ─────────────────────────────────────────────────────

def generer_configurations(instance, methode="greedy_aleatoire", nb_configs=None, seed=42):
    """
    methode : "greedy_aleatoire" | "greedy_trie" | "enumeration" | "toutes"
    Retourne une liste de frozensets (indices capteurs 0-based).
    """
    if methode == "greedy_aleatoire":
        configs = heuristique_greedy_aleatoire(instance, nb_configs, seed=seed)
    elif methode == "greedy_trie":
        configs = heuristique_greedy_trie(instance, nb_configs)
    elif methode == "enumeration":
        configs = heuristique_enumeration(instance)
    elif methode == "toutes":
        c1 = set(map(frozenset, heuristique_greedy_aleatoire(instance, nb_configs, seed=seed)))
        c2 = set(map(frozenset, heuristique_greedy_trie(instance, nb_configs)))
        c3 = set(map(frozenset, heuristique_enumeration(instance)))
        configs = list(c1 | c2 | c3)
    else:
        raise ValueError(f"Méthode inconnue : {methode}")

    # Dédoublonnage final
    return list(set(configs))


def afficher_configurations(configs, instance):
    print(f"{len(configs)} configuration(s) élémentaire(s) :")
    for k, c in enumerate(configs):
        capteurs_str = "{" + ", ".join(f"s{i+1}" for i in sorted(c)) + "}"
        zones_str = "{" + ", ".join(f"z{z+1}" for z in sorted(set().union(*[instance.zones[i] for i in c]))) + "}"
        print(f"  u{k+1} = {capteurs_str}  →  zones {zones_str}")
    print()
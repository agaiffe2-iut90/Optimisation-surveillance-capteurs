"""
data.py - Gestion des données du problème de surveillance par capteurs
"""

import json
import random


class Instance:
    """Représente une instance du problème de surveillance."""

    def __init__(self, nb_zones, nb_capteurs, zones_par_capteur, durees_vie):
        """
        nb_zones          : int - nombre de zones à surveiller
        nb_capteurs       : int - nombre de capteurs disponibles
        zones_par_capteur : list[set] - zones[i] = ensemble des zones couvertes par le capteur i
        durees_vie        : list[float] - durees_vie[i] = durée de vie du capteur i
        """
        self.M = nb_zones
        self.N = nb_capteurs
        self.zones = zones_par_capteur   # liste de sets, indices 0-based
        self.T = durees_vie

    def afficher(self):
        print(f"Nombre de zones    : {self.M}")
        print(f"Nombre de capteurs : {self.N}")
        print(f"{'Capteur':<10} {'Zones couvertes':<30} {'Durée de vie'}")
        print("-" * 55)
        for i in range(self.N):
            zones_str = "{" + ", ".join(f"z{z+1}" for z in sorted(self.zones[i])) + "}"
            print(f"s{i+1:<9} {zones_str:<30} T{i+1} = {self.T[i]}")
        print()


def lire_depuis_fichier(chemin):
    """
    Lit une instance depuis un fichier JSON.

    Format attendu :
    {
        "nb_zones": 3,
        "nb_capteurs": 4,
        "capteurs": [
            {"zones": [0, 1], "duree_vie": 6},
            {"zones": [1, 2], "duree_vie": 3},
            ...
        ]
    }
    """
    with open(chemin, "r") as f:
        data = json.load(f)

    nb_zones = data["nb_zones"]
    nb_capteurs = data["nb_capteurs"]
    zones_par_capteur = [set(c["zones"]) for c in data["capteurs"]]
    durees_vie = [c["duree_vie"] for c in data["capteurs"]]

    return Instance(nb_zones, nb_capteurs, zones_par_capteur, durees_vie)


def saisir_au_clavier():
    """Saisie interactive des données par l'utilisateur."""
    print("=== Saisie de l'instance ===")
    M = int(input("Nombre de zones à surveiller : "))
    N = int(input("Nombre de capteurs           : "))

    zones_par_capteur = []
    durees_vie = []

    for i in range(N):
        print(f"\nCapteur s{i+1} :")
        zones_str = input(f"  Zones couvertes (numéros 1..{M} séparés par espaces) : ")
        zones = set(int(z) - 1 for z in zones_str.split())
        duree = float(input(f"  Durée de vie : "))
        zones_par_capteur.append(zones)
        durees_vie.append(duree)

    return Instance(M, N, zones_par_capteur, durees_vie)


def generer_aleatoire(nb_zones, nb_capteurs, duree_min=1, duree_max=10, seed=None):
    """
    Génère une instance aléatoire en garantissant que chaque zone
    est couverte par au moins un capteur.
    """
    if seed is not None:
        random.seed(seed)

    zones_par_capteur = [set() for _ in range(nb_capteurs)]

    # Garantir que chaque zone est couverte par au moins un capteur
    for z in range(nb_zones):
        i = random.randint(0, nb_capteurs - 1)
        zones_par_capteur[i].add(z)

    # Ajouter des zones supplémentaires aléatoirement
    for i in range(nb_capteurs):
        nb_extra = random.randint(0, nb_zones // 2)
        for _ in range(nb_extra):
            zones_par_capteur[i].add(random.randint(0, nb_zones - 1))

    durees_vie = [float(random.randint(duree_min, duree_max)) for _ in range(nb_capteurs)]

    return Instance(nb_zones, nb_capteurs, zones_par_capteur, durees_vie)


# ── Instance de l'exemple du sujet ──────────────────────────────────────────

def instance_exemple():
    """Retourne l'instance de l'exemple du sujet (4 capteurs, 3 zones)."""
    zones = [
        {0, 1},   # s1 couvre z1, z2
        {1, 2},   # s2 couvre z2, z3
        {2},      # s3 couvre z3
        {0, 2},   # s4 couvre z1, z3
    ]
    durees = [6, 3, 2, 6]
    return Instance(3, 4, zones, durees)
"""
experiences.py - Parties 4 et 5 du projet

Partie 4 : Résolution sur plusieurs instances
Partie 5 : Influence du nombre et type de configs sur la durée de vie
"""

import json
import os

from data import lire_depuis_fichier, instance_exemple, generer_aleatoire
from configs import generer_configurations, afficher_configurations
from solver import resoudre, afficher_solution


METHODES = ["greedy_aleatoire", "greedy_trie", "enumeration"]
LABELS    = {
    "greedy_aleatoire": "Greedy aléatoire",
    "greedy_trie"     : "Greedy trié",
    "enumeration"     : "Énumération",
}
INSTANCES_DIR = os.path.join(os.path.dirname(__file__), "instances")


# ── Partie 4 : instances fixes ────────────────────────────────────────────────

def charger_instances():
    """Charge toutes les instances JSON du dossier instances/."""
    instances = {}
    if not os.path.isdir(INSTANCES_DIR):
        return instances
    for fname in sorted(os.listdir(INSTANCES_DIR)):
        if fname.endswith(".json"):
            chemin = os.path.join(INSTANCES_DIR, fname)
            nom = fname.replace(".json", "")
            instances[nom] = lire_depuis_fichier(chemin)
    return instances


def partie4(instances):
    """Résout chaque instance avec l'énumération et affiche les résultats."""
    print("\n" + "=" * 60)
    print("PARTIE 4 — Résolution des instances")
    print("=" * 60)

    resultats = {}
    for nom, inst in instances.items():
        print(f"\n--- Instance : {nom} ---")
        inst.afficher()
        configs = generer_configurations(inst, methode="enumeration")
        if not configs:
            print("Aucune configuration trouvée.\n")
            continue
        afficher_configurations(configs, inst)
        sol = resoudre(inst, configs, verbose=False)
        afficher_solution(inst, sol)
        resultats[nom] = sol["duree_vie"] if sol else None

    # Tableau récapitulatif
    print("\n" + "=" * 60)
    print("RÉCAPITULATIF PARTIE 4")
    print("=" * 60)
    print(f"{'Instance':<20} {'Durée de vie optimale':>22}")
    print("-" * 44)
    for nom, dv in resultats.items():
        val_str = f"{dv:.4f}" if dv is not None else "N/A"
        print(f"{nom:<20} {val_str:>22}")
    print()
    return resultats


# ── Partie 5 : influence des configs ─────────────────────────────────────────

def partie5(instances):
    """
    Pour chaque instance, compare les 3 heuristiques et l'influence
    du nombre de configs générées sur la durée de vie du réseau.
    """
    print("\n" + "=" * 60)
    print("PARTIE 5 — Influence des configurations élémentaires")
    print("=" * 60)

    for nom, inst in instances.items():
        print(f"\n--- Instance : {nom} ---")
        _comparer_methodes(inst, nom)
        _comparer_nb_configs(inst, nom)


def _comparer_methodes(instance, nom_instance):
    """Compare les 3 heuristiques sur une même instance."""
    print(f"\n  Comparaison des heuristiques (instance {nom_instance}) :")
    print(f"  {'Heuristique':<22} {'Nb configs':>12} {'Durée de vie':>14}")
    print("  " + "-" * 50)

    for methode in METHODES:
        configs = generer_configurations(instance, methode=methode)
        if not configs:
            print(f"  {LABELS[methode]:<22} {'—':>12} {'—':>14}")
            continue
        sol = resoudre(instance, configs, verbose=False)
        dv = sol["duree_vie"] if sol else float("nan")
        print(f"  {LABELS[methode]:<22} {len(configs):>12} {dv:>14.4f}")


def _comparer_nb_configs(instance, nom_instance, nb_list=None):
    """
    Pour les heuristiques greedy, montre l'influence du nombre
    de configs générées sur la durée de vie.
    """
    if nb_list is None:
        nb_list = [2, 5, 10, 20, 50]

    print(f"\n  Influence du nombre de configs (greedy aléatoire) :")
    print(f"  {'Nb configs demandé':>22} {'Nb obtenus':>12} {'Durée de vie':>14}")
    print("  " + "-" * 50)

    for nb in nb_list:
        configs = generer_configurations(instance, methode="greedy_aleatoire",
                                         nb_configs=nb, seed=0)
        if not configs:
            continue
        sol = resoudre(instance, configs, verbose=False)
        dv = sol["duree_vie"] if sol else float("nan")
        print(f"  {nb:>22} {len(configs):>12} {dv:>14.4f}")


# ── Lancement complet ─────────────────────────────────────────────────────────

def lancer_experiences():
    instances = {"exemple_sujet": instance_exemple()}

    # Ajout des instances JSON si présentes
    instances.update(charger_instances())

    # Instances aléatoires supplémentaires
    instances["aleatoire_5z_6c"]  = generer_aleatoire(5, 6,  seed=1)
    instances["aleatoire_4z_8c"]  = generer_aleatoire(4, 8,  seed=2)
    instances["aleatoire_6z_10c"] = generer_aleatoire(6, 10, seed=3)

    partie4(instances)
    partie5(instances)
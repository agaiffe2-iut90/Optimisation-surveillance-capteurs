"""
main.py - Point d'entrée du projet surveillance par capteurs

Usage :
  python main.py                        → résout l'exemple du sujet
  python main.py --fichier mon_inst.json → charge une instance depuis un fichier
  python main.py --aleatoire 5 8        → instance aléatoire (5 zones, 8 capteurs)
  python main.py --clavier              → saisie interactive
  python main.py --experiences          → lance toutes les expériences (Parties 4 & 5)
"""

import argparse
import os
import sys

from data import instance_exemple, lire_depuis_fichier, generer_aleatoire, Instance
from configs import generer_configurations, afficher_configurations
from solver import resoudre, afficher_solution
from experiences import lancer_experiences


# ── Résolution d'une instance avec une méthode donnée ────────────────────────

def resoudre_instance(instance, methode="greedy_aleatoire", nb_configs=None, verbose=True):
    instance.afficher()
    configs = generer_configurations(instance, methode=methode, nb_configs=nb_configs)
    if not configs:
        print("Aucune configuration élémentaire trouvée.")
        return None
    if verbose:
        afficher_configurations(configs, instance)
    solution = resoudre(instance, configs, verbose=verbose)
    if verbose:
        afficher_solution(instance, solution)
    return solution


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Problème d'activation de capteurs pour surveillance de zones"
    )
    parser.add_argument("--fichier",    type=str, help="Chemin vers un fichier JSON d'instance")
    parser.add_argument("--aleatoire",  nargs=2,  metavar=("M", "N"), type=int,
                        help="Génère une instance aléatoire (M zones, N capteurs)")
    parser.add_argument("--clavier",    action="store_true", help="Saisie au clavier")
    parser.add_argument("--methode",    type=str, default="greedy_aleatoire",
                        choices=["greedy_aleatoire", "greedy_trie", "enumeration", "toutes"],
                        help="Heuristique de génération des configurations")
    parser.add_argument("--nb-configs", type=int, default=None,
                        help="Nombre de configurations à générer (heuristiques 1 & 2)")
    parser.add_argument("--experiences", action="store_true",
                        help="Lance les expériences comparatives (Parties 4 & 5)")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.experiences:
        lancer_experiences()
        return

    # Chargement de l'instance
    if args.fichier:
        print(f"Chargement depuis {args.fichier}...")
        instance = lire_depuis_fichier(args.fichier)
    elif args.aleatoire:
        M, N = args.aleatoire
        print(f"Génération d'une instance aléatoire ({M} zones, {N} capteurs)...")
        instance = generer_aleatoire(M, N, seed=42)
    elif args.clavier:
        from data import saisir_au_clavier
        instance = saisir_au_clavier()
    else:
        print("=== Instance de l'exemple du sujet ===\n")
        instance = instance_exemple()

    resoudre_instance(instance, methode=args.methode, nb_configs=args.nb_configs)


if __name__ == "__main__":
    main()
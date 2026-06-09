"""
main.py - Point d'entrée du projet surveillance par capteurs

Usage :
  python main.py                              → résout l'exemple du sujet
  python main.py --clavier                    → saisie des données au clavier
  python main.py --fichier-txt instances/instance_moyen.txt
  python main.py --aleatoire 5 8             → instance aléatoire (5 zones, 8 capteurs)
  python main.py --methode glouton_trie      → heuristique gloutonne triée
  python main.py --experiences               → expériences Parties 4 & 5
"""

import argparse
import os
import sys

from data import instance_exemple, lire_depuis_fichier_texte, generer_aleatoire, Instance
from configs import generer_configurations, afficher_configurations
from solver import resoudre, afficher_solution
from experiences import lancer_experiences

#python main.py --fichier-txt instances/instance_moyen.txt
#python main.py --fichier-txt instances/moyen_test_2.txt
#python main.py --fichier-txt instances/gros_test_1.txt
#python main.py --fichier-txt instances/maxi_test_1.txt


# ── Résolution d'une instance ─────────────────────────────────────────────────

def resoudre_instance(instance, methode="glouton_aleatoire", nb_configs=None, verbose=True):
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
    parser.add_argument("--fichier-txt", type=str, metavar="CHEMIN",
                        help="Chemin vers un fichier texte (format : N / M / durées / zones)")
    parser.add_argument("--aleatoire",  nargs=2,  metavar=("M", "N"), type=int,
                        help="Génère une instance aléatoire (M zones, N capteurs)")
    parser.add_argument("--clavier",    action="store_true",
                        help="Saisie manuelle des données au clavier")
    parser.add_argument("--methode",    type=str, default="glouton_aleatoire",
                        choices=["glouton_aleatoire", "glouton_trie", "enumeration", "toutes"],
                        help="Heuristique de génération des configurations (défaut: glouton_aleatoire)")
    parser.add_argument("--nb-configs", type=int, default=None,
                        help="Nombre de configurations à générer")
    parser.add_argument("--experiences", action="store_true",
                        help="Lance les expériences comparatives (Parties 4 & 5)")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.experiences:
        lancer_experiences()
        return

    # ── Chargement de l'instance ──────────────────────────────────────────────
    fichier_txt = getattr(args, "fichier_txt", None)
    if fichier_txt:
        print(f"Chargement depuis {fichier_txt}...")
        instance = lire_depuis_fichier_texte(fichier_txt)
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

    # ── Résolution ────────────────────────────────────────────────────────────
    resoudre_instance(instance, methode=args.methode, nb_configs=args.nb_configs)


if __name__ == "__main__":
    main()
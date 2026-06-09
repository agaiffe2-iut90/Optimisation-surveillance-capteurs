"""
main.py - Point d'entrée du projet surveillance par capteurs

Usage :
  python main.py                                   → résout l'exemple du sujet (glouton + LP)
  python main.py --fichier-txt inst.txt --tabou    → résolution par recherche tabou
  python main.py --fichier-txt inst.txt --descente → résolution par descente
  python main.py --fichier-txt inst.txt --comparer → compare glouton / descente / tabou
  python main.py --aleatoire 5 8                   → instance aléatoire (5 zones, 8 capteurs)
  python main.py --experiences                     → expériences Parties 4 & 5
"""

import argparse
import os
import sys

from data import instance_exemple, lire_depuis_fichier, lire_depuis_fichier_texte, generer_aleatoire, Instance
from configs import generer_configurations, afficher_configurations
from solver import resoudre, afficher_solution
from experiences import lancer_experiences
from tabou import descente, tabou, comparer_methodes


# ── Résolution d'une instance avec une méthode donnée ────────────────────────

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
    parser.add_argument("--fichier",    type=str, help="Chemin vers un fichier JSON d'instance")
    parser.add_argument("--fichier-txt", type=str, metavar="CHEMIN",
                        help="Chemin vers un fichier texte au format annexe (N / M / durées / zones)")
    parser.add_argument("--aleatoire",  nargs=2,  metavar=("M", "N"), type=int,
                        help="Génère une instance aléatoire (M zones, N capteurs)")
    parser.add_argument("--clavier",    action="store_true", help="Saisie au clavier")
    parser.add_argument("--methode",    type=str, default="glouton_aleatoire",
                        choices=["glouton_aleatoire", "glouton_trie", "enumeration", "toutes"],
                        help="Heuristique de génération des configurations")
    parser.add_argument("--nb-configs", type=int, default=None,
                        help="Nombre de configurations à générer (heuristiques gloutonnes)")
    parser.add_argument("--experiences", action="store_true",
                        help="Lance les expériences comparatives (Parties 4 & 5)")
    # ── Méthodes de recherche locale ──
    parser.add_argument("--descente",   action="store_true",
                        help="Résolution par méthode de descente (hill climbing)")
    parser.add_argument("--tabou",      action="store_true",
                        help="Résolution par recherche tabou")
    parser.add_argument("--comparer",   action="store_true",
                        help="Compare glouton / descente / tabou sur l'instance")
    parser.add_argument("--tenure",     type=int, default=10,
                        help="Durée de vie d'un mouvement tabou (défaut: 10)")
    parser.add_argument("--max-iter",   type=int, default=200,
                        help="Nombre max d'itérations pour tabou/descente (défaut: 200)")
    parser.add_argument("--nb-voisins", type=int, default=20,
                        help="Taille du voisinage exploré à chaque itération (défaut: 20)")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.experiences:
        lancer_experiences()
        return

    # ── Chargement de l'instance ──────────────────────────────────────────────
    fichier_txt = getattr(args, "fichier_txt", None)
    if fichier_txt:
        print(f"Chargement depuis {fichier_txt} (format texte)...")
        instance = lire_depuis_fichier_texte(fichier_txt)
    elif args.fichier:
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

    # ── Sélection de la méthode ───────────────────────────────────────────────
    max_iter = getattr(args, "max_iter", 200)
    nb_voisins = getattr(args, "nb_voisins", 20)

    if args.comparer:
        instance.afficher()
        comparer_methodes(instance, nb_runs=3)

    elif args.tabou:
        instance.afficher()
        val, configs, _ = tabou(
            instance,
            nb_voisins=nb_voisins,
            max_iter=max_iter,
            tenure=args.tenure,
            verbose=True,
        )
        print(f"\n→ Durée de vie (tabou) : {val:.4f} unités de temps")

    elif args.descente:
        instance.afficher()
        val, configs, _ = descente(
            instance,
            nb_voisins=nb_voisins,
            max_iter=max_iter,
            verbose=True,
        )
        print(f"\n→ Durée de vie (descente) : {val:.4f} unités de temps")

    else:
        # Par défaut : glouton + LP
        resoudre_instance(instance, methode=args.methode, nb_configs=args.nb_configs)


if __name__ == "__main__":
    main()
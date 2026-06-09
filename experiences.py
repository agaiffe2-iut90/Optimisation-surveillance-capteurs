"""
experiences.py - Parties 4 et 5 du projet

Partie 4 : Résolution sur plusieurs instances
Partie 5 : Influence du nombre et type de configs sur la durée de vie
           → génère des graphiques .png dans le dossier courant
"""

import os

import matplotlib
matplotlib.use("Agg")          # backend sans fenêtre (compatible serveur / CI)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from data import instance_exemple, generer_aleatoire
from configs import generer_configurations, afficher_configurations
from solver import resoudre, afficher_solution


METHODES = ["glouton_aleatoire", "glouton_trie"]
LABELS    = {
    "glouton_aleatoire": "Glouton aléatoire",
    "glouton_trie"     : "Glouton trié",
}
COULEURS  = {
    "glouton_aleatoire": "#4C72B0",
    "glouton_trie"     : "#DD8452",
}
INSTANCES_DIR = os.path.join(os.path.dirname(__file__), "instances")
GRAPHIQUES_DIR = os.path.dirname(__file__)


# ── Styles communs ────────────────────────────────────────────────────────────

def _style_global():
    """Applique un style homogène à tous les graphiques."""
    plt.rcParams.update({
        "figure.facecolor"  : "#1e1e2e",
        "axes.facecolor"    : "#1e1e2e",
        "axes.edgecolor"    : "#45475a",
        "axes.labelcolor"   : "#cdd6f4",
        "axes.titlecolor"   : "#cdd6f4",
        "axes.titlesize"    : 13,
        "axes.labelsize"    : 11,
        "axes.grid"         : True,
        "grid.color"        : "#313244",
        "grid.linestyle"    : "--",
        "grid.linewidth"    : 0.6,
        "xtick.color"       : "#cdd6f4",
        "ytick.color"       : "#cdd6f4",
        "xtick.labelsize"   : 9,
        "ytick.labelsize"   : 9,
        "legend.facecolor"  : "#313244",
        "legend.edgecolor"  : "#45475a",
        "legend.labelcolor" : "#cdd6f4",
        "legend.fontsize"   : 9,
        "text.color"        : "#cdd6f4",
        "savefig.facecolor" : "#1e1e2e",
        "savefig.dpi"       : 150,
    })


# ── Partie 4 : instances fixes ────────────────────────────────────────────────

def partie4(instances):
    """Résout chaque instance avec l'énumération et affiche les résultats."""
    print("\n" + "=" * 60)
    print("PARTIE 4 — Résolution des instances")
    print("=" * 60)

    resultats = {}
    for nom, inst in instances.items():
        print(f"\n--- Instance : {nom} ---")
        inst.afficher()
        configs = generer_configurations(inst, methode="toutes")
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

    # ── Graphique Partie 4 ─────────────────────────────────────────────────
    _graphique_partie4(resultats)

    return resultats


def _graphique_partie4(resultats):
    """Graphique en barres : durée de vie optimale par instance."""
    _style_global()

    noms  = list(resultats.keys())
    vals  = [v if v is not None else 0 for v in resultats.values()]
    x     = np.arange(len(noms))
    largeur = 0.55

    fig, ax = plt.subplots(figsize=(max(7, len(noms) * 1.4), 5))
    fig.suptitle("Partie 4 — Durée de vie optimale par instance",
                 fontsize=14, fontweight="bold", y=0.98)

    barres = ax.bar(x, vals, width=largeur, color="#89b4fa",
                    edgecolor="#1e1e2e", linewidth=0.8, zorder=3)

    # Étiquettes sur les barres
    for rect, val in zip(barres, vals):
        if val > 0:
            ax.text(rect.get_x() + rect.get_width() / 2,
                    rect.get_height() + max(vals) * 0.015,
                    f"{val:.2f}", ha="center", va="bottom",
                    fontsize=9, color="#cdd6f4", fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(noms, rotation=20, ha="right")
    ax.set_ylabel("Durée de vie optimale (unités de temps)")
    ax.set_xlabel("Instance")
    ax.set_ylim(0, max(vals) * 1.18 if vals else 1)

    plt.tight_layout()
    chemin = os.path.join(GRAPHIQUES_DIR, "graphique_partie4.png")
    plt.savefig(chemin)
    plt.close()
    print(f"[Graphique] Sauvegardé → {chemin}")


# ── Partie 5 : influence des configs ─────────────────────────────────────────

def partie5(instances):
    """
    Pour chaque instance, compare les 3 heuristiques et l'influence
    du nombre de configs générées sur la durée de vie du réseau.
    """
    print("\n" + "=" * 60)
    print("PARTIE 5 — Influence des configurations élémentaires")
    print("=" * 60)

    tableau_methodes  = {}  # {nom_instance: {methode: (nb_configs, duree_vie)}}
    tableau_nb_configs = {}  # {nom_instance: [(nb_demande, nb_obtenu, duree_vie)]}

    for nom, inst in instances.items():
        print(f"\n--- Instance : {nom} ---")
        tableau_methodes[nom]   = _comparer_methodes(inst, nom)
        tableau_nb_configs[nom] = _comparer_nb_configs(inst, nom)

    # ── Graphiques ─────────────────────────────────────────────────────────
    _graphique_comparaison_methodes(tableau_methodes)
    _graphique_influence_nb_configs(tableau_nb_configs)


def _comparer_methodes(instance, nom_instance):
    """Compare les 3 heuristiques sur une même instance."""
    print(f"\n  Comparaison des heuristiques (instance {nom_instance}) :")
    print(f"  {'Heuristique':<22} {'Nb configs':>12} {'Durée de vie':>14}")
    print("  " + "-" * 50)

    resultats = {}
    for methode in METHODES:
        configs = generer_configurations(instance, methode=methode)
        if not configs:
            print(f"  {LABELS[methode]:<22} {'—':>12} {'—':>14}")
            resultats[methode] = (0, None)
            continue
        sol = resoudre(instance, configs, verbose=False)
        dv  = sol["duree_vie"] if sol else float("nan")
        print(f"  {LABELS[methode]:<22} {len(configs):>12} {dv:>14.4f}")
        resultats[methode] = (len(configs), dv)

    return resultats


def _comparer_nb_configs(instance, nom_instance, nb_list=None):
    """
    Pour les heuristiques gloutonnes, montre l'influence du nombre
    de configs générées sur la durée de vie.
    """
    if nb_list is None:
        nb_list = [2, 5, 10, 20, 50]

    print(f"\n  Influence du nombre de configs (glouton aléatoire) :")
    print(f"  {'Nb configs demandé':>22} {'Nb obtenus':>12} {'Durée de vie':>14}")
    print("  " + "-" * 50)

    resultats = []
    for nb in nb_list:
        configs = generer_configurations(instance, methode="glouton_aleatoire",
                                         nb_configs=nb, seed=0)
        if not configs:
            continue
        sol = resoudre(instance, configs, verbose=False)
        dv  = sol["duree_vie"] if sol else float("nan")
        print(f"  {nb:>22} {len(configs):>12} {dv:>14.4f}")
        resultats.append((nb, len(configs), dv))

    return resultats


# ── Graphiques Partie 5 ───────────────────────────────────────────────────────

def _graphique_comparaison_methodes(tableau):
    """
    Graphique groupé : pour chaque instance, 3 barres (une par heuristique)
    montrant la durée de vie obtenue.
    """
    _style_global()

    noms_instances = list(tableau.keys())
    n_instances    = len(noms_instances)
    n_methodes     = len(METHODES)
    x              = np.arange(n_instances)
    largeur        = 0.22
    offsets        = np.linspace(-(n_methodes - 1) / 2,
                                  (n_methodes - 1) / 2,
                                  n_methodes) * largeur

    fig, ax = plt.subplots(figsize=(max(8, n_instances * 2.2), 5))
    fig.suptitle("Partie 5 — Comparaison des heuristiques par instance",
                 fontsize=14, fontweight="bold", y=0.98)

    for idx, methode in enumerate(METHODES):
        vals = []
        for nom in noms_instances:
            nb_c, dv = tableau[nom].get(methode, (0, None))
            vals.append(dv if dv is not None and not (isinstance(dv, float) and dv != dv) else 0)

        barres = ax.bar(x + offsets[idx], vals, width=largeur,
                        label=LABELS[methode],
                        color=COULEURS[methode],
                        edgecolor="#1e1e2e", linewidth=0.6, zorder=3)

        for rect, val in zip(barres, vals):
            if val > 0:
                ax.text(rect.get_x() + rect.get_width() / 2,
                        rect.get_height() + 0.05,
                        f"{val:.1f}", ha="center", va="bottom",
                        fontsize=7.5, color="#cdd6f4")

    ax.set_xticks(x)
    ax.set_xticklabels(noms_instances, rotation=20, ha="right")
    ax.set_ylabel("Durée de vie optimale (unités de temps)")
    ax.set_xlabel("Instance")
    ax.legend(loc="upper right")

    plt.tight_layout()
    chemin = os.path.join(GRAPHIQUES_DIR, "graphique_partie5_methodes.png")
    plt.savefig(chemin)
    plt.close()
    print(f"\n[Graphique] Sauvegardé → {chemin}")


def _graphique_influence_nb_configs(tableau):
    """
    Graphique en lignes : pour chaque instance, évolution de la durée de vie
    en fonction du nombre de configurations générées (glouton aléatoire).
    """
    _style_global()

    noms_instances = list(tableau.keys())
    # Palette de couleurs distinctes pour les instances
    palette = ["#89b4fa", "#a6e3a1", "#fab387", "#f38ba8",
               "#cba6f7", "#94e2d5", "#f9e2af"]

    fig, ax = plt.subplots(figsize=(9, 5))
    fig.suptitle("Partie 5 — Influence du nombre de configurations (glouton aléatoire)",
                 fontsize=13, fontweight="bold", y=0.98)

    for idx, nom in enumerate(noms_instances):
        donnees = tableau[nom]
        if not donnees:
            continue
        nb_demandes = [d[0] for d in donnees]
        durees      = [d[2] for d in donnees]
        couleur     = palette[idx % len(palette)]

        ax.plot(nb_demandes, durees,
                marker="o", linewidth=2, markersize=6,
                color=couleur, label=nom, zorder=3)

        # Annotation du dernier point
        if durees:
            ax.annotate(f"{durees[-1]:.2f}",
                        xy=(nb_demandes[-1], durees[-1]),
                        xytext=(5, 4), textcoords="offset points",
                        fontsize=8, color=couleur)

    ax.set_xlabel("Nombre de configurations demandées")
    ax.set_ylabel("Durée de vie optimale (unités de temps)")
    ax.legend(loc="lower right", title="Instance")
    ax.set_xscale("symlog", linthresh=5)    # échelle quasi-log pour mieux voir [2..50]

    plt.tight_layout()
    chemin = os.path.join(GRAPHIQUES_DIR, "graphique_partie5_nb_configs.png")
    plt.savefig(chemin)
    plt.close()
    print(f"[Graphique] Sauvegardé → {chemin}")


# ── Lancement complet ─────────────────────────────────────────────────────────

def lancer_experiences():
    instances = {"exemple_sujet": instance_exemple()}

    partie4(instances)
    partie5(instances)
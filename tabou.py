"""
tabou.py - Méthodes de recherche locale : Descente & Recherche Tabou

Espace de recherche : ensembles de configurations élémentaires
Évaluation         : résolution du LP → durée de vie du réseau
Voisinage          : remplacer une config par une autre (swap)
"""

import random
import time

from configs import generer_configurations, reduire_en_elementaire, couvre_tout
from solver import resoudre_pulp


# ── Évaluation ────────────────────────────────────────────────────────────────

def evaluer(instance, configs):
    """Résout le LP sur l'ensemble de configs, retourne la durée de vie."""
    if not configs:
        return 0.0
    result = resoudre_pulp(instance, list(configs), verbose=False)
    return result[0] if result else 0.0


# ── Génération du pool de configs ─────────────────────────────────────────────

def _config_aleatoire(instance):
    """Construit une configuration élémentaire aléatoire."""
    ordre = list(range(instance.N))
    random.shuffle(ordre)
    sel, couvertes = set(), set()
    for i in ordre:
        apport = instance.zones[i] - couvertes
        if apport:
            sel.add(i)
            couvertes |= instance.zones[i]
        if couvertes == set(range(instance.M)):
            break
    if not couvre_tout(sel, instance):
        return None
    return reduire_en_elementaire(sel, instance)


def generer_pool(instance, taille=300, seed=None):
    """Génère un pool diversifié de configurations élémentaires."""
    if seed is not None:
        random.seed(seed)
    pool = set()
    tentatives = 0
    while len(pool) < taille and tentatives < taille * 25:
        tentatives += 1
        c = _config_aleatoire(instance)
        if c:
            pool.add(c)
    return list(pool)


# ── Voisinage ─────────────────────────────────────────────────────────────────

def generer_voisins(configs_courantes, pool, nb_voisins=20):
    """
    Génère des voisins par swap : retire une config, en ajoute une du pool.
    Retourne une liste de (nouvelles_configs, config_retirée, config_ajoutée).
    """
    configs_set = set(configs_courantes)
    candidats = [c for c in pool if c not in configs_set]
    if not candidats:
        return []

    voisins = []
    for _ in range(nb_voisins):
        retirée = random.choice(configs_courantes)
        ajoutée = random.choice(candidats)
        nouvelle = [c for c in configs_courantes if c != retirée] + [ajoutée]
        voisins.append((nouvelle, retirée, ajoutée))
    return voisins


# ── Méthode de descente ───────────────────────────────────────────────────────

def descente(instance, configs_initiales=None, nb_voisins=15,
             max_iter=100, timeout=60, verbose=True):
    """
    Hill climbing : à chaque itération, prend le meilleur voisin améliorant.
    S'arrête quand aucun voisin n'améliore (optimum local).

    Retourne : (meilleure_valeur, meilleures_configs, historique_valeurs)
    """
    if configs_initiales is None:
        configs_initiales = generer_configurations(instance, methode="glouton_aleatoire")

    pool = generer_pool(instance, taille=max(200, instance.N * 5))
    pool = list(set(pool) | set(configs_initiales))

    sol = list(configs_initiales)
    val = evaluer(instance, sol)
    historique = [val]
    t0 = time.time()

    if verbose:
        print(f"\n=== Méthode de descente ===")
        print(f"Valeur initiale : {val:.4f}  ({len(sol)} configs)")

    for it in range(max_iter):
        if time.time() - t0 > timeout:
            if verbose:
                print(f"Timeout ({timeout}s) atteint à l'itération {it+1}")
            break

        voisins = generer_voisins(sol, pool, nb_voisins)
        if not voisins:
            break

        meilleur_sol, meilleur_val = None, val
        for (nouvelle, _, _) in voisins:
            v = evaluer(instance, nouvelle)
            if v > meilleur_val:
                meilleur_val, meilleur_sol = v, nouvelle

        if meilleur_sol is None:
            if verbose:
                print(f"Optimum local atteint à l'itération {it+1}")
            break

        sol, val = meilleur_sol, meilleur_val
        historique.append(val)
        if verbose:
            print(f"  Iter {it+1:3d} : {val:.4f}")

    if verbose:
        print(f"Résultat final : {val:.4f}")
    return val, sol, historique


# ── Recherche tabou ───────────────────────────────────────────────────────────

def tabou(instance, configs_initiales=None, nb_voisins=20, max_iter=200,
          tenure=10, patience=40, timeout=120, verbose=True):
    """
    Recherche tabou :
      - Même principe que la descente, mais on accepte aussi des dégradations.
      - On interdit les mouvements récents via une liste tabou (tenure itérations).
      - Critère d'aspiration : un mouvement tabou est quand même accepté s'il
        donne la meilleure solution globale jamais trouvée.

    Paramètres :
      tenure   : durée pendant laquelle un mouvement reste interdit
      patience : arrêt si pas d'amélioration pendant 'patience' itérations

    Retourne : (meilleure_valeur, meilleures_configs, historique_valeurs)
    """
    if configs_initiales is None:
        configs_initiales = generer_configurations(instance, methode="glouton_aleatoire")

    pool = generer_pool(instance, taille=max(200, instance.N * 5))
    pool = list(set(pool) | set(configs_initiales))

    sol = list(configs_initiales)
    val = evaluer(instance, sol)

    best_sol, best_val = sol[:], val
    # Liste tabou : config_retirée → itération d'expiration
    liste_tabou = {}
    historique = [val]
    sans_amelio = 0
    t0 = time.time()

    if verbose:
        print(f"\n=== Recherche tabou (tenure={tenure}, patience={patience}) ===")
        print(f"Valeur initiale : {val:.4f}  ({len(sol)} configs)")

    for it in range(max_iter):
        if time.time() - t0 > timeout:
            if verbose:
                print(f"Timeout ({timeout}s) atteint à l'itération {it+1}")
            break
        if sans_amelio >= patience:
            if verbose:
                print(f"Arrêt : {patience} itérations sans amélioration")
            break

        voisins = generer_voisins(sol, pool, nb_voisins)
        if not voisins:
            break

        meilleur_sol, meilleur_val, meilleur_mv = None, -1.0, None

        for (nouvelle, retirée, ajoutée) in voisins:
            est_tabou = (retirée in liste_tabou and liste_tabou[retirée] > it)
            v = evaluer(instance, nouvelle)

            # Critère d'aspiration : on passe outre le tabou si c'est le meilleur global
            aspiration = v > best_val

            if (not est_tabou or aspiration) and v > meilleur_val:
                meilleur_val = v
                meilleur_sol = nouvelle
                meilleur_mv  = (retirée, ajoutée)

        if meilleur_sol is None:
            break

        # Appliquer le mouvement
        sol, val = meilleur_sol, meilleur_val
        retirée, _ = meilleur_mv

        # Mettre à jour la liste tabou
        liste_tabou[retirée] = it + tenure
        liste_tabou = {k: v for k, v in liste_tabou.items() if v > it}

        historique.append(val)

        if val > best_val:
            best_val, best_sol = val, sol[:]
            sans_amelio = 0
            if verbose:
                print(f"  Iter {it+1:3d} ★ {best_val:.4f}  |tabou|={len(liste_tabou)}")
        else:
            sans_amelio += 1
            if verbose and (it + 1) % 10 == 0:
                print(f"  Iter {it+1:3d}   courant={val:.4f}  meilleur={best_val:.4f}  |tabou|={len(liste_tabou)}")

    if verbose:
        print(f"Résultat final : {best_val:.4f}  ({len(best_sol)} configs)")
    return best_val, best_sol, historique


# ── Comparaison des méthodes ──────────────────────────────────────────────────

def comparer_methodes(instance, nb_runs=3, verbose=True):
    """
    Compare glouton / descente / tabou sur la même instance.
    Effectue nb_runs exécutions pour chaque méthode (résultats aléatoires).
    """
    print("\n" + "=" * 55)
    print("  Comparaison des méthodes")
    print("=" * 55)

    # ── Glouton de référence ──
    configs_ref = generer_configurations(instance, methode="glouton_aleatoire")
    val_glouton = evaluer(instance, configs_ref)
    print(f"\n  Glouton (référence)  : {val_glouton:.4f}  ({len(configs_ref)} configs)")

    # ── Descente ──
    val_descente = 0.0
    for run in range(nb_runs):
        ci = generer_configurations(instance, methode="glouton_aleatoire",
                                    seed=random.randint(0, 9999))
        v, _, _ = descente(instance, configs_initiales=ci,
                           nb_voisins=15, max_iter=80, verbose=False)
        val_descente = max(val_descente, v)
    print(f"  Descente (best/{nb_runs})   : {val_descente:.4f}")

    # ── Tabou ──
    val_tabou = 0.0
    for run in range(nb_runs):
        ci = generer_configurations(instance, methode="glouton_aleatoire",
                                    seed=random.randint(0, 9999))
        v, _, _ = tabou(instance, configs_initiales=ci,
                        nb_voisins=20, max_iter=150, tenure=10, verbose=False)
        val_tabou = max(val_tabou, v)
    print(f"  Tabou   (best/{nb_runs})   : {val_tabou:.4f}")

    print("\n" + "=" * 55)
    if val_tabou > val_glouton:
        gain = (val_tabou - val_glouton) / val_glouton * 100
        print(f"  Gain tabou vs glouton : +{gain:.2f}%")
    return val_glouton, val_descente, val_tabou

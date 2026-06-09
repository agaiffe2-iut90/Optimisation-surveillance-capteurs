"""
solver.py - Écriture du programme linéaire et résolution

Deux modes :
  1. PuLP avec GLPK (glpsol) si disponible
  2. PuLP avec solver par défaut (CBC/HiGHS) en fallback
"""

import os
import pulp


# ── Écriture du fichier .lp (format CPLEX) ──────────────────────────────────

def ecrire_lp(instance, configs, chemin_lp="programme.lp"):
    """
    Génère le fichier .lp correspondant au programme linéaire :

      max  sum_k t_k
      s.c. pour chaque capteur i : sum_{k : i in config_k} t_k <= T_i
           t_k >= 0
    """
    K = len(configs)

    with open(chemin_lp, "w") as f:
        f.write("Maximize\n")
        obj = " + ".join(f"t{k+1}" for k in range(K))
        f.write(f"  obj: {obj}\n\n")

        f.write("Subject To\n")
        for i in range(instance.N):
            configs_avec_i = [k for k, c in enumerate(configs) if i in c]
            if not configs_avec_i:
                continue
            lhs = " + ".join(f"t{k+1}" for k in configs_avec_i)
            f.write(f"  c_s{i+1}: {lhs} <= {instance.T[i]}\n")

        f.write("\nBounds\n")
        for k in range(K):
            f.write(f"  t{k+1} >= 0\n")

        f.write("\nEnd\n")

    return chemin_lp


# ── Résolution via PuLP ──────────────────────────────────────────────────────

def resoudre_pulp(instance, configs, verbose=False):
    """
    Construit et résout le PL avec PuLP.
    Essaie GLPK en priorité, sinon utilise le solver par défaut (CBC/HiGHS).

    Retourne (valeur_objectif, dict{k: t_k}, nom_solver) ou None si échec.
    """
    K = len(configs)

    # Définition du problème
    prob = pulp.LpProblem("surveillance_capteurs", pulp.LpMaximize)

    # Variables de décision : t_k >= 0
    t = [pulp.LpVariable(f"t{k+1}", lowBound=0) for k in range(K)]

    # Fonction objectif : maximiser sum(t_k)
    prob += pulp.lpSum(t), "duree_vie_reseau"

    # Contraintes : pour chaque capteur i, sum des t_k le contenant <= T_i
    for i in range(instance.N):
        configs_avec_i = [k for k, c in enumerate(configs) if i in c]
        if not configs_avec_i:
            continue
        prob += pulp.lpSum(t[k] for k in configs_avec_i) <= instance.T[i], f"capteur_s{i+1}"

    # Choix du solver (msg=0 pour silence, msg=1 si verbose explicite)
    msg = 1 if verbose else 0
    solver = None
    nom_solver = "défaut"

    if pulp.GLPK_CMD().available():
        solver = pulp.GLPK_CMD(msg=msg)
        nom_solver = "GLPK"
    else:
        # Fallback : HiGHS ou CBC selon ce qui est dispo
        for SolverClass, nom in [(pulp.HiGHS_CMD, "HiGHS"), (pulp.PULP_CBC_CMD, "CBC")]:
            try:
                s = SolverClass(msg=0)   # CBC ignore msg via solve(), on force ici
                if s.available():
                    solver = s
                    nom_solver = nom
                    break
            except Exception:
                continue

    # Résolution
    status = prob.solve(solver)

    if pulp.LpStatus[status] != "Optimal":
        print(f"[WARN] Statut : {pulp.LpStatus[status]}")
        return None

    valeur = pulp.value(prob.objective)
    variables = {k: pulp.value(t[k]) or 0.0 for k in range(K)}

    return valeur, variables, nom_solver


# ── Interface principale ─────────────────────────────────────────────────────

def resoudre(instance, configs, dossier_tmp="/tmp", verbose=True):
    """
    Résout le problème d'ordonnancement avec PuLP.
    Génère aussi le fichier .lp pour traçabilité.

    Retourne un dict :
      {
        "duree_vie"  : float,
        "temps"      : {k: float},
        "methode"    : str,
        "configs"    : configs,
      }
    """
    # Génération du fichier .lp (pour traçabilité / utilisation avec glpsol)
    chemin_lp = os.path.join(dossier_tmp, "programme.lp")
    ecrire_lp(instance, configs, chemin_lp)

    result = resoudre_pulp(instance, configs, verbose=verbose)
    if result is None:
        print("[ERREUR] PuLP n'a pas trouvé de solution optimale.")
        return None

    valeur, variables, nom_solver = result
    if verbose:
        print(f"[INFO] Solveur utilisé : {nom_solver}")

    return {
        "duree_vie" : valeur,
        "temps"     : variables,
        "methode"   : nom_solver,
        "configs"   : configs,
    }


def afficher_solution(instance, solution):
    """Affiche la solution de manière lisible."""
    if solution is None:
        print("Pas de solution.")
        return

    configs = solution["configs"]
    temps   = solution["temps"]
    methode = solution["methode"]
    duree   = solution["duree_vie"]

    nb_actives = sum(1 for t in temps.values() if t > 1e-9)
    nb_epuises = 0
    
    for i in range(instance.N):
        configs_avec_i = [k for k, c in enumerate(configs) if i in c]
        energie = sum(temps.get(k, 0.0) for k in configs_avec_i)
        if (instance.T[i] - energie) < 1e-6:
            nb_epuises += 1

    print("\n" + "="*55)
    print("--- RÉSUMÉ ---")
    print(f"Configurations générées (total) : {len(configs)}")
    print(f"Configurations actives (>0)     : {nb_actives}")
    print(f"Durée de vie optimale           : {duree:.4f} u.t.")
    print(f"Capteurs épuisés                : {nb_epuises}/{instance.N}")
    print("="*55 + "\n")

    # --- AFFICHAGE DÉTAILLÉ CLASSIQUE ---
    print(f"=== Détail de la Solution (solveur : {methode.upper()}) ===")
    
    print("Activité des configurations (seules les actives sont affichées) :")
    for k, c in enumerate(configs):
        t = temps.get(k, 0.0)
        if t > 1e-9:
            capteurs_str = "{" + ", ".join(f"s{i+1}" for i in sorted(c)) + "}"
            print(f"  u{k+1} = {capteurs_str:<25}  activée pendant  t{k+1} = {t:.4f}")

    print("\nÉnergie consommée par capteur :")
    for i in range(instance.N):
        configs_avec_i = [k for k, c in enumerate(configs) if i in c]
        energie = sum(temps.get(k, 0.0) for k in configs_avec_i)
        reste   = instance.T[i] - energie
        statut  = "⚡ épuisé" if reste < 1e-6 else f"reste {reste:.4f}"
        print(f"  s{i+1} : actif {energie:.4f} / {instance.T[i]}  ({statut})")
    print()
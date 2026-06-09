import matplotlib.pyplot as plt

# 1. Les données du graphique moyen_test_2
x_configs = [5, 10, 20, 50, 100]
y_aleatoire = [65, 83, 87, 104, 104]  # Les valeurs de la courbe bleue
y_trie = [15, 15, 15, 15, 15]         # Les valeurs de la courbe orange

# 2. Configuration du graphique (Style classique fond blanc)
plt.style.use('default') # Force le fond blanc standard de matplotlib
plt.figure(figsize=(10, 6), facecolor='white')

# 3. Tracé des courbes
plt.plot(x_configs, y_aleatoire, marker='o', linewidth=2, markersize=8, 
         label='Glouton aléatoire', color='#4c72b0')
plt.plot(x_configs, y_trie, marker='o', linewidth=2, markersize=8, 
         label='Glouton trié', color='#dd8452')

# 4. Paramétrage des axes (Échelle logarithmique comme sur ta capture)
plt.xscale('log')
plt.xticks(x_configs, x_configs) # Pour afficher exactement 5, 10, 20, 50, 100

# 5. Titres et légendes
plt.title('Influence du nombre et type de configurations (moyen_test_2)', fontsize=14, fontweight='bold')
plt.xlabel('Nombre de configurations demandées', fontsize=12)
plt.ylabel('Durée de vie optimale (unités de temps)', fontsize=12)

# Ajout des petites valeurs de fin de courbe
plt.text(100, 106, '104.0', color='#4c72b0', fontweight='bold', ha='center')
plt.text(100, 12, '15.0', color='#dd8452', fontweight='bold', ha='center')

# Grille discrète et légende
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='lower right', fontsize=11)

# 6. Sauvegarde de l'image pour le rapport !
plt.savefig('moyen_test_2_fond_blanc.png', dpi=300, bbox_inches='tight')
print("✅ Graphique généré avec succès : moyen_test_2_fond_blanc.png")
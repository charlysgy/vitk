# Guide de Vérification d'Alignement

Ce guide explique comment vérifier si vos volumes médicaux sont correctement alignés (recalés) en utilisant les outils développés.

## Méthodes de Vérification

### 1. Analyse Automatique Complète

Exécutez le script principal qui inclut maintenant une analyse d'alignement automatique :

```bash
python main.py
```

Le script affichera automatiquement :
- ✅ Vérification des dimensions
- 📊 Analyse des centres de masse
- 🔗 Corrélations spatiales par tranches
- 📏 Détection de décalages
- 📋 Évaluation globale et recommandations

### 2. Vérification Rapide Dédiée

Pour une analyse rapide sans interface graphique :

```bash
python check_alignment.py
```

### 3. Vérification Interactive

Dans l'interface graphique (`python main.py`), utilisez les nouvelles commandes :

| Touche | Action |
|--------|--------|
| `a` | Analyser l'alignement à la position actuelle |
| `d` | Activer/désactiver le mode différence |
| `s` | Sauvegarder un rapport d'alignement |

## Critères d'Alignement

### Volumes Bien Alignés ✅
- **Corrélations élevées** : > 0.7 dans toutes les orientations
- **Décalages faibles** : < 2 voxels
- **Centres de masse proches** : < 5 voxels de distance

### Volumes Mal Alignés ❌
- **Corrélations faibles** : < 0.7 dans une ou plusieurs orientations
- **Décalages importants** : ≥ 2 voxels
- **Centres de masse éloignés** : ≥ 5 voxels de distance

## Interprétation des Résultats

### Analyse des Corrélations
```
Corrélation spatiale par tranches:
   Axiale   - Moyenne: 0.85, Min: 0.72  ✅ Bon alignement
   Coronale - Moyenne: 0.45, Min: 0.12  ❌ Mauvais alignement
   Sagittale- Moyenne: 0.78, Min: 0.65  ✅ Bon alignement
```

### Détection de Décalages
```
Décalage estimé (X, Y, Z): (1.2, 0.8, 2.1) voxels
```
- Si tous les décalages < 2 voxels → Bon alignement
- Si un décalage ≥ 2 voxels → Recalage nécessaire

### Centres de Masse
```
Centre de masse Volume 1: (64.2, 128.5, 96.7)
Centre de masse Volume 2: (66.1, 130.2, 94.3)
Distance entre centres: 3.1 voxels
```
- Distance < 5 voxels → Bon alignement global
- Distance ≥ 5 voxels → Décalage important

## Vérification Visuelle

### Dans l'Interface Interactive

1. **Navigation synchronisée** : Utilisez les flèches pour naviguer
   - Les deux volumes doivent montrer les mêmes structures anatomiques
   - Vérifiez dans les 3 orientations (axiale, coronale, sagittale)

2. **Mode différence** (touche `d`) :
   - Active l'affichage des différences absolues
   - Les zones bien alignées apparaissent sombres
   - Les zones mal alignées apparaissent claires

3. **Analyse position par position** (touche `a`) :
   - Corrélations en temps réel à la position actuelle
   - Intensités moyennes pour détecter des artefacts

### Points de Vérification Anatomiques

- **Contours externes** du cerveau/organe
- **Structures vasculaires** (vaisseaux sanguins)
- **Interfaces tissu-air** (sinus, ventricules)
- **Structures symétriques** (comparaison gauche/droite)
- **Repères anatomiques** spécifiques à votre modalité

## Actions Correctives

### Si les volumes sont mal alignés :

1. **Décalage simple** : Translation pure
   ```
   Recommandation: Appliquer une correction de translation
   Décalage détecté: (2.5, -1.8, 0.3) voxels
   ```

2. **Problème de dimensions** :
   ```
   Recommandation: Effectuer un recalage spatial pour harmoniser les dimensions
   ```

3. **Désalignement complexe** :
   ```
   Recommandation: Envisager un recalage rigide ou non-rigide
   ```

## Génération de Rapports

### Rapport Automatique
Le script `main.py` génère automatiquement un rapport dans la console.

### Rapport Sauvegardé
Appuyez sur `s` dans l'interface interactive pour sauvegarder un rapport dans `alignment_report.txt`.

## Exemples de Cas Typiques

### Cas 1: Volumes Parfaitement Alignés
```
✅ RÉSULTAT: Les volumes sont BIEN ALIGNÉS
   Corrélations moyennes: 0.89, 0.91, 0.87
   Décalage max: 0.8 voxels
   Distance centres: 1.2 voxels
```

### Cas 2: Décalage de Translation
```
❌ RÉSULTAT: Les volumes sont MAL ALIGNÉS
   Décalage important détecté: (3.2, -2.1, 1.8)
   → Appliquer une correction de translation
```

### Cas 3: Problème d'Acquisition
```
❌ RÉSULTAT: Les volumes sont MAL ALIGNÉS
   Corrélations faibles dans les plans: coronal, sagittal
   → Vérifier les paramètres d'acquisition (résolution, FOV)
```

## Conseils Pratiques

1. **Toujours vérifier** l'alignement avant de comparer des volumes
2. **Utiliser les 3 orientations** pour une vérification complète
3. **Se concentrer sur les structures stables** (os, contours)
4. **Documenter** les résultats de vérification
5. **Répéter** la vérification après tout recalage

## Limitations

- L'analyse automatique détecte les problèmes majeurs
- Les désalignements subtils nécessitent une vérification visuelle
- Les résultats dépendent de la qualité des images d'origine
- Certains artefacts peuvent masquer des problèmes d'alignement

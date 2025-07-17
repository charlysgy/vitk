# Architecture du Projet VTK-ITK

## Structure des Modules

Ce projet a été restructuré en plusieurs modules spécialisés pour une meilleure organisation et maintenabilité.

### 📁 Structure du Projet

```
vitk/
├── __init__.py          # Package principal avec imports
├── main.py              # Point d'entrée principal
├── converters.py        # Conversions ITK ↔ NumPy ↔ VTK
├── visualization.py     # Interface de visualisation interactive
├── utils.py             # Utilitaires et fonctions de debug
├── config.py            # Configuration et constantes
├── examples.py          # Exemples d'utilisation avancée
└── Data/                # Dossier des données
    ├── case6_gre1.nrrd
    ├── case6_gre2.nrrd
    └── ...
```

## 📋 Description des Modules

### 🔄 `converters.py`
**Fonctions de conversion entre formats**
- `itk_to_numpy()` - Conversion ITK → NumPy
- `numpy_to_vtk_volume()` - Conversion NumPy → VTK (avec transposition)
- `simple_numpy_to_vtk()` - Conversion NumPy → VTK (simplifiée)
- `load_medical_image()` - Chargement d'images médicales

### 🖥️ `visualization.py`
**Interface de visualisation interactive**
- `InteractiveImageViewer` - Classe principale pour la visualisation
- `show_interactive_comparison()` - Fonction de convenance
- Gestion des événements clavier et souris
- Affichage multi-vues (6 vues : 3 orientations × 2 volumes)

### 🛠️ `utils.py`
**Utilitaires et fonctions d'aide**
- `debug_array_info()` - Informations détaillées sur les arrays
- `validate_volume_shape()` - Validation des dimensions
- `calculate_intensity_stats()` - Calcul des statistiques d'intensité
- `compare_volumes()` - Comparaison de deux volumes
- `print_intensity_stats()` - Affichage formaté des statistiques

### ⚙️ `config.py`
**Configuration et constantes**
- Paramètres de visualisation (taille fenêtre, couleurs)
- Configuration des viewports et orientations
- Messages d'aide et constantes

### 📖 `examples.py`
**Exemples d'utilisation avancée**
- Comparaison de base
- Analyse personnalisée des volumes
- Analyse coupe par coupe
- Comparaison des méthodes de conversion
- Traitement par lot

## 🚀 Utilisation

### Utilisation Simple
```python
# Import du package principal
from vitk import show_interactive_comparison, load_medical_image

# Chargement et affichage
_, array1 = load_medical_image("Data/case6_gre1.nrrd")
_, array2 = load_medical_image("Data/case6_gre2.nrrd") 
show_interactive_comparison(array1, array2)
```

### Utilisation Avancée
```python
from vitk import InteractiveImageViewer, calculate_intensity_stats, debug_array_info

# Analyse détaillée
stats = calculate_intensity_stats(array1, array2)
debug_array_info(array1, "Volume 1")

# Visualisation personnalisée
viewer = InteractiveImageViewer(array1, array2)
viewer.show()
```

### Lancement du Script Principal
```bash
# Utiliser le nouveau main.py
python main_new.py

# Ou les exemples
python examples.py
```

## 🎯 Avantages de cette Architecture

### ✅ **Séparation des Responsabilités**
- Chaque module a une fonction spécifique
- Code plus lisible et maintenable
- Tests unitaires facilités

### ✅ **Réutilisabilité**
- Modules indépendants réutilisables
- Imports sélectifs possibles
- Extension facile

### ✅ **Maintenabilité**
- Modifications localisées
- Débogage simplifié
- Documentation par module

### ✅ **Extensibilité**
- Ajout facile de nouvelles fonctionnalités
- Interface stable
- Configuration centralisée

## 🔧 Migration depuis l'Ancien Code

### Étapes de Migration
1. **Remplacer** `main.py` par `main_new.py`
2. **Utiliser** les imports modulaires :
   ```python
   # Ancien
   from main import debug_array_info, InteractiveImageViewer
   
   # Nouveau
   from utils import debug_array_info
   from visualization import InteractiveImageViewer
   ```
3. **Adapter** le code existant selon les nouveaux modules

### Compatibilité
- L'API principale reste identique
- Les fonctions ont les mêmes signatures
- Seuls les imports changent

## 📚 Documentation des APIs

### Converters
```python
def load_medical_image(file_path, pixel_type=itk.F):
    """Charge une image médicale avec ITK"""
    
def simple_numpy_to_vtk(numpy_array):
    """Conversion NumPy → VTK simplifiée"""
```

### Visualization
```python
class InteractiveImageViewer:
    def __init__(self, volume1, volume2):
        """Initialise avec deux volumes à comparer"""
    
    def show(self):
        """Lance l'interface interactive"""
```

### Utils
```python
def debug_array_info(array, name="Array"):
    """Affiche les informations de débogage"""
    
def calculate_intensity_stats(volume1, volume2=None):
    """Calcule les statistiques d'intensité"""
```

## 🏗️ Futures Extensions Possibles

1. **Plugin System** - Système de plugins pour nouvelles fonctionnalités
2. **Export Module** - Export vers différents formats
3. **Registration Module** - Algorithmes de recalage d'images
4. **Filtering Module** - Filtres et traitements d'images
5. **GUI Module** - Interface graphique Qt/Tkinter
6. **CLI Module** - Interface en ligne de commande avancée

Cette architecture modulaire permet une évolution progressive du projet tout en maintenant la simplicité d'utilisation pour les cas basiques.

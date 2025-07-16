# Projet VTK-ITK - Architecture Modulaire

🏥 **Outil de comparaison interactive de volumes médicaux** utilisant ITK et VTK avec une architecture modulaire propre.

## 🚀 Démarrage Rapide

```bash
# Configuration automatique
make setup

# Ou manuellement
python3 setup.py

# Lancement de l'application
make run
# ou
python3 main.py
```

## 📁 Architecture

```
vitk/
├── 🔧 main.py              # Point d'entrée principal
├── 🔄 converters.py        # Conversions ITK ↔ NumPy ↔ VTK  
├── 🖥️  visualization.py    # Interface interactive VTK
├── 🛠️  utils.py            # Utilitaires et débogage
├── ⚙️  config.py           # Configuration centralisée
├── 📖 examples.py          # Exemples d'utilisation avancée
├── 🧪 test_architecture.py # Tests unitaires
├── 🔧 setup.py             # Script de configuration
├── 📝 Makefile             # Automatisation des tâches
├── 📚 ARCHITECTURE.md      # Documentation détaillée
└── 📄 Data/                # Données médicales
    ├── case6_gre1.nrrd
    └── case6_gre2.nrrd
```


### ✅ **Séparation des Responsabilités**
- **converters.py** : Gestion des conversions de formats
- **visualization.py** : Interface utilisateur et rendu VTK
- **utils.py** : Fonctions utilitaires réutilisables
- **config.py** : Paramètres centralisés

### ✅ **Réutilisabilité**
```python
# Import sélectif selon les besoins
from converters import load_medical_image
from utils import debug_array_info
from visualization import show_interactive_comparison
```

## 🎯 Utilisation

### Interface Simple
```python
from vitk import show_interactive_comparison, load_medical_image

# Chargement et comparaison en une ligne
_, vol1 = load_medical_image("Data/case6_gre1.nrrd")
_, vol2 = load_medical_image("Data/case6_gre2.nrrd")
show_interactive_comparison(vol1, vol2)
```

### Interface Avancée
```python
from vitk import InteractiveImageViewer, calculate_intensity_stats

# Analyse détaillée
stats = calculate_intensity_stats(vol1, vol2)
viewer = InteractiveImageViewer(vol1, vol2)
viewer.show()
```

### Traitement par Lot
```python
from vitk import debug_array_info, validate_volume_shape

# Analyse de plusieurs volumes
for file_path in image_files:
    _, volume = load_medical_image(file_path)
    validate_volume_shape(volume)
    debug_array_info(volume, file_path.name)
```

## 🛠️ Commandes Make

```bash
make help       # Aide et liste des commandes
make setup      # Configuration complète du projet
make run        # Lance l'application principale
make test       # Tests unitaires
make examples   # Lance les exemples interactifs
make check-deps # Vérifie les dépendances
make check-data # Vérifie les fichiers de données
make clean      # Nettoyage des fichiers temporaires
make lint       # Vérification qualité du code
make info       # Informations sur le projet
```

## 🎮 Contrôles de Navigation

Une fois l'interface lancée :
- **↑/↓** : Navigation axiale
- **←/→** : Navigation sagittale  
- **Page Up/Down** : Navigation coronale
- **Q ou Escape** : Quitter
- **Clic souris** : Zoom et rotation

## 📦 Dépendances

- **Python 3.7+**
- **NumPy** : Manipulation d'arrays
- **VTK** : Visualisation et rendu
- **ITK** : Traitement d'images médicales

Installation automatique :
```bash
make install
# ou
pip install numpy vtk itk
```

## 🧪 Tests et Validation

```bash
# Tests complets
make test

# Vérifications spécifiques
make check-deps  # Dépendances
make check-data  # Fichiers requis
make lint       # Qualité du code
```

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** : Documentation détaillée de l'architecture
- **[examples.py](examples.py)** : Exemples d'utilisation avancée
- **Docstrings** : Documentation intégrée dans chaque module

## 🔄 Migration depuis l'Ancien Code

L'ancien `main.py` monolithique est sauvegardé dans `main_old.py`. 

**Avant** (ancien code) :
```python
# Tout dans un seul fichier de 300+ lignes
from main import debug_array_info, InteractiveImageViewer
```

**Après** (nouveau code) :
```python
# Imports modulaires et spécialisés
from utils import debug_array_info
from visualization import InteractiveImageViewer
```

## 🎯 Exemples d'Utilisation

### Comparaison Basique
```bash
python3 main.py
```

### Exemples Avancés
```bash
python3 examples.py
# Puis choisir parmi :
# 1. Comparaison de base
# 2. Analyse personnalisée  
# 3. Analyse par coupe
# 4. Comparaison des conversions
# 5. Traitement par lot
```

### Script Simple Personnalisé
```bash
python3 example_simple.py  # Généré par setup.py
```

## 🔧 Développement

### Ajout d'un Nouveau Module
1. Créer le fichier `.py` avec documentation
2. Ajouter les imports dans `__init__.py`
3. Créer les tests correspondants
4. Mettre à jour la documentation

### Structure d'un Module Type
```python
"""
Module Description
==================
Description du module et de ses fonctionnalités.
"""

import dependencies

def public_function():
    """Documentation de la fonction publique"""
    pass

class PublicClass:
    """Documentation de la classe publique"""
    
    def __init__(self):
        pass
```

## 📈 Roadmap Futures Extensions

- **🔌 Plugin System** : Architecture de plugins
- **🗂️ Export Module** : Export multi-formats
- **📐 Registration Module** : Recalage d'images
- **🎨 Filtering Module** : Filtres avancés
- **🖥️ GUI Module** : Interface Qt/Tkinter
- **⌨️ CLI Module** : Interface ligne de commande

## 🤝 Contribution

1. Fork du projet
2. Création d'une branche feature
3. Tests avec `make test`
4. Pull request avec description

---

**🎉 Cette architecture modulaire transforme un script monolithique de 300+ lignes en modules spécialisés, maintenables et réutilisables !**

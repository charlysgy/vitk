"""
Configuration Module
===================

Ce module contient les constantes et paramètres de configuration
pour l'application de comparaison d'images médicales.
"""

import itk
from pathlib import Path

# Chemins de fichiers
DATA_DIR = Path("./Data")
DEFAULT_IMAGE1 = "case6_gre1.nrrd"
DEFAULT_IMAGE2 = "case6_gre2.nrrd"

# Paramètres ITK
DEFAULT_PIXEL_TYPE = itk.F

# Paramètres VTK
DEFAULT_SPACING = (1.0, 1.0, 1.0)
DEFAULT_ORIGIN = (0.0, 0.0, 0.0)

# Paramètres de visualisation
WINDOW_SIZE = (1800, 900)
WINDOW_TITLE = "Navigation Interactive - Avant/Après"
BACKGROUND_COLOR = (0.1, 0.1, 0.1)
TEXT_COLOR = (1.0, 1.0, 1.0)
FONT_SIZE = 14

# Positions des viewports (2x3 grid)
VIEWPORTS = [
    [0.0, 0.5, 0.33, 1.0],   # Volume1 - Axial
    [0.33, 0.5, 0.66, 1.0],  # Volume1 - Coronal  
    [0.66, 0.5, 1.0, 1.0],   # Volume1 - Sagittal
    [0.0, 0.0, 0.33, 0.5],   # Volume2 - Axial
    [0.33, 0.0, 0.66, 0.5],  # Volume2 - Coronal
    [0.66, 0.0, 1.0, 0.5],   # Volume2 - Sagittal
]

VIEWPORT_TITLES = [
    "Volume 1 - Axial", "Volume 1 - Coronal", "Volume 1 - Sagittal",
    "Volume 2 - Axial", "Volume 2 - Coronal", "Volume 2 - Sagittal"
]

# Orientations pour le reslicing
ORIENTATIONS = {
    'axial': {
        'direction_cosines': (1,0,0, 0,1,0, 0,0,1),
        'name': 'Axial'
    },
    'coronal': {
        'direction_cosines': (1,0,0, 0,0,-1, 0,1,0),
        'name': 'Coronal'
    },
    'sagittal': {
        'direction_cosines': (0,1,0, 0,0,-1, 1,0,0),
        'name': 'Sagittal'
    }
}

# Messages d'aide
HELP_MESSAGES = {
    'controls': """
=== CONTRÔLES ===
  ↑/↓ : Navigation axiale
  ←/→ : Navigation sagittale
  Page Up/Down : Navigation coronale
  'q' ou 'Escape' : Quitter
  Fermeture fenêtre : Alt+F4 ou bouton X
""",
    'startup': """
=== Medical Image Comparison Tool ===
Outil de comparaison interactive de volumes médicaux
utilisant ITK et VTK.
"""
}

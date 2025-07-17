"""
VTK-ITK Integration Package
===========================

Un package pour l'intégration et la visualisation d'images médicales
utilisant ITK et VTK.

Modules:
    - converters: Conversions entre formats ITK, NumPy et VTK
    - visualization: Visualisation interactive des volumes
    - utils: Utilitaires et fonctions de débogage
"""

__version__ = "1.0.0"
__author__ = "Your Name"

# Imports principaux pour faciliter l'utilisation
# Les imports sont conditionnels pour éviter les erreurs si les dépendances ne sont pas installées
try:
    from .converters import itk_to_numpy, numpy_to_vtk_volume, simple_numpy_to_vtk
    from .visualization import InteractiveImageViewer, show_interactive_comparison
    from .utils import debug_array_info
    
    __all__ = [
        "itk_to_numpy",
        "numpy_to_vtk_volume", 
        "simple_numpy_to_vtk",
        "InteractiveImageViewer",
        "show_interactive_comparison",
        "debug_array_info"
    ]
except ImportError as e:
    print(f"Avertissement: Certains modules ne peuvent pas être importés: {e}")
    print("Assurez-vous que numpy, vtk et itk sont installés.")
    __all__ = []

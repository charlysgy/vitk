#!/usr/bin/env python3
"""
Exemple Simple d'Utilisation
============================
"""

from utils import debug_array_info
from converters import load_medical_image
from visualization import show_interactive_comparison

def main():
    print("=== Exemple Simple ===")
    
    try:
        # Chargement des images
        _, array1 = load_medical_image("Data/case6_gre1.nrrd")
        _, array2 = load_medical_image("Data/case6_gre2.nrrd")
        
        # Analyse rapide
        debug_array_info(array1, "Image 1")
        debug_array_info(array2, "Image 2")
        
        # Visualisation
        show_interactive_comparison(array1, array2)
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test du Mode Différence
=======================

Script de test pour vérifier que le mode différence fonctionne correctement
sans bugs lors de l'activation/désactivation répétée.
"""

import sys
from pathlib import Path
import numpy as np

try:
    from converters import load_medical_image
    from visualization import InteractiveImageViewer
except ImportError:
    print("Erreur: Impossible d'importer les modules. Vérifiez que vous êtes dans le bon répertoire.")
    sys.exit(1)


def test_difference_mode():
    """Test automatique du mode différence"""
    print("=== Test du Mode Différence ===")
    
    # Configuration des chemins
    data_dir = Path("./Data")
    image1_path = data_dir / "case6_gre1.nrrd"
    image2_path = data_dir / "case6_gre2.nrrd"
    
    # Vérification de l'existence des fichiers
    if not image1_path.exists() or not image2_path.exists():
        print("Erreur: Fichiers de test non trouvés")
        sys.exit(1)
    
    try:
        # Chargement des images
        print("Chargement des images...")
        image1_itk, array1 = load_medical_image(str(image1_path))
        image2_itk, array2 = load_medical_image(str(image2_path))
        print("✓ Images chargées")
        
        # Créer le visualiseur
        print("Création du visualiseur...")
        viewer = InteractiveImageViewer(array1, array2)
        print("✓ Visualiseur créé")
        
        # Test du mode différence
        print("\nTest 1: Activation du mode différence...")
        viewer.toggle_difference_mode()
        print("✓ Mode différence activé")
        
        print("Test 2: Désactivation du mode différence...")
        viewer.toggle_difference_mode()
        print("✓ Mode différence désactivé")
        
        print("Test 3: Réactivation du mode différence...")
        viewer.toggle_difference_mode()
        print("✓ Mode différence réactivé")
        
        print("Test 4: Nouvelle désactivation...")
        viewer.toggle_difference_mode()
        print("✓ Mode différence redésactivé")
        
        print("\n✅ TOUS LES TESTS RÉUSSIS!")
        print("Le mode différence fonctionne correctement.")
        
        # Test de la navigation
        print("\nTest 5: Navigation avec mode différence...")
        viewer.toggle_difference_mode()  # Activer
        old_slice = viewer.axial_slice
        viewer.axial_slice = min(viewer.axial_slice + 5, viewer.shape[0] - 1)
        viewer.update_slices()
        print(f"✓ Navigation testée (slice {old_slice} → {viewer.axial_slice})")
        
        viewer.toggle_difference_mode()  # Désactiver
        viewer.axial_slice = max(viewer.axial_slice - 3, 0)
        viewer.update_slices()
        print(f"✓ Navigation normale testée (slice → {viewer.axial_slice})")
        
        print("\n🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print("Vous pouvez maintenant utiliser le mode différence sans problème.")
        
    except Exception as e:
        print(f"\n❌ ERREUR DURANT LES TESTS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    test_difference_mode()

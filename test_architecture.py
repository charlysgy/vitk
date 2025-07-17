"""
Tests Unitaires pour le Projet VTK-ITK
======================================

Ce module contient les tests unitaires pour valider le bon fonctionnement
des différents modules du projet.
"""

import unittest
import numpy as np
import tempfile
import os
from pathlib import Path

# Tests avec des données factices pour éviter les dépendances
try:
    from utils import debug_array_info, validate_volume_shape, calculate_intensity_stats
    from converters import simple_numpy_to_vtk
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Modules non disponibles pour les tests: {e}")
    MODULES_AVAILABLE = False


class TestUtils(unittest.TestCase):
    """Tests pour le module utils"""
    
    def setUp(self):
        """Préparation des données de test"""
        if not MODULES_AVAILABLE:
            self.skipTest("Modules non disponibles")
            
        # Création de volumes de test
        self.volume1 = np.random.rand(10, 20, 30).astype(np.float32)
        self.volume2 = np.random.rand(10, 20, 30).astype(np.float32)
        self.volume_invalid = np.random.rand(10, 20)  # 2D au lieu de 3D
    
    def test_validate_volume_shape_valid(self):
        """Test de validation avec un volume valide"""
        result = validate_volume_shape(self.volume1, expected_dims=3)
        self.assertTrue(result)
    
    def test_validate_volume_shape_invalid_dims(self):
        """Test de validation avec un volume de mauvaise dimension"""
        with self.assertRaises(ValueError):
            validate_volume_shape(self.volume_invalid, expected_dims=3)
    
    def test_validate_volume_shape_non_numpy(self):
        """Test de validation avec un objet qui n'est pas un array NumPy"""
        with self.assertRaises(ValueError):
            validate_volume_shape([1, 2, 3], expected_dims=3)
    
    def test_calculate_intensity_stats_single_volume(self):
        """Test de calcul de statistiques pour un volume"""
        stats = calculate_intensity_stats(self.volume1)
        
        self.assertIn('volume1', stats)
        self.assertIn('min', stats['volume1'])
        self.assertIn('max', stats['volume1'])
        self.assertIn('mean', stats['volume1'])
        self.assertIn('std', stats['volume1'])
    
    def test_calculate_intensity_stats_two_volumes(self):
        """Test de calcul de statistiques pour deux volumes"""
        stats = calculate_intensity_stats(self.volume1, self.volume2)
        
        self.assertIn('volume1', stats)
        self.assertIn('volume2', stats)
        self.assertIn('combined', stats)
        self.assertIn('display', stats)
        
        # Vérification des paramètres d'affichage
        self.assertIn('window', stats['display'])
        self.assertIn('level', stats['display'])


class TestConverters(unittest.TestCase):
    """Tests pour le module converters"""
    
    def setUp(self):
        """Préparation des données de test"""
        if not MODULES_AVAILABLE:
            self.skipTest("Modules non disponibles")
            
        self.test_volume = np.random.rand(5, 10, 15).astype(np.float32)
    
    def test_simple_numpy_to_vtk_basic(self):
        """Test de base de la conversion NumPy vers VTK"""
        try:
            vtk_volume = simple_numpy_to_vtk(self.test_volume)
            
            # Vérification que l'objet VTK est créé
            self.assertIsNotNone(vtk_volume)
            
            # Vérification des dimensions (ordre ITK: Z,Y,X)
            expected_dims = (self.test_volume.shape[2], 
                           self.test_volume.shape[1], 
                           self.test_volume.shape[0])
            actual_dims = vtk_volume.GetDimensions()
            self.assertEqual(actual_dims, expected_dims)
            
        except ImportError:
            self.skipTest("VTK non disponible")


class TestIntegration(unittest.TestCase):
    """Tests d'intégration pour vérifier la cohérence entre modules"""
    
    def setUp(self):
        """Préparation des données de test"""
        if not MODULES_AVAILABLE:
            self.skipTest("Modules non disponibles")
            
        # Volumes de test avec des caractéristiques connues
        self.volume_zeros = np.zeros((5, 5, 5), dtype=np.float32)
        self.volume_ones = np.ones((5, 5, 5), dtype=np.float32)
        self.volume_gradient = np.arange(125).reshape(5, 5, 5).astype(np.float32)
    
    def test_workflow_complete(self):
        """Test du workflow complet : validation → stats → conversion"""
        # 1. Validation
        validate_volume_shape(self.volume_gradient)
        
        # 2. Calcul des statistiques
        stats = calculate_intensity_stats(self.volume_gradient, self.volume_ones)
        
        # Vérifications des stats
        self.assertEqual(stats['volume1']['min'], 0.0)
        self.assertEqual(stats['volume1']['max'], 124.0)
        self.assertEqual(stats['volume2']['min'], 1.0)
        self.assertEqual(stats['volume2']['max'], 1.0)
        
        # 3. Conversion VTK (si disponible)
        try:
            vtk_vol1 = simple_numpy_to_vtk(self.volume_gradient)
            vtk_vol2 = simple_numpy_to_vtk(self.volume_ones)
            
            self.assertIsNotNone(vtk_vol1)
            self.assertIsNotNone(vtk_vol2)
            
        except ImportError:
            # VTK non disponible, on skip cette partie
            pass
    
    def test_stats_consistency(self):
        """Test de cohérence des statistiques"""
        # Volume avec des valeurs connues
        test_vol = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]], dtype=np.float32)
        
        stats = calculate_intensity_stats(test_vol)
        
        # Vérifications
        self.assertEqual(stats['volume1']['min'], 1.0)
        self.assertEqual(stats['volume1']['max'], 8.0)
        self.assertAlmostEqual(stats['volume1']['mean'], 4.5, places=1)


class TestArchitecture(unittest.TestCase):
    """Tests pour vérifier l'architecture modulaire"""
    
    def test_module_imports(self):
        """Test que tous les modules peuvent être importés séparément"""
        import_tests = [
            ('utils', ['debug_array_info', 'validate_volume_shape']),
            ('config', ['WINDOW_SIZE', 'VIEWPORTS']),
        ]
        
        for module_name, expected_attrs in import_tests:
            try:
                module = __import__(module_name)
                for attr in expected_attrs:
                    self.assertTrue(hasattr(module, attr), 
                                  f"Module {module_name} should have {attr}")
            except ImportError:
                # Module non disponible, on skip
                continue
    
    def test_package_structure(self):
        """Test de la structure du package"""
        expected_files = [
            '__init__.py',
            'utils.py',
            'config.py',
            'ARCHITECTURE.md'
        ]
        
        current_dir = Path('.')
        for filename in expected_files:
            file_path = current_dir / filename
            if file_path.exists():
                self.assertTrue(file_path.is_file(), 
                              f"{filename} should be a file")


def create_test_suite():
    """Crée une suite de tests personnalisée"""
    suite = unittest.TestSuite()
    
    # Ajout des tests en fonction de la disponibilité des modules
    if MODULES_AVAILABLE:
        suite.addTest(unittest.makeSuite(TestUtils))
        suite.addTest(unittest.makeSuite(TestConverters))
        suite.addTest(unittest.makeSuite(TestIntegration))
    
    suite.addTest(unittest.makeSuite(TestArchitecture))
    
    return suite


def run_tests():
    """Lance les tests avec rapport détaillé"""
    print("=== Tests Unitaires VTK-ITK ===")
    print(f"Modules disponibles: {MODULES_AVAILABLE}")
    
    # Création du runner avec verbosité
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Lancement des tests
    suite = create_test_suite()
    result = runner.run(suite)
    
    # Rapport final
    print(f"\n=== Résultats ===")
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    print(f"Succès: {result.wasSuccessful()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

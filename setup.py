#!/usr/bin/env python3
"""
Setup Script pour le Projet VTK-ITK
===================================

Ce script facilite l'installation et la configuration du projet.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7+ requis")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} détecté")
    return True


def check_dependencies():
    """Vérifie les dépendances disponibles"""
    dependencies = {
        'numpy': 'numpy',
        'vtk': 'vtk',
        'itk': 'itk'
    }
    
    available = {}
    missing = []
    
    for name, import_name in dependencies.items():
        try:
            __import__(import_name)
            available[name] = True
            print(f"✓ {name} disponible")
        except ImportError:
            available[name] = False
            missing.append(name)
            print(f"❌ {name} manquant")
    
    return available, missing


def install_dependencies(missing_deps):
    """Installe les dépendances manquantes"""
    if not missing_deps:
        print("✓ Toutes les dépendances sont installées")
        return True
    
    print(f"\n📦 Installation des dépendances manquantes: {', '.join(missing_deps)}")
    
    # Commandes d'installation
    install_commands = {
        'numpy': 'pip install numpy',
        'vtk': 'pip install vtk',
        'itk': 'pip install itk'
    }
    
    for dep in missing_deps:
        if dep in install_commands:
            print(f"Installation de {dep}...")
            try:
                result = subprocess.run(
                    install_commands[dep].split(),
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"✓ {dep} installé avec succès")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur lors de l'installation de {dep}: {e}")
                return False
        else:
            print(f"❌ Commande d'installation inconnue pour {dep}")
            return False
    
    return True


def check_data_files():
    """Vérifie la présence des fichiers de données"""
    data_dir = Path("Data")
    required_files = ["case6_gre1.nrrd", "case6_gre2.nrrd"]
    
    if not data_dir.exists():
        print(f"❌ Dossier {data_dir} non trouvé")
        return False
    
    missing_files = []
    for filename in required_files:
        file_path = data_dir / filename
        if file_path.exists():
            print(f"✓ {filename} trouvé")
        else:
            print(f"❌ {filename} manquant")
            missing_files.append(filename)
    
    if missing_files:
        print(f"\n⚠️  Fichiers manquants dans {data_dir}:")
        for filename in missing_files:
            print(f"   - {filename}")
        print("   Veuillez placer ces fichiers dans le dossier Data/")
        return False
    
    return True


def check_module_structure():
    """Vérifie la structure des modules"""
    required_modules = [
        "__init__.py",
        "converters.py", 
        "visualization.py",
        "utils.py",
        "config.py",
        "main.py"
    ]
    
    missing_modules = []
    for module in required_modules:
        if Path(module).exists():
            print(f"✓ {module}")
        else:
            print(f"❌ {module} manquant")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  Modules manquants: {', '.join(missing_modules)}")
        return False
    
    return True


def run_tests():
    """Lance les tests pour vérifier l'installation"""
    print("\n🧪 Lancement des tests...")
    
    try:
        result = subprocess.run(
            [sys.executable, "test_architecture.py"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✓ Tests réussis")
            return True
        else:
            print("❌ Certains tests ont échoué")
            print(result.stdout)
            if result.stderr:
                print("Erreurs:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Tests interrompus (timeout)")
        return False
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False


def create_example_script():
    """Crée un script d'exemple simple"""
    example_content = '''#!/usr/bin/env python3
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
'''
    
    with open("example_simple.py", "w") as f:
        f.write(example_content)
    
    print("✓ Script d'exemple créé: example_simple.py")


def main():
    """Fonction principale de setup"""
    print("=" * 50)
    print("🔧 SETUP PROJET VTK-ITK")
    print("=" * 50)
    
    # Vérifications préliminaires
    print("\n📋 Vérifications préliminaires...")
    
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Vérification des dépendances...")
    available, missing = check_dependencies()
    
    # Installation automatique optionnelle
    if missing:
        response = input(f"\nInstaller automatiquement les dépendances manquantes? (y/N): ")
        if response.lower() in ['y', 'yes', 'oui']:
            if not install_dependencies(missing):
                print("❌ Erreur lors de l'installation des dépendances")
                sys.exit(1)
        else:
            print("⚠️  Installation manuelle requise")
            print("Commandes suggérées:")
            for dep in missing:
                print(f"  pip install {dep}")
            sys.exit(1)
    
    print("\n📁 Vérification de la structure des modules...")
    if not check_module_structure():
        print("❌ Structure des modules incomplète")
        sys.exit(1)
    
    print("\n📄 Vérification des fichiers de données...")
    data_ok = check_data_files()
    
    if data_ok and all(available.values()):
        # Lancer les tests si tout est disponible
        run_tests()
    
    # Création du script d'exemple
    print("\n📝 Création du script d'exemple...")
    create_example_script()
    
    # Résumé final
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DE L'INSTALLATION")
    print("=" * 50)
    
    print(f"✓ Python: {sys.version_info.major}.{sys.version_info.minor}")
    print(f"✓ Modules: Tous présents")
    
    for name, status in available.items():
        status_icon = "✓" if status else "❌"
        print(f"{status_icon} {name}: {'Disponible' if status else 'Manquant'}")
    
    print(f"{'✓' if data_ok else '❌'} Données: {'Présentes' if data_ok else 'Manquantes'}")
    
    if all(available.values()) and data_ok:
        print("\n🎉 Installation complète!")
        print("Vous pouvez maintenant utiliser:")
        print("  python main.py")
        print("  python examples.py")
        print("  python example_simple.py")
    else:
        print("\n⚠️  Installation incomplète")
        print("Veuillez résoudre les problèmes indiqués ci-dessus")


if __name__ == "__main__":
    main()

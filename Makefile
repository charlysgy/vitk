# Makefile pour le projet VTK-ITK
# ================================

# Variables
PYTHON = python3
PROJECT_DIR = .
DATA_DIR = Data
VENV_DIR = venv

# Couleurs pour l'affichage
BLUE = \033[34m
GREEN = \033[32m
YELLOW = \033[33m
RED = \033[31m
NC = \033[0m # No Color

.PHONY: help setup install run test clean lint format check-deps check-data docs

# Aide par défaut
help:
	@echo "$(BLUE)Projet VTK-ITK - Commandes disponibles:$(NC)"
	@echo ""
	@echo "$(GREEN)setup$(NC)      - Configuration initiale complète"
	@echo "$(GREEN)install$(NC)    - Installation des dépendances"
	@echo "$(GREEN)run$(NC)        - Lance l'application principale"
	@echo "$(GREEN)test$(NC)       - Lance les tests unitaires"
	@echo "$(GREEN)check-deps$(NC) - Vérifie les dépendances"
	@echo "$(GREEN)check-data$(NC) - Vérifie la présence des données"
	@echo "$(GREEN)clean$(NC)      - Nettoie les fichiers temporaires"
	@echo "$(GREEN)lint$(NC)       - Vérifie la qualité du code"
	@echo "$(GREEN)format$(NC)     - Formate le code (autopep8)"
	@echo "$(GREEN)docs$(NC)       - Génère la documentation"
	@echo ""
	@echo "$(YELLOW)Exemples:$(NC)"
	@echo "  make setup    # Configuration complète"
	@echo "  make run      # Lance l'application"
	@echo "  make test     # Lance les tests"

# Configuration initiale
setup:
	@echo "$(BLUE)🔧 Configuration initiale du projet...$(NC)"
	@$(PYTHON) setup.py
	@echo "$(GREEN)✓ Configuration terminée$(NC)"

# Installation des dépendances
install:
	@echo "$(BLUE)📦 Installation des dépendances...$(NC)"
	@pip install scipy matplotlib numpy vtk itk
	@echo "$(GREEN)✓ Dépendances installées$(NC)"

# Vérification des dépendances
check-deps:
	@echo "$(BLUE)🔍 Vérification des dépendances...$(NC)"
	@$(PYTHON) -c "import numpy; print('✓ numpy:', numpy.__version__)" || echo "❌ numpy manquant"
	@$(PYTHON) -c "import vtk; print('✓ vtk:', vtk.vtkVersion().GetVTKVersion())" || echo "❌ vtk manquant"
	@$(PYTHON) -c "import itk; print('✓ itk disponible')" || echo "❌ itk manquant"

# Vérification des données
check-data:
	@echo "$(BLUE)📄 Vérification des fichiers de données...$(NC)"
	@test -d $(DATA_DIR) && echo "✓ Dossier Data/ existe" || echo "❌ Dossier Data/ manquant"
	@test -f $(DATA_DIR)/case6_gre1.nrrd && echo "✓ case6_gre1.nrrd trouvé" || echo "❌ case6_gre1.nrrd manquant"
	@test -f $(DATA_DIR)/case6_gre2.nrrd && echo "✓ case6_gre2.nrrd trouvé" || echo "❌ case6_gre2.nrrd manquant"

# Lance l'application principale
run: check-deps check-data
	@echo "$(BLUE)🚀 Lancement de l'application...$(NC)"
	@$(PYTHON) main.py

# Lance les exemples
examples:
	@echo "$(BLUE)📖 Lancement des exemples...$(NC)"
	@$(PYTHON) examples.py

# Lance les tests
test:
	@echo "$(BLUE)🧪 Lancement des tests unitaires...$(NC)"
	@$(PYTHON) test_architecture.py

# Nettoyage
clean:
	@echo "$(BLUE)🧹 Nettoyage des fichiers temporaires...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".DS_Store" -delete
	@echo "$(GREEN)✓ Nettoyage terminé$(NC)"

# Vérification de la qualité du code
lint:
	@echo "$(BLUE)🔍 Vérification de la qualité du code...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 *.py --max-line-length=100 --ignore=E203,W503; \
		echo "$(GREEN)✓ Lint terminé$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  flake8 non installé, installation...$(NC)"; \
		pip install flake8; \
		flake8 *.py --max-line-length=100 --ignore=E203,W503; \
	fi

# Formatage du code
format:
	@echo "$(BLUE)🎨 Formatage du code...$(NC)"
	@if command -v autopep8 >/dev/null 2>&1; then \
		autopep8 --in-place --aggressive --aggressive *.py; \
		echo "$(GREEN)✓ Formatage terminé$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  autopep8 non installé, installation...$(NC)"; \
		pip install autopep8; \
		autopep8 --in-place --aggressive --aggressive *.py; \
	fi

# Génération de la documentation
docs:
	@echo "$(BLUE)📚 Génération de la documentation...$(NC)"
	@if command -v pydoc >/dev/null 2>&1; then \
		pydoc -w converters utils visualization config; \
		echo "$(GREEN)✓ Documentation générée$(NC)"; \
	else \
		echo "$(RED)❌ pydoc non disponible$(NC)"; \
	fi

# Analyse de performance (si profileur disponible)
profile:
	@echo "$(BLUE)⚡ Analyse de performance...$(NC)"
	@$(PYTHON) -m cProfile -o profile_output.prof main.py
	@echo "$(GREEN)✓ Profil sauvé dans profile_output.prof$(NC)"

# Création d'un environnement virtuel
venv:
	@echo "$(BLUE)🏠 Création de l'environnement virtuel...$(NC)"
	@$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)✓ Environnement virtuel créé dans $(VENV_DIR)/$(NC)"
	@echo "$(YELLOW)Activez-le avec: source $(VENV_DIR)/bin/activate$(NC)"

# Installation dans l'environnement virtuel
install-venv: venv
	@echo "$(BLUE)📦 Installation dans l'environnement virtuel...$(NC)"
	@$(VENV_DIR)/bin/pip install numpy vtk itk
	@echo "$(GREEN)✓ Installation terminée$(NC)"

# Informations sur le projet
info:
	@echo "$(BLUE)ℹ️  Informations sur le projet:$(NC)"
	@echo ""
	@echo "📁 Structure:"
	@find . -maxdepth 1 -name "*.py" -exec basename {} \; | sort
	@echo ""
	@echo "📊 Statistiques:"
	@echo "  Fichiers Python: $$(find . -name "*.py" | wc -l)"
	@echo "  Lignes de code: $$(find . -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $$1}')"
	@echo ""
	@echo "🗂️  Modules:"
	@echo "  - converters.py: Conversions ITK/NumPy/VTK"
	@echo "  - visualization.py: Interface interactive"
	@echo "  - utils.py: Utilitaires et debug"
	@echo "  - config.py: Configuration"
	@echo "  - main.py: Point d'entrée principal"

# Backup du projet
backup:
	@echo "$(BLUE)💾 Sauvegarde du projet...$(NC)"
	@tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz \
		--exclude="__pycache__" \
		--exclude="*.pyc" \
		--exclude="venv" \
		--exclude="backup_*.tar.gz" \
		.
	@echo "$(GREEN)✓ Sauvegarde créée$(NC)"

# Vérification complète avant commit
check-all: clean lint test
	@echo "$(GREEN)✅ Toutes les vérifications passées$(NC)"

.PHONY: help setup dev data train test lint demo repro clean

PYTHON ?= python
NPM ?= npm

help:
	@echo "DelayRay Master Command Interface"
	@echo "-----------------------------------"
	@echo "make setup    - Install backend & frontend dependencies"
	@echo "make dev      - Start FastAPI backend and Vite frontend concurrently"
	@echo "make data     - Generate synthetic data and seed database"
	@echo "make train    - Run ML training, evaluation, and ablation pipelines"
	@echo "make test     - Run backend and frontend automated test suites"
	@echo "make lint     - Run code style and lint checks"
	@echo "make demo     - Launch the full containerized stack via Docker Compose"
	@echo "make repro    - Clean, regenerate data, retrain, and re-evaluate"
	@echo "make clean    - Remove build artifacts, pycache, and temporary files"

setup:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r backend/requirements.txt
	cd frontend && $(NPM) install

dev:
	$(PYTHON) scripts/run_dev.py

data:
	$(PYTHON) scripts/generate_data.py
	$(PYTHON) scripts/seed_db.py

train:
	$(PYTHON) scripts/train.py
	$(PYTHON) scripts/evaluate.py
	$(PYTHON) scripts/run_ablation.py

test:
	$(PYTHON) -m pytest backend/tests -v

lint:
	ruff check backend
	black --check backend
	cd frontend && $(NPM) run lint

demo:
	docker compose up --build

repro: clean data train test
	@echo "DelayRay reproducibility pipeline completed successfully."

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage

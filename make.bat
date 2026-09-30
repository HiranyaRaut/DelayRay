@echo off
REM DelayRay Windows Make Polyfill

IF "%1"=="" GOTO help
IF "%1"=="help" GOTO help
IF "%1"=="setup" GOTO setup
IF "%1"=="dev" GOTO dev
IF "%1"=="data" GOTO data
IF "%1"=="train" GOTO train
IF "%1"=="test" GOTO test
IF "%1"=="lint" GOTO lint
IF "%1"=="demo" GOTO demo
IF "%1"=="repro" GOTO repro

:help
echo DelayRay Windows Command Helper
echo -------------------------------
echo make setup   - Install backend and frontend dependencies
echo make dev     - Start FastAPI backend and Vite frontend concurrently
echo make data    - Generate synthetic data and seed database
echo make train   - Run ML training, evaluation, and ablation
echo make test    - Run automated test suite
echo make lint    - Run linting and code checks
echo make demo    - Launch full stack in Docker Compose
echo make repro   - Regenerate data, retrain, and re-evaluate
GOTO end

:setup
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
GOTO end

:dev
python scripts/run_dev.py
GOTO end

:data
python scripts/generate_data.py
python scripts/seed_db.py
GOTO end

:train
python scripts/train.py
python scripts/evaluate.py
python scripts/run_ablation.py
GOTO end

:test
pytest backend/tests -v
GOTO end

:lint
ruff check backend
black --check backend
cd frontend && npm run lint && cd ..
GOTO end

:demo
docker compose up --build
GOTO end

:repro
call make.bat data
call make.bat train
call make.bat test
echo Repro completed.
GOTO end

:end

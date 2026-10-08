.PHONY: dbt train api mlflow test lint format clean

dbt:
	cd dbt_project && dbt build

train:
	python ml/train.py

api:
	uvicorn api.main:app --reload

mlflow:
	mlflow ui --port 5000

test:
	pytest -v

lint:
	ruff check .

format:
	ruff format .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +

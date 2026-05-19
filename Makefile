.PHONY: install test lint run setup

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	ruff check app/ tests/ evals/
	ruff format --check app/ tests/ evals/

run:
	streamlit run app/main.py

setup:
	@echo "Running Snowflake DDL setup..."
	snowsql -f sql/01_database.sql
	snowsql -f sql/02_schema.sql
	snowsql -f sql/03_tables.sql
	snowsql -f sql/04_load.sql
	@echo "Setup complete."

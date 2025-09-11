install:
	pip install -e .

run:
	streamlit run app/Home.py

lint:
	ruff check . || true

format:
	black .

test:
	pytest -q

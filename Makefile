# Makefile

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

logs:
	docker-compose logs -f

install:
	python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

run-api:
	uvicorn src.services.payments.api.api:app --reload

run-ui:
	streamlit run src/ui/streamlit_app.py

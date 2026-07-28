build:
	docker build -t marino-rag-api .

dev:
	docker run -p 8000:8000 --env-file .env -v .:/app marino-rag-api \
		uvicorn main:app --host 0.0.0.0 --port 8000 --reload

run:
	docker run -p 8000:8000 --env-file .env marino-rag-api

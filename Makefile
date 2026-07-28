build:
	docker build -t marino-rag-api .

dev:
	docker run -p 10000:10000 --env-file .env -v .:/app marino-rag-api \
		uvicorn main:app --host 0.0.0.0 --port 10000 --reload

run:
	docker run -p 10000:10000 --env-file .env marino-rag-api

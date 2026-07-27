dev:
	uvicorn main:app --reload --port 8000

prod:
	gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
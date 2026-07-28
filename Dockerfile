# ---------- Stage 1: builder ----------
# Install dependecies, some libraries by llama-index/HF may require build-essential
# to compile wheel non pure-Python

FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \ 
    build-essential \ 
    && rm -rf /var/lib/apt/lists/* 

# Only copy requirements.txt before the rest of the code: if only 
# main.py/rag.py changes, this layer stays in cache and it does no reinstall 

COPY requirements.txt . 
RUN pip install --user --no-cache-dir -r requirements.txt 

# ---------- Stage 2: runtime ----------
# Final clean image: no build-essential, no pip cache 

FROM python:3.11-slim 

WORKDIR /app 

RUN useradd --create-home appuser 

# Only copy the installed python libraries from stage builder
COPY --from=builder /root/.local /home/appuser/.local 

COPY . . 

RUN chown -R appuser:appuser /app 
USER appuser 

ENV PATH=/home/appuser/.local/bin:$PATH 
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \ 
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1 

# in production command 
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT:-8000}"]
from fastapi import FastAPI
from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time
from prometheus_client.exposition import generate_latest

app = FastAPI()

# Configuração do Prometheus
REQUESTS_TOTAL = Counter('http_requests_total', 'Total number of HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Duration of HTTP requests in seconds')
REQUEST_ERRORS = Counter('http_requests_errors_total', 'Total number of HTTP request errors')

@app.on_event("startup")
async def startup_event():
    # Inicia o servidor de métricas Prometheus
    start_http_server(8001)

@app.get("/healthcheck")
async def healthcheck():
    REQUESTS_TOTAL.inc()
    start_time = time.time()
    try:
        response = {"status": "healthy"}
    except Exception as e:
        REQUEST_ERRORS.inc()
        raise e
    finally:
        latency = time.time() - start_time
        REQUEST_LATENCY.observe(latency)
    return response

@app.get("/test")
async def test_route():
    REQUESTS_TOTAL.inc()
    start_time = time.time()
    try:
        response = {"message": "test successful"}
    except Exception as e:
        REQUEST_ERRORS.inc()
        raise e
    finally:
        latency = time.time() - start_time
        REQUEST_LATENCY.observe(latency)
    return response

@app.get("/metrics")
def metrics():
    return generate_latest()

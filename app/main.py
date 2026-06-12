from fastapi import FastAPI
from redis import Redis
from psycopg2 import connect
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
import os

app = FastAPI()

Instrumentator().instrument(app).expose(app)

REQUEST_COUNT = Counter("api_requests_total", "Número total de peticiones a la API")

redis_client = Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)

def get_db_connection():
    return connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "secret")
    )

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
def read_root():
    REQUEST_COUNT.inc()
    try:
        hits = redis_client.incr("hits")
    except Exception:
        hits = 0
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
    except Exception:
        db_version = "unavailable"
    return {
        "status": "Cloud Environment Operational",
        "total_api_requests": hits,
        "database_connected": db_version
    }

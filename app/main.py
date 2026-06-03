from fastapi import FastAPI
from redis import Redis
from psycopg2 import connect
import os

app = FastAPI()

redis_client = Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379)

def get_db_connection():
    return connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "secret")
    )

@app.get("/")
def read_root():
    hits = redis_client.incr("hits")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {
        "status": "Cloud Environment Operational",
        "total_api_requests": hits,
        "database_connected": db_version
    }

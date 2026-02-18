
from app.api.routes import datasets, connections
from fastapi import FastAPI


app = FastAPI(title="Veda API")

@app.get("/")
def read_root():
    return {"message": "Veda backend is running"}

app.include_router(datasets.router)
app.include_router(connections.router)

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

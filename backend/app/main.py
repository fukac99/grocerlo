from fastapi import FastAPI

from app.api import products_router

app = FastAPI(title="Grocery Saver API")
app.include_router(products_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

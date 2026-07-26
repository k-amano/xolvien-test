from fastapi import FastAPI

from app.database import engine, Base
from app.routers import expenses, categories, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker REST API", version="1.0.0")

app.include_router(expenses.router)
app.include_router(categories.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}

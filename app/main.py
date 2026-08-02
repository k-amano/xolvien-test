from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.routers import expenses, categories, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker REST API", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "VALIDATION_ERROR", "message": str(exc)}},
    )


app.include_router(expenses.router)
app.include_router(categories.router)
app.include_router(reports.router)


@app.get("/health")
def health():
    return {"status": "ok"}

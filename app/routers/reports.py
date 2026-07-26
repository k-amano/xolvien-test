from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.database import get_db
from app.models import Expense, Category
from app.schemas import MonthlyReport, CategorySummary
from app.errors import error_response

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


@router.get("/monthly", response_model=MonthlyReport)
def monthly_report(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    if year < 2000 or year > 2100:
        return error_response(400, "VALIDATION_ERROR", "Year must be between 2000 and 2100.")
    if month < 1 or month > 12:
        return error_response(400, "VALIDATION_ERROR", "Month must be between 1 and 12.")

    expenses = (
        db.query(Expense)
        .filter(extract("year", Expense.date) == year)
        .filter(extract("month", Expense.date) == month)
        .all()
    )

    total = sum(e.amount for e in expenses)
    count = len(expenses)

    cat_totals: dict[int, int] = {}
    for e in expenses:
        cat_totals[e.category_id] = cat_totals.get(e.category_id, 0) + e.amount

    by_category = []
    for cat_id, subtotal in cat_totals.items():
        cat = db.query(Category).filter(Category.id == cat_id).first()
        share = round(subtotal / total * 100, 1) if total > 0 else 0.0
        by_category.append(
            CategorySummary(category=cat.name, subtotal=subtotal, share=share)
        )

    return MonthlyReport(
        year=year, month=month, total=total, count=count, by_category=by_category
    )

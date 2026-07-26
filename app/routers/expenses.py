from datetime import date as date_type
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Expense, Category
from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.errors import error_response

router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])


def _validate_expense_fields(data, db, partial=False):
    """Validate expense fields. Returns error_response or None."""
    if hasattr(data, "amount") and data.amount is not None:
        if not isinstance(data.amount, int) or data.amount < 1:
            return error_response(400, "VALIDATION_ERROR", "Amount must be an integer >= 1.")

    if hasattr(data, "memo") and data.memo is not None:
        if len(data.memo) > 200:
            return error_response(400, "VALIDATION_ERROR", "Memo must be at most 200 characters.")

    if hasattr(data, "category_id") and data.category_id is not None:
        cat = db.query(Category).filter(Category.id == data.category_id).first()
        if not cat:
            return error_response(404, "NOT_FOUND", "Category not found.")

    return None


@router.post("", status_code=201, response_model=ExpenseResponse)
def create_expense(data: ExpenseCreate, db: Session = Depends(get_db)):
    err = _validate_expense_fields(data, db)
    if err:
        return err

    expense = Expense(
        date=data.date,
        amount=data.amount,
        category_id=data.category_id,
        memo=data.memo,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("", response_model=list[ExpenseResponse])
def list_expenses(
    category_id: Optional[int] = Query(None),
    from_date: Optional[date_type] = Query(None, alias="from"),
    to_date: Optional[date_type] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    q = db.query(Expense)
    if category_id is not None:
        q = q.filter(Expense.category_id == category_id)
    if from_date is not None:
        q = q.filter(Expense.date >= from_date)
    if to_date is not None:
        q = q.filter(Expense.date <= to_date)
    return q.order_by(Expense.date.desc(), Expense.id.desc()).all()


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        return error_response(404, "NOT_FOUND", "Expense not found.")
    return expense


@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, data: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        return error_response(404, "NOT_FOUND", "Expense not found.")

    err = _validate_expense_fields(data, db, partial=True)
    if err:
        return err

    if data.date is not None:
        expense.date = data.date
    if data.amount is not None:
        expense.amount = data.amount
    if data.category_id is not None:
        expense.category_id = data.category_id
    if data.memo is not None:
        expense.memo = data.memo

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        return error_response(404, "NOT_FOUND", "Expense not found.")
    db.delete(expense)
    db.commit()

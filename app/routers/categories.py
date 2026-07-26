from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Expense
from app.schemas import CategoryCreate, CategoryResponse
from app.errors import error_response

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.post("", status_code=201, response_model=CategoryResponse)
def create_category(data: CategoryCreate, db: Session = Depends(get_db)):
    name = data.name.strip()
    if not name or len(name) > 50:
        return error_response(400, "VALIDATION_ERROR", "Category name must be 1-50 characters after trimming.")

    existing = db.query(Category).filter(Category.name.ilike(name)).first()
    if existing:
        return error_response(409, "DUPLICATE_NAME", f"Category '{name}' already exists.")

    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name.asc()).all()


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        return error_response(404, "NOT_FOUND", "Category not found.")

    expense_count = db.query(Expense).filter(Expense.category_id == category_id).count()
    if expense_count > 0:
        return error_response(409, "CATEGORY_IN_USE", "Cannot delete category that is referenced by expenses.")

    db.delete(category)
    db.commit()

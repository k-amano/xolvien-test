from datetime import date, datetime
from typing import Optional, List

from pydantic import BaseModel, field_validator


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    date: date
    amount: int
    category_id: int
    memo: Optional[str] = None


class ExpenseUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[int] = None
    category_id: Optional[int] = None
    memo: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    date: date
    amount: int
    category_id: int
    memo: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CategorySummary(BaseModel):
    category: str
    subtotal: int
    share: float


class MonthlyReport(BaseModel):
    year: int
    month: int
    total: int
    count: int
    by_category: List[CategorySummary]

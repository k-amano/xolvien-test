# Expense Tracker REST API

A REST API for recording daily expenses, organizing them by category, and reviewing monthly spending summaries.

## Setup

```bash
pip install -r requirements.txt
```

## Run the server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

API docs available at `http://localhost:8000/docs`.

## Run tests

```bash
pytest tests/ -v
```

## API Usage Example

```bash
# Create a category
curl -X POST http://localhost:8000/api/v1/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "Food"}'

# Create an expense
curl -X POST http://localhost:8000/api/v1/expenses \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-07-15", "amount": 1500, "category_id": 1, "memo": "lunch"}'

# List expenses
curl http://localhost:8000/api/v1/expenses

# Monthly report
curl "http://localhost:8000/api/v1/reports/monthly?year=2026&month=7"

# Health check
curl http://localhost:8000/health
```

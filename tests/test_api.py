"""Test cases TP-001 through TP-010."""


def _create_category(client, name="Food"):
    return client.post("/api/v1/categories", json={"name": name})


def _create_expense(client, category_id, date="2026-07-15", amount=1000, memo="lunch"):
    return client.post(
        "/api/v1/expenses",
        json={"date": date, "amount": amount, "category_id": category_id, "memo": memo},
    )


def test_tp001_create_expense_valid(client):
    """TP-001: POST /expenses with valid fields → 201, response has id and all fields."""
    cat = _create_category(client)
    cat_id = cat.json()["id"]

    resp = _create_expense(client, cat_id, date="2026-07-15", amount=1500, memo="dinner")
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["date"] == "2026-07-15"
    assert body["amount"] == 1500
    assert body["category_id"] == cat_id
    assert body["memo"] == "dinner"
    assert "created_at" in body


def test_tp002_create_expense_invalid_amount(client):
    """TP-002: POST /expenses with amount=0 and amount=-100 → 400 VALIDATION_ERROR."""
    cat = _create_category(client)
    cat_id = cat.json()["id"]

    resp_zero = client.post(
        "/api/v1/expenses",
        json={"date": "2026-07-15", "amount": 0, "category_id": cat_id},
    )
    assert resp_zero.status_code == 400
    assert resp_zero.json()["error"]["code"] == "VALIDATION_ERROR"

    resp_neg = client.post(
        "/api/v1/expenses",
        json={"date": "2026-07-15", "amount": -100, "category_id": cat_id},
    )
    assert resp_neg.status_code == 400
    assert resp_neg.json()["error"]["code"] == "VALIDATION_ERROR"


def test_tp003_create_expense_nonexistent_category(client):
    """TP-003: POST /expenses with non-existent category_id → 404 NOT_FOUND."""
    resp = client.post(
        "/api/v1/expenses",
        json={"date": "2026-07-15", "amount": 500, "category_id": 9999},
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


def test_tp004_list_expenses_date_range(client):
    """TP-004: GET /expenses with from/to date range → only matching expenses, newest first."""
    cat = _create_category(client)
    cat_id = cat.json()["id"]

    _create_expense(client, cat_id, date="2026-07-01", amount=100)
    _create_expense(client, cat_id, date="2026-07-10", amount=200)
    _create_expense(client, cat_id, date="2026-07-20", amount=300)
    _create_expense(client, cat_id, date="2026-07-31", amount=400)

    resp = client.get("/api/v1/expenses", params={"from": "2026-07-05", "to": "2026-07-25"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["date"] == "2026-07-20"
    assert data[1]["date"] == "2026-07-10"


def test_tp005_patch_expense_amount_only(client):
    """TP-005: PATCH /expenses/{id} updating only amount → 200, amount changed, others unchanged."""
    cat = _create_category(client)
    cat_id = cat.json()["id"]

    created = _create_expense(client, cat_id, date="2026-07-15", amount=1000, memo="lunch").json()
    expense_id = created["id"]

    resp = client.patch(f"/api/v1/expenses/{expense_id}", json={"amount": 2000})
    assert resp.status_code == 200
    body = resp.json()
    assert body["amount"] == 2000
    assert body["date"] == created["date"]
    assert body["category_id"] == created["category_id"]
    assert body["memo"] == created["memo"]


def test_tp006_delete_then_get(client):
    """TP-006: DELETE then GET same id → 204 then 404."""
    cat = _create_category(client)
    cat_id = cat.json()["id"]

    created = _create_expense(client, cat_id).json()
    expense_id = created["id"]

    del_resp = client.delete(f"/api/v1/expenses/{expense_id}")
    assert del_resp.status_code == 204

    get_resp = client.get(f"/api/v1/expenses/{expense_id}")
    assert get_resp.status_code == 404
    assert get_resp.json()["error"]["code"] == "NOT_FOUND"


def test_tp007_duplicate_category_different_case(client):
    """TP-007: POST /categories with duplicate name different casing → 409 DUPLICATE_NAME."""
    resp1 = _create_category(client, "Food")
    assert resp1.status_code == 201

    resp2 = _create_category(client, "food")
    assert resp2.status_code == 409
    assert resp2.json()["error"]["code"] == "DUPLICATE_NAME"


def test_tp008_delete_category_in_use(client):
    """TP-008: DELETE /categories/{id} still referenced by expense → 409 CATEGORY_IN_USE."""
    cat = _create_category(client)
    cat_id = cat.json()["id"]

    _create_expense(client, cat_id)

    resp = client.delete(f"/api/v1/categories/{cat_id}")
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "CATEGORY_IN_USE"


def test_tp009_monthly_report_three_categories(client):
    """TP-009: GET /reports/monthly with expenses in 3 categories → correct totals and shares."""
    c1 = _create_category(client, "Food").json()["id"]
    c2 = _create_category(client, "Transport").json()["id"]
    c3 = _create_category(client, "Utilities").json()["id"]

    _create_expense(client, c1, date="2026-07-10", amount=5000)
    _create_expense(client, c1, date="2026-07-11", amount=3000)
    _create_expense(client, c2, date="2026-07-12", amount=2000)
    _create_expense(client, c3, date="2026-07-13", amount=10000)

    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 7})
    assert resp.status_code == 200
    body = resp.json()
    assert body["year"] == 2026
    assert body["month"] == 7
    assert body["total"] == 20000
    assert body["count"] == 4

    by_cat = {item["category"]: item for item in body["by_category"]}
    assert by_cat["Food"]["subtotal"] == 8000
    assert by_cat["Transport"]["subtotal"] == 2000
    assert by_cat["Utilities"]["subtotal"] == 10000

    total_share = sum(item["share"] for item in body["by_category"])
    assert abs(total_share - 100.0) < 0.5


def test_tp010_monthly_report_no_expenses(client):
    """TP-010: GET /reports/monthly for month with no expenses → 200, total 0, count 0, empty."""
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 0
    assert body["count"] == 0
    assert body["by_category"] == []

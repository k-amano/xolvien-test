"""Integration test cases ITC-001 through ITC-050."""

import json


def _create_category(client, name="Food"):
    return client.post("/api/v1/categories", json={"name": name})


def _create_expense(client, category_id, date="2026-07-15", amount=1000, memo="lunch"):
    return client.post(
        "/api/v1/expenses",
        json={"date": date, "amount": amount, "category_id": category_id, "memo": memo},
    )


# ITC-001
def test_itc001_create_expense_valid_fields_and_verify_persistence(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    resp = _create_expense(client, cat_id, date="2026-07-15", amount=1500, memo="dinner")
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-001', 'actual': str(actual)}))
    assert actual == 201
    body = resp.json()
    assert isinstance(body["id"], int)
    assert body["date"] == "2026-07-15"
    assert body["amount"] == 1500
    assert body["category_id"] == cat_id
    assert body["memo"] == "dinner"
    assert "created_at" in body
    # Verify persistence via GET
    get_resp = client.get(f"/api/v1/expenses/{body['id']}")
    assert get_resp.status_code == 200
    get_body = get_resp.json()
    assert get_body["id"] == body["id"]
    assert get_body["date"] == "2026-07-15"
    assert get_body["amount"] == 1500
    assert get_body["category_id"] == cat_id
    assert get_body["memo"] == "dinner"
    assert get_body["created_at"] == body["created_at"]


# ITC-002
def test_itc002_create_expense_invalid_amount_zero_and_negative(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    resp_zero = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 0, "category_id": cat_id})
    resp_neg = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": -100, "category_id": cat_id})
    actual = f"{resp_zero.status_code},{resp_neg.status_code}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-002', 'actual': str(actual)}))
    assert resp_zero.status_code == 400
    assert resp_zero.json()["error"]["code"] == "VALIDATION_ERROR"
    assert resp_neg.status_code == 400
    assert resp_neg.json()["error"]["code"] == "VALIDATION_ERROR"
    # Verify no expenses were created
    list_resp = client.get("/api/v1/expenses")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 0


# ITC-003
def test_itc003_create_expense_nonexistent_category(client):
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 500, "category_id": 9999})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-003', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# ITC-004
def test_itc004_list_expenses_date_range_filter_newest_first(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id, date="2026-07-01", amount=100)
    _create_expense(client, cat_id, date="2026-07-10", amount=200)
    _create_expense(client, cat_id, date="2026-07-20", amount=300)
    _create_expense(client, cat_id, date="2026-07-31", amount=400)
    resp = client.get("/api/v1/expenses", params={"from": "2026-07-05", "to": "2026-07-25"})
    data = resp.json()
    actual = f"{resp.status_code},len={len(data)},dates={[d['date'] for d in data]}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-004', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 2
    assert data[0]["date"] == "2026-07-20"
    assert data[1]["date"] == "2026-07-10"


# ITC-005
def test_itc005_patch_expense_amount_only_others_unchanged(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id, date="2026-07-15", amount=1000, memo="lunch").json()
    expense_id = created["id"]
    resp = client.patch(f"/api/v1/expenses/{expense_id}", json={"amount": 2000})
    body = resp.json()
    actual = f"{resp.status_code},amount={body['amount']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-005', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["amount"] == 2000
    assert body["date"] == created["date"]
    assert body["category_id"] == created["category_id"]
    assert body["memo"] == created["memo"]


# ITC-006
def test_itc006_delete_expense_then_get_returns_404(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id).json()
    expense_id = created["id"]
    del_resp = client.delete(f"/api/v1/expenses/{expense_id}")
    get_resp = client.get(f"/api/v1/expenses/{expense_id}")
    actual = f"del={del_resp.status_code},get={get_resp.status_code}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-006', 'actual': str(actual)}))
    assert del_resp.status_code == 204
    assert get_resp.status_code == 404
    assert get_resp.json()["error"]["code"] == "NOT_FOUND"


# ITC-007
def test_itc007_duplicate_category_name_different_case(client):
    resp1 = _create_category(client, "Food")
    resp2 = _create_category(client, "food")
    actual = f"first={resp1.status_code},second={resp2.status_code}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-007', 'actual': str(actual)}))
    assert resp1.status_code == 201
    assert resp2.status_code == 409
    assert resp2.json()["error"]["code"] == "DUPLICATE_NAME"


# ITC-008
def test_itc008_delete_category_in_use_by_expense(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id)
    resp = client.delete(f"/api/v1/categories/{cat_id}")
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-008', 'actual': str(actual)}))
    assert actual == 409
    assert resp.json()["error"]["code"] == "CATEGORY_IN_USE"


# ITC-009
def test_itc009_monthly_report_three_categories_correct_aggregation(client):
    c1 = _create_category(client, "Food").json()["id"]
    c2 = _create_category(client, "Transport").json()["id"]
    c3 = _create_category(client, "Utilities").json()["id"]
    _create_expense(client, c1, date="2026-07-10", amount=5000)
    _create_expense(client, c1, date="2026-07-11", amount=3000)
    _create_expense(client, c2, date="2026-07-12", amount=2000)
    _create_expense(client, c3, date="2026-07-13", amount=10000)
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 7})
    body = resp.json()
    actual = f"{resp.status_code},total={body['total']},count={body['count']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-009', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["total"] == 20000
    assert body["count"] == 4
    by_cat = {item["category"]: item for item in body["by_category"]}
    assert by_cat["Food"]["subtotal"] == 8000
    assert by_cat["Food"]["share"] == 40.0
    assert by_cat["Transport"]["subtotal"] == 2000
    assert by_cat["Transport"]["share"] == 10.0
    assert by_cat["Utilities"]["subtotal"] == 10000
    assert by_cat["Utilities"]["share"] == 50.0
    total_share = sum(item["share"] for item in body["by_category"])
    assert abs(total_share - 100.0) < 0.5


# ITC-010
def test_itc010_monthly_report_no_expenses_returns_zeros(client):
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 1})
    body = resp.json()
    actual = f"{resp.status_code},total={body['total']},count={body['count']},by_cat={body['by_category']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-010', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["year"] == 2026
    assert body["month"] == 1
    assert body["total"] == 0
    assert body["count"] == 0
    assert body["by_category"] == []


# ITC-011
def test_itc011_health_check_returns_ok(client):
    resp = client.get("/health")
    body = resp.json()
    actual = f"{resp.status_code},status={body['status']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-011', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["status"] == "ok"


# ITC-012
def test_itc012_create_expense_invalid_date_format(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    resp = client.post("/api/v1/expenses", json={"date": "07-15-2026", "amount": 500, "category_id": cat_id})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-012', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# ITC-013
def test_itc013_patch_expense_date_only(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id, date="2026-07-15", amount=1000, memo="lunch").json()
    expense_id = created["id"]
    resp = client.patch(f"/api/v1/expenses/{expense_id}", json={"date": "2026-08-01"})
    body = resp.json()
    actual = f"{resp.status_code},date={body['date']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-013', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["date"] == "2026-08-01"
    assert body["amount"] == created["amount"]
    assert body["category_id"] == created["category_id"]
    assert body["memo"] == created["memo"]


# ITC-014
def test_itc014_patch_expense_memo_only(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id, date="2026-07-15", amount=1000, memo="lunch").json()
    expense_id = created["id"]
    resp = client.patch(f"/api/v1/expenses/{expense_id}", json={"memo": "updated memo"})
    body = resp.json()
    actual = f"{resp.status_code},memo={body['memo']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-014', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["memo"] == "updated memo"
    assert body["date"] == created["date"]
    assert body["amount"] == created["amount"]
    assert body["category_id"] == created["category_id"]


# ITC-015
def test_itc015_list_expenses_no_filter_sorted_desc(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id, date="2026-07-01", amount=100)
    _create_expense(client, cat_id, date="2026-07-20", amount=200)
    _create_expense(client, cat_id, date="2026-07-10", amount=300)
    resp = client.get("/api/v1/expenses")
    data = resp.json()
    dates = [d["date"] for d in data]
    actual = f"{resp.status_code},dates={dates}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-015', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert dates == sorted(dates, reverse=True)


# ITC-016
def test_itc016_monthly_report_year_above_range(client):
    resp = client.get("/api/v1/reports/monthly", params={"year": 2101, "month": 6})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-016', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# ITC-017
def test_itc017_create_category_name_whitespace_trimmed(client):
    resp = client.post("/api/v1/categories", json={"name": "  Groceries  "})
    body = resp.json()
    actual = f"{resp.status_code},name={body['name']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-017', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert body["name"] == "Groceries"
    assert isinstance(body["id"], int)


# ITC-018
def test_itc018_patch_expense_invalid_amount_zero(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id).json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"amount": 0})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-018', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# ITC-019
def test_itc019_list_expenses_combined_category_and_date_filter(client):
    cat1 = _create_category(client, "Food").json()["id"]
    cat2 = _create_category(client, "Transport").json()["id"]
    _create_expense(client, cat1, date="2026-07-01", amount=100)
    _create_expense(client, cat1, date="2026-07-15", amount=200)
    _create_expense(client, cat2, date="2026-07-10", amount=300)
    _create_expense(client, cat1, date="2026-07-25", amount=400)
    resp = client.get("/api/v1/expenses", params={"category_id": cat1, "from": "2026-07-05", "to": "2026-07-25"})
    data = resp.json()
    actual = f"{resp.status_code},len={len(data)}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-019', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 2
    assert all(item["category_id"] == cat1 for item in data)
    dates = [d["date"] for d in data]
    assert dates == sorted(dates, reverse=True)


# ITC-020
def test_itc020_monthly_report_missing_params(client):
    resp = client.get("/api/v1/reports/monthly")
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-020', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# ITC-021
def test_itc021_monthly_report_isolates_single_month(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id, date="2026-06-15", amount=1000)
    _create_expense(client, cat_id, date="2026-07-15", amount=2000)
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 7})
    body = resp.json()
    actual = f"{resp.status_code},total={body['total']},count={body['count']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-021', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["total"] == 2000
    assert body["count"] == 1
    assert len(body["by_category"]) == 1


# ITC-022
def test_itc022_deleted_expense_excluded_from_report(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    e1 = _create_expense(client, cat_id, date="2026-07-10", amount=500).json()
    _create_expense(client, cat_id, date="2026-07-11", amount=300)
    client.delete(f"/api/v1/expenses/{e1['id']}")
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 7})
    body = resp.json()
    actual = f"{resp.status_code},total={body['total']},count={body['count']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-022', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["total"] == 300
    assert body["count"] == 1


# ITC-023
def test_itc023_create_expense_with_deleted_category_fails(client):
    cat = _create_category(client, "Temp")
    cat_id = cat.json()["id"]
    client.delete(f"/api/v1/categories/{cat_id}")
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 100, "category_id": cat_id})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-023', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# ITC-024
def test_itc024_patched_amount_reflected_in_report(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    e = _create_expense(client, cat_id, date="2026-07-15", amount=1000).json()
    client.patch(f"/api/v1/expenses/{e['id']}", json={"amount": 5000})
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 7})
    body = resp.json()
    actual = f"{resp.status_code},total={body['total']},count={body['count']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-024', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["total"] == 5000
    assert body["count"] == 1


# ITC-025
def test_itc025_patch_date_moves_expense_out_of_month_report(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    e = _create_expense(client, cat_id, date="2026-07-15", amount=1000).json()
    client.patch(f"/api/v1/expenses/{e['id']}", json={"date": "2026-08-15"})
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 7})
    body = resp.json()
    actual = f"{resp.status_code},total={body['total']},count={body['count']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-025', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["total"] == 0
    assert body["count"] == 0
    assert body["by_category"] == []


# ITC-026
def test_itc026_list_expenses_combined_category_and_date_filter(client):
    food_id = _create_category(client, "Food").json()["id"]
    transport_id = _create_category(client, "Transport").json()["id"]
    _create_expense(client, food_id, date="2026-07-10", amount=100)
    _create_expense(client, transport_id, date="2026-07-20", amount=200)
    _create_expense(client, food_id, date="2026-07-25", amount=300)
    resp = client.get("/api/v1/expenses", params={"category_id": food_id, "from": "2026-07-15", "to": "2026-07-31"})
    data = resp.json()
    actual = f"{resp.status_code},len={len(data)}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-026', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 1
    assert data[0]["amount"] == 300
    assert data[0]["date"] == "2026-07-25"


# ITC-027
def test_itc027_recreate_category_after_delete(client):
    cat1 = _create_category(client, "Temp")
    cat1_id = cat1.json()["id"]
    client.delete(f"/api/v1/categories/{cat1_id}")
    cat2 = _create_category(client, "Temp")
    actual = cat2.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-027', 'actual': str(actual)}))
    assert actual == 201
    body = cat2.json()
    assert body["name"] == "Temp"
    assert isinstance(body["id"], int)


# ITC-028
def test_itc028_patch_category_moves_expense_in_filtered_list(client):
    food_id = _create_category(client, "Food").json()["id"]
    transport_id = _create_category(client, "Transport").json()["id"]
    e = _create_expense(client, food_id, date="2026-07-15", amount=1000).json()
    client.patch(f"/api/v1/expenses/{e['id']}", json={"category_id": transport_id})
    food_resp = client.get("/api/v1/expenses", params={"category_id": food_id})
    transport_resp = client.get("/api/v1/expenses", params={"category_id": transport_id})
    actual = f"food_len={len(food_resp.json())},transport_len={len(transport_resp.json())}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-028', 'actual': str(actual)}))
    assert food_resp.status_code == 200
    assert len(food_resp.json()) == 0
    assert transport_resp.status_code == 200
    assert len(transport_resp.json()) == 1


# ITC-029
def test_itc029_delete_expenses_then_delete_category_succeeds(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    e = _create_expense(client, cat_id, date="2026-07-15", amount=500).json()
    del_expense = client.delete(f"/api/v1/expenses/{e['id']}")
    del_cat = client.delete(f"/api/v1/categories/{cat_id}")
    actual = f"del_expense={del_expense.status_code},del_cat={del_cat.status_code}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-029', 'actual': str(actual)}))
    assert del_expense.status_code == 204
    assert del_cat.status_code == 204


# ITC-030
def test_itc030_full_lifecycle_health_create_list(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    cat = _create_category(client, "Food")
    assert cat.status_code == 201
    cat_id = cat.json()["id"]
    expense = _create_expense(client, cat_id, date="2026-07-15", amount=750, memo="lifecycle")
    assert expense.status_code == 201
    list_resp = client.get("/api/v1/expenses")
    data = list_resp.json()
    actual = f"health={health.status_code},cat={cat.status_code},expense={expense.status_code},list={list_resp.status_code},len={len(data)}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-030', 'actual': str(actual)}))
    assert list_resp.status_code == 200
    assert len(data) == 1
    assert data[0]["amount"] == 750
    assert data[0]["memo"] == "lifecycle"
    assert data[0]["date"] == "2026-07-15"
    assert data[0]["category_id"] == cat_id


# ITC-031
def test_itc031_health_check_returns_ok(client):
    resp = client.get("/health")
    body = resp.json()
    actual = f"{resp.status_code},status={body['status']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-031', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body == {"status": "ok"}


# ITC-032
def test_itc032_patch_expense_date_only(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id, date="2026-07-15", amount=1000, memo="lunch").json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"date": "2026-08-01"})
    body = resp.json()
    actual = f"{resp.status_code},date={body['date']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-032', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["date"] == "2026-08-01"
    assert body["amount"] == created["amount"]
    assert body["category_id"] == created["category_id"]
    assert body["memo"] == created["memo"]


# ITC-033
def test_itc033_patch_expense_memo_only(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id, date="2026-07-15", amount=1000, memo="lunch").json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"memo": "updated memo"})
    body = resp.json()
    actual = f"{resp.status_code},memo={body['memo']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-033', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["memo"] == "updated memo"
    assert body["date"] == created["date"]
    assert body["amount"] == created["amount"]
    assert body["category_id"] == created["category_id"]


# ITC-034
def test_itc034_patch_expense_invalid_amount_zero(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id).json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"amount": 0})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-034', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# ITC-035
def test_itc035_list_expenses_from_filter_only(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id, date="2026-07-01", amount=100)
    _create_expense(client, cat_id, date="2026-07-15", amount=200)
    _create_expense(client, cat_id, date="2026-07-30", amount=300)
    resp = client.get("/api/v1/expenses", params={"from": "2026-07-15"})
    data = resp.json()
    actual = f"{resp.status_code},len={len(data)}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-035', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 2
    assert all(d["date"] >= "2026-07-15" for d in data)
    dates = [d["date"] for d in data]
    assert dates == sorted(dates, reverse=True)


# ITC-036
def test_itc036_list_expenses_to_filter_only(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id, date="2026-07-01", amount=100)
    _create_expense(client, cat_id, date="2026-07-15", amount=200)
    _create_expense(client, cat_id, date="2026-07-30", amount=300)
    resp = client.get("/api/v1/expenses", params={"to": "2026-07-15"})
    data = resp.json()
    actual = f"{resp.status_code},len={len(data)}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-036', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 2
    assert all(d["date"] <= "2026-07-15" for d in data)
    dates = [d["date"] for d in data]
    assert dates == sorted(dates, reverse=True)


# ITC-037
def test_itc037_list_expenses_no_filter_sorted_desc(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id, date="2026-07-01", amount=100)
    _create_expense(client, cat_id, date="2026-07-20", amount=200)
    _create_expense(client, cat_id, date="2026-07-10", amount=300)
    resp = client.get("/api/v1/expenses")
    data = resp.json()
    dates = [d["date"] for d in data]
    actual = f"{resp.status_code},dates={dates}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-037', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 3
    assert dates == sorted(dates, reverse=True)


# ITC-038
def test_itc038_create_category_trims_whitespace(client):
    resp = client.post("/api/v1/categories", json={"name": "  Groceries  "})
    body = resp.json()
    actual = f"{resp.status_code},name={body['name']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-038', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert body["name"] == "Groceries"
    assert isinstance(body["id"], int)


# ITC-039
def test_itc039_monthly_report_year_above_range(client):
    resp = client.get("/api/v1/reports/monthly", params={"year": 2101, "month": 6})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-039', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# ITC-040
def test_itc040_patch_expense_change_category(client):
    cat1 = _create_category(client, "Food").json()["id"]
    cat2 = _create_category(client, "Transport").json()["id"]
    created = _create_expense(client, cat1, date="2026-07-15", amount=1000, memo="lunch").json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"category_id": cat2})
    body = resp.json()
    actual = f"{resp.status_code},category_id={body['category_id']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-040', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["category_id"] == cat2
    assert body["date"] == created["date"]
    assert body["amount"] == created["amount"]
    assert body["memo"] == created["memo"]


# ITC-041
def test_itc041_patch_expense_update_date_only(client):
    cat = _create_category(client, "PatchDateCat")
    cat_id = cat.json()["id"]
    created = client.post("/api/v1/expenses", json={
        "date": "2026-07-01", "amount": 500, "category_id": cat_id, "memo": "original"
    }).json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"date": "2026-08-15"})
    body = resp.json()
    actual = f"{resp.status_code},date={body['date']},amount={body['amount']},memo={body['memo']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-041', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["date"] == "2026-08-15"
    assert body["amount"] == 500
    assert body["memo"] == "original"


# ITC-042
def test_itc042_patch_expense_update_memo_only(client):
    cat = _create_category(client, "PatchMemoCat")
    cat_id = cat.json()["id"]
    created = client.post("/api/v1/expenses", json={
        "date": "2026-07-10", "amount": 800, "category_id": cat_id, "memo": "before"
    }).json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"memo": "after update"})
    body = resp.json()
    actual = f"{resp.status_code},memo={body['memo']},amount={body['amount']},date={body['date']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-042', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["memo"] == "after update"
    assert body["amount"] == 800
    assert body["date"] == "2026-07-10"


# ITC-043
def test_itc043_patch_expense_update_multiple_fields(client):
    cat = _create_category(client, "MultiPatchCat")
    cat_id = cat.json()["id"]
    created = client.post("/api/v1/expenses", json={
        "date": "2026-06-01", "amount": 100, "category_id": cat_id, "memo": "old"
    }).json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={
        "date": "2026-07-20", "amount": 9999, "memo": "new memo"
    })
    body = resp.json()
    actual = f"{resp.status_code},date={body['date']},amount={body['amount']},memo={body['memo']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-043', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["date"] == "2026-07-20"
    assert body["amount"] == 9999
    assert body["memo"] == "new memo"


# ITC-044
def test_itc044_patch_expense_invalid_amount_zero(client):
    cat = _create_category(client, "PatchInvCat")
    cat_id = cat.json()["id"]
    created = client.post("/api/v1/expenses", json={
        "date": "2026-07-01", "amount": 500, "category_id": cat_id
    }).json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"amount": 0})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-044', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# ITC-045
def test_itc045_patch_expense_memo_exceeds_max_length(client):
    cat = _create_category(client, "PatchMemoLenCat")
    cat_id = cat.json()["id"]
    created = client.post("/api/v1/expenses", json={
        "date": "2026-07-01", "amount": 300, "category_id": cat_id
    }).json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"memo": "x" * 201})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-045', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# ITC-046
def test_itc046_list_expenses_no_filters_returns_all_ordered(client):
    cat = _create_category(client, "ListAllCat")
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id, date="2026-07-01", amount=100)
    _create_expense(client, cat_id, date="2026-07-15", amount=200)
    _create_expense(client, cat_id, date="2026-07-10", amount=300)
    resp = client.get("/api/v1/expenses")
    data = resp.json()
    dates = [d["date"] for d in data]
    actual = f"{resp.status_code},len={len(data)},dates={dates}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-046', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) >= 3
    assert dates[0] == "2026-07-15"
    assert dates[1] == "2026-07-10"
    assert dates[2] == "2026-07-01"


# ITC-047
def test_itc047_list_expenses_from_date_filter_only(client):
    cat = _create_category(client, "FromOnlyCat")
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id, date="2026-06-01", amount=100)
    _create_expense(client, cat_id, date="2026-07-15", amount=200)
    _create_expense(client, cat_id, date="2026-08-01", amount=300)
    resp = client.get("/api/v1/expenses", params={"from": "2026-07-01"})
    data = resp.json()
    actual = f"{resp.status_code},len={len(data)}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-047', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 2
    assert all(d["date"] >= "2026-07-01" for d in data)
    assert data[0]["date"] == "2026-08-01"


# ITC-048
def test_itc048_list_expenses_to_date_filter_only(client):
    cat = _create_category(client, "ToOnlyCat")
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id, date="2026-06-01", amount=100)
    _create_expense(client, cat_id, date="2026-07-15", amount=200)
    _create_expense(client, cat_id, date="2026-08-01", amount=300)
    resp = client.get("/api/v1/expenses", params={"to": "2026-07-15"})
    data = resp.json()
    actual = f"{resp.status_code},len={len(data)}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-048', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 2
    assert all(d["date"] <= "2026-07-15" for d in data)
    assert data[0]["date"] == "2026-07-15"


# ITC-049
def test_itc049_monthly_report_year_above_valid_range(client):
    resp = client.get("/api/v1/reports/monthly", params={"year": 2101, "month": 6})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-049', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# ITC-050
def test_itc050_health_check_returns_ok(client):
    resp = client.get("/health")
    body = resp.json()
    actual = f"{resp.status_code},status={body['status']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'ITC-050', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body == {"status": "ok"}

"""Test cases TC-001 through TC-050."""

import json


def _create_category(client, name="Food"):
    return client.post("/api/v1/categories", json={"name": name})


def _create_expense(client, category_id, date="2026-07-15", amount=1000, memo="lunch"):
    return client.post(
        "/api/v1/expenses",
        json={"date": date, "amount": amount, "category_id": category_id, "memo": memo},
    )


# TC-001 | TP-001
def test_tc001_create_expense_valid_all_fields(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    resp = _create_expense(client, cat_id, date="2026-07-15", amount=1500, memo="dinner")
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-001', 'actual': str(actual)}))
    assert actual == 201
    body = resp.json()
    assert isinstance(body["id"], int)
    assert body["date"] == "2026-07-15"
    assert body["amount"] == 1500
    assert body["category_id"] == cat_id
    assert body["memo"] == "dinner"
    assert "created_at" in body


# TC-002 | TP-002
def test_tc002_create_expense_invalid_amount_zero_and_negative(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    resp_zero = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 0, "category_id": cat_id})
    resp_neg = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": -100, "category_id": cat_id})
    actual = f"{resp_zero.status_code},{resp_neg.status_code}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-002', 'actual': str(actual)}))
    assert resp_zero.status_code == 400
    assert resp_zero.json()["error"]["code"] == "VALIDATION_ERROR"
    assert resp_neg.status_code == 400
    assert resp_neg.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-003 | TP-003
def test_tc003_create_expense_nonexistent_category(client):
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 500, "category_id": 9999})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-003', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# TC-004 | TP-004
def test_tc004_list_expenses_date_range_filter(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id, date="2026-07-01", amount=100)
    _create_expense(client, cat_id, date="2026-07-10", amount=200)
    _create_expense(client, cat_id, date="2026-07-20", amount=300)
    _create_expense(client, cat_id, date="2026-07-31", amount=400)
    resp = client.get("/api/v1/expenses", params={"from": "2026-07-05", "to": "2026-07-25"})
    data = resp.json()
    actual = f"{resp.status_code},len={len(data)},dates={[d['date'] for d in data]}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-004', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 2
    assert data[0]["date"] == "2026-07-20"
    assert data[1]["date"] == "2026-07-10"


# TC-005 | TP-005
def test_tc005_patch_expense_amount_only(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id, date="2026-07-15", amount=1000, memo="lunch").json()
    expense_id = created["id"]
    resp = client.patch(f"/api/v1/expenses/{expense_id}", json={"amount": 2000})
    body = resp.json()
    actual = f"{resp.status_code},amount={body['amount']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-005', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["amount"] == 2000
    assert body["date"] == created["date"]
    assert body["category_id"] == created["category_id"]
    assert body["memo"] == created["memo"]


# TC-006 | TP-006
def test_tc006_delete_expense_then_get_returns_404(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id).json()
    expense_id = created["id"]
    del_resp = client.delete(f"/api/v1/expenses/{expense_id}")
    get_resp = client.get(f"/api/v1/expenses/{expense_id}")
    actual = f"del={del_resp.status_code},get={get_resp.status_code}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-006', 'actual': str(actual)}))
    assert del_resp.status_code == 204
    assert get_resp.status_code == 404
    assert get_resp.json()["error"]["code"] == "NOT_FOUND"


# TC-007 | TP-007
def test_tc007_duplicate_category_name_different_case(client):
    resp1 = _create_category(client, "Food")
    resp2 = _create_category(client, "food")
    actual = f"first={resp1.status_code},second={resp2.status_code}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-007', 'actual': str(actual)}))
    assert resp1.status_code == 201
    assert resp2.status_code == 409
    assert resp2.json()["error"]["code"] == "DUPLICATE_NAME"


# TC-008 | TP-008
def test_tc008_delete_category_in_use(client):
    cat = _create_category(client)
    cat_id = cat.json()["id"]
    _create_expense(client, cat_id)
    resp = client.delete(f"/api/v1/categories/{cat_id}")
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-008', 'actual': str(actual)}))
    assert actual == 409
    assert resp.json()["error"]["code"] == "CATEGORY_IN_USE"


# TC-009 | TP-009
def test_tc009_monthly_report_three_categories(client):
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
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-009', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["year"] == 2026
    assert body["month"] == 7
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


# TC-010 | TP-010
def test_tc010_monthly_report_no_expenses(client):
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 1})
    body = resp.json()
    actual = f"{resp.status_code},total={body['total']},count={body['count']},by_cat={body['by_category']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-010', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["year"] == 2026
    assert body["month"] == 1
    assert body["total"] == 0
    assert body["count"] == 0
    assert body["by_category"] == []


# TC-011
def test_tc011_get_expense_by_id(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    created = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 500, "category_id": cat_id, "memo": "snack"}).json()
    resp = client.get(f"/api/v1/expenses/{created['id']}")
    body = resp.json()
    actual = f"{resp.status_code},amount={body['amount']},memo={body['memo']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-011', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["id"] == created["id"]
    assert body["date"] == "2026-07-15"
    assert body["amount"] == 500
    assert body["category_id"] == cat_id
    assert body["memo"] == "snack"
    assert "created_at" in body


# TC-012
def test_tc012_patch_nonexistent_expense(client):
    resp = client.patch("/api/v1/expenses/9999", json={"amount": 500})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-012', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# TC-013
def test_tc013_delete_nonexistent_expense(client):
    resp = client.delete("/api/v1/expenses/9999")
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-013', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# TC-014
def test_tc014_create_expense_minimum_amount(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 1, "category_id": cat_id})
    body = resp.json()
    actual = f"{resp.status_code},amount={body['amount']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-014', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert body["amount"] == 1


# TC-015
def test_tc015_create_expense_memo_max_length(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    memo = "A" * 200
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 100, "category_id": cat_id, "memo": memo})
    body = resp.json()
    actual = f"{resp.status_code},memo_len={len(body['memo'])}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-015', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert len(body["memo"]) == 200


# TC-016
def test_tc016_create_expense_memo_over_max_length(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    memo = "A" * 201
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 100, "category_id": cat_id, "memo": memo})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-016', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-017
def test_tc017_list_categories_sorted(client):
    _create_category(client, "Utilities")
    _create_category(client, "Food")
    _create_category(client, "Transport")
    resp = client.get("/api/v1/categories")
    data = resp.json()
    names = [c["name"] for c in data]
    actual = f"{resp.status_code},names={names}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-017', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 3
    assert names == ["Food", "Transport", "Utilities"]


# TC-018
def test_tc018_create_category_name_max_length(client):
    name = "A" * 50
    resp = _create_category(client, name)
    body = resp.json()
    actual = f"{resp.status_code},name_len={len(body['name'])}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-018', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert len(body["name"]) == 50


# TC-019
def test_tc019_create_category_name_over_max_length(client):
    name = "A" * 51
    resp = _create_category(client, name)
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-019', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-020
def test_tc020_monthly_report_invalid_month(client):
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 13})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-020', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-021
def test_tc021_patch_nonexistent_expense(client):
    resp = client.patch("/api/v1/expenses/9999", json={"amount": 500})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-021', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# TC-022
def test_tc022_delete_nonexistent_expense(client):
    resp = client.delete("/api/v1/expenses/9999")
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-022', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# TC-023
def test_tc023_create_expense_memo_max_boundary(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    memo = "a" * 200
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 100, "category_id": cat_id, "memo": memo})
    body = resp.json()
    actual = f"{resp.status_code},memo_len={len(body['memo'])}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-023', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert len(body["memo"]) == 200
    assert "id" in body
    assert "created_at" in body


# TC-024
def test_tc024_create_expense_memo_exceeds_max(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    memo = "a" * 201
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 100, "category_id": cat_id, "memo": memo})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-024', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-025
def test_tc025_create_category_name_max_boundary(client):
    name = "A" * 50
    resp = client.post("/api/v1/categories", json={"name": name})
    body = resp.json()
    actual = f"{resp.status_code},name_len={len(body['name'])}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-025', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert len(body["name"]) == 50
    assert "id" in body


# TC-026
def test_tc026_create_category_name_exceeds_max(client):
    name = "A" * 51
    resp = client.post("/api/v1/categories", json={"name": name})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-026', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-027
def test_tc027_list_expenses_filter_by_category(client):
    cat1 = _create_category(client, "Food").json()["id"]
    cat2 = _create_category(client, "Transport").json()["id"]
    _create_expense(client, cat1, date="2026-07-10", amount=100)
    _create_expense(client, cat1, date="2026-07-11", amount=200)
    _create_expense(client, cat2, date="2026-07-12", amount=300)
    resp = client.get("/api/v1/expenses", params={"category_id": cat1})
    data = resp.json()
    actual = f"{resp.status_code},len={len(data)}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-027', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 2
    assert all(item["category_id"] == cat1 for item in data)


# TC-028
def test_tc028_monthly_report_invalid_month(client):
    resp0 = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 0})
    resp13 = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 13})
    actual = f"month0={resp0.status_code},month13={resp13.status_code}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-028', 'actual': str(actual)}))
    assert resp0.status_code == 400
    assert resp0.json()["error"]["code"] == "VALIDATION_ERROR"
    assert resp13.status_code == 400
    assert resp13.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-029
def test_tc029_patch_expense_nonexistent_category(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id).json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"category_id": 9999})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-029', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# TC-030
def test_tc030_delete_nonexistent_category(client):
    resp = client.delete("/api/v1/categories/9999")
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-030', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# TC-031
def test_tc031_create_category_valid(client):
    resp = client.post("/api/v1/categories", json={"name": "Transport"})
    body = resp.json()
    actual = f"{resp.status_code},name={body['name']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-031', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert isinstance(body["id"], int)
    assert body["name"] == "Transport"


# TC-032
def test_tc032_list_categories_sorted_by_name(client):
    _create_category(client, "Utilities")
    _create_category(client, "Food")
    _create_category(client, "Transport")
    resp = client.get("/api/v1/categories")
    data = resp.json()
    names = [c["name"] for c in data]
    actual = f"{resp.status_code},names={names}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-032', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 3
    assert names == ["Food", "Transport", "Utilities"]


# TC-033
def test_tc033_delete_category_not_in_use(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    del_resp = client.delete(f"/api/v1/categories/{cat_id}")
    get_resp = client.get("/api/v1/categories")
    actual = f"del={del_resp.status_code},remaining={len(get_resp.json())}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-033', 'actual': str(actual)}))
    assert del_resp.status_code == 204
    assert get_resp.json() == []


# TC-034
def test_tc034_create_expense_without_memo(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 500, "category_id": cat_id})
    body = resp.json()
    actual = f"{resp.status_code},memo={body.get('memo')}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-034', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert body.get("memo") is None
    assert "id" in body
    assert "created_at" in body


# TC-035
def test_tc035_create_expense_memo_exceeds_200_chars(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    memo = "a" * 201
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 1000, "category_id": cat_id, "memo": memo})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-035', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-036
def test_tc036_create_category_empty_name(client):
    resp = client.post("/api/v1/categories", json={"name": ""})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-036', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-037
def test_tc037_create_category_name_exceeds_50_chars(client):
    name = "A" * 51
    resp = client.post("/api/v1/categories", json={"name": name})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-037', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-038
def test_tc038_get_expense_by_id_valid(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    created = client.post("/api/v1/expenses", json={"date": "2026-07-20", "amount": 2500, "category_id": cat_id, "memo": "test"}).json()
    resp = client.get(f"/api/v1/expenses/{created['id']}")
    body = resp.json()
    actual = f"{resp.status_code},date={body['date']},amount={body['amount']},memo={body['memo']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-038', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert body["id"] == created["id"]
    assert body["date"] == "2026-07-20"
    assert body["amount"] == 2500
    assert body["memo"] == "test"
    assert "created_at" in body


# TC-039
def test_tc039_monthly_report_invalid_month_zero(client):
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 0})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-039', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-040
def test_tc040_create_expense_amount_minimum_boundary(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 1, "category_id": cat_id})
    body = resp.json()
    actual = f"{resp.status_code},amount={body['amount']}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-040', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert body["amount"] == 1
    assert "id" in body
    assert "created_at" in body


# TC-041
def test_tc041_create_expense_memo_exceeds_200_chars(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    memo = "A" * 201
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 500, "category_id": cat_id, "memo": memo})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-041', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-042
def test_tc042_create_category_name_exceeds_50_chars(client):
    name = "A" * 51
    resp = client.post("/api/v1/categories", json={"name": name})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-042', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-043
def test_tc043_create_category_whitespace_only_name(client):
    resp = client.post("/api/v1/categories", json={"name": "   "})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-043', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-044
def test_tc044_patch_nonexistent_expense(client):
    resp = client.patch("/api/v1/expenses/99999", json={"amount": 2000})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-044', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# TC-045
def test_tc045_list_expenses_filter_by_category_id(client):
    cat1 = _create_category(client, "Food").json()["id"]
    cat2 = _create_category(client, "Transport").json()["id"]
    _create_expense(client, cat1, date="2026-07-10", amount=100)
    _create_expense(client, cat1, date="2026-07-11", amount=200)
    _create_expense(client, cat2, date="2026-07-12", amount=300)
    resp = client.get("/api/v1/expenses", params={"category_id": cat1})
    data = resp.json()
    actual = f"{resp.status_code},len={len(data)}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-045', 'actual': str(actual)}))
    assert resp.status_code == 200
    assert len(data) == 2
    assert all(item["category_id"] == cat1 for item in data)


# TC-046
def test_tc046_create_expense_boundary_amount_one(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    resp = client.post("/api/v1/expenses", json={"date": "2026-07-15", "amount": 1, "category_id": cat_id})
    body = resp.json()
    actual = f"{resp.status_code},amount={body['amount']},memo={body.get('memo')}"
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-046', 'actual': str(actual)}))
    assert resp.status_code == 201
    assert body["amount"] == 1
    assert body.get("memo") is None
    assert "id" in body
    assert "created_at" in body


# TC-047
def test_tc047_monthly_report_year_below_range(client):
    resp = client.get("/api/v1/reports/monthly", params={"year": 1999, "month": 6})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-047', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-048
def test_tc048_monthly_report_month_zero(client):
    resp = client.get("/api/v1/reports/monthly", params={"year": 2026, "month": 0})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-048', 'actual': str(actual)}))
    assert actual == 400
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


# TC-049
def test_tc049_patch_expense_nonexistent_category(client):
    cat = _create_category(client, "Food")
    cat_id = cat.json()["id"]
    created = _create_expense(client, cat_id).json()
    resp = client.patch(f"/api/v1/expenses/{created['id']}", json={"category_id": 99999})
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-049', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


# TC-050
def test_tc050_delete_nonexistent_category(client):
    resp = client.delete("/api/v1/categories/99999")
    actual = resp.status_code
    print('XOLVIEN_RESULT:' + json.dumps({'tc_id': 'TC-050', 'actual': str(actual)}))
    assert actual == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"

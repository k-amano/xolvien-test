# Test Report (Integration Test)

| Item | Value |
|---|---|
| Executed At | 2026-08-02 12:11:23 UTC |
| Test Command | `python -m pytest -v 2>&1` |
| Result | ✅ PASS |
| Retries | 0 |
| Summary | 50 passed, 0 failed |

## Test Results

| TC-ID | Test Item | Expected | Actual | Result | Executed At |
|---|---|---|---|---|---|
| ITC-001 | Create expense with all valid fields and verify persistence via GET | POST → 201 with id, date, amount, category_id, memo, created_at; GET → 200 with identical fields | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-002 | Reject expense creation with amount=0 and amount=-100 | Both return 400 with error.code='VALIDATION_ERROR'; no expense records created | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-003 | Reject expense creation with non-existent category_id | 404 with error.code='NOT_FOUND' | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-004 | Filter expenses by from/to date range and verify newest-first ordering | 200 with 2 expenses; first has date 2026-07-20, second has date 2026-07-10 (descending order) | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-005 | Partial update expense amount only, other fields unchanged | 200 with amount=2000; date, category_id, memo unchanged from original | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-006 | Delete expense then verify it is no longer retrievable | DELETE → 204; GET → 404 with error.code='NOT_FOUND' | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-007 | Reject duplicate category name with different casing | First → 201; Second → 409 with error.code='DUPLICATE_NAME' | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-008 | Reject deletion of category referenced by an expense | 409 with error.code='CATEGORY_IN_USE' | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-009 | Monthly report with expenses across 3 categories returns correct totals and shares summing to ~100% | 200 with total=20000, count=4, by_category Food subtotal=8000 share=40.0, Transport subtotal=2000 share=10.0, Utilities subtotal=10000 share=50.0; shares sum to 100.0 | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-010 | Monthly report for month with no expenses returns zeros and empty by_category | 200 with year=2026, month=1, total=0, count=0, by_category=[] | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-011 | Health check returns 200 with status ok | 200; {"status": "ok"} | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-012 | Create expense with invalid date format (not ISO 8601) | 400; {"error": {"code": "VALIDATION_ERROR", "message": "..."}} | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-013 | Update only the date field of an existing expense | 200; date changed to 2026-08-01, amount/category_id/memo unchanged | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-014 | Update only the memo field of an existing expense | 200; memo changed to "updated memo", date/amount/category_id unchanged | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-015 | List all expenses without filters returns results sorted by date descending | 200; array of expenses ordered by date descending | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-016 | Monthly report with year above valid range (2101) | 400; {"error": {"code": "VALIDATION_ERROR", "message": "..."}} | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-017 | Create category with leading/trailing whitespace in name is trimmed and accepted | 201; name is "Groceries" (trimmed), id assigned | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-018 | Patch expense with invalid amount zero | 400; {"error": {"code": "VALIDATION_ERROR", "message": "..."}} | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-019 | List expenses with combined category_id and date range filters | 200; only expenses matching both category and date range, sorted by date descending | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-020 | Monthly report with missing required params (no year, no month) | 400; {"error": {"code": "VALIDATION_ERROR", "message": "..."}} | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-021 | Create expenses across two months and verify monthly report isolates to requested month only | 200; total=2000, count=1, by_category contains only the July expense | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-022 | Deleted expense is excluded from monthly summary report | 200; total=300, count=1 | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-023 | Cannot create expense referencing a deleted category | 404; error.code=NOT_FOUND | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-024 | Patching expense amount is reflected in monthly report totals | 200; total=5000, count=1 | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-025 | Patching expense date to different month moves it out of original month report | 200; total=0, count=0, by_category=[] | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-026 | Combining category_id and date range filters returns correct intersection | 200; array with 1 expense (amount=300, date=2026-07-25) | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-027 | Re-creating a category with the same name after deletion succeeds | 201; new category with name=Temp and a new id | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-028 | Patching expense category_id moves it to new category in filtered list | Food filter: 200 with empty array; Transport filter: 200 with 1 expense | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-029 | Deleting all expenses referencing a category then deleting the category succeeds | DELETE expense: 204; DELETE category: 204 | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-030 | Full lifecycle: health check, create category, create expense, list expenses returns the created expense | Health: 200 {status:ok}; Create category: 201; Create expense: 201; List: 200 with 1 expense matching all fields | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-031 | Health check endpoint returns ok status | 200 {"status": "ok"} | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-032 | Partial update expense date only, other fields unchanged | 200 updated expense with new date and original amount, category_id, memo preserved | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-033 | Partial update expense memo only, other fields unchanged | 200 updated expense with new memo and original date, amount, category_id preserved | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-034 | Partial update expense with invalid amount zero rejects | 400 {"error": {"code": "VALIDATION_ERROR", "message": "..."}} | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-035 | List expenses with only from filter returns expenses on or after date | 200 array containing only expenses with date >= 2026-07-15 in descending order | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-036 | List expenses with only to filter returns expenses on or before date | 200 array containing only expenses with date <= 2026-07-15 in descending order | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-037 | List all expenses no filters returns all records sorted by date descending | 200 array of all expenses sorted by date descending | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-038 | Create category with leading/trailing whitespace trims name and succeeds | 201 {"id": int, "name": "Groceries"} | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-039 | Monthly report year above valid range 2101 returns validation error | 400 {"error": {"code": "VALIDATION_ERROR", "message": "..."}} | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-040 | Partial update expense category_id to a different valid category | 200 updated expense with new category_id and original date, amount, memo preserved | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-041 | Patch expense - update date only | 200, date=2026-08-15, amount=500, memo=original unchanged | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-042 | Patch expense - update memo only | 200, memo=after update, amount=800, date=2026-07-10 unchanged | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-043 | Patch expense - update multiple fields at once | 200, date=2026-07-20, amount=9999, memo=new memo | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-044 | Patch expense - invalid amount zero | 400, error.code=VALIDATION_ERROR | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-045 | Patch expense - memo exceeds 200 characters | 400, error.code=VALIDATION_ERROR | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-046 | List expenses - no filters returns all expenses ordered by date desc then id desc | 200, results ordered [2026-07-15, 2026-07-10, 2026-07-01], len>=3 | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-047 | List expenses - from date filter only (no to) | 200, results include only dates >= 2026-07-01, excludes 2026-06-01 | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-048 | List expenses - to date filter only (no from) | 200, results include only dates <= 2026-07-15, excludes 2026-08-01 | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-049 | Monthly report - year above valid range (2101) | 400, error.code=VALIDATION_ERROR | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |
| ITC-050 | Health check endpoint returns ok | 200, {"status":"ok"} | — | ✅ PASSED | 2026-08-02 12:11:23 UTC |

## Test Execution Log

```
te_expense_valid_fields_and_verify_persistence PASSED [ 51%]
tests/test_integration.py::test_itc002_create_expense_invalid_amount_zero_and_negative PASSED [ 52%]
tests/test_integration.py::test_itc003_create_expense_nonexistent_category PASSED [ 53%]
tests/test_integration.py::test_itc004_list_expenses_date_range_filter_newest_first PASSED [ 54%]
tests/test_integration.py::test_itc005_patch_expense_amount_only_others_unchanged PASSED [ 55%]
tests/test_integration.py::test_itc006_delete_expense_then_get_returns_404 PASSED [ 56%]
tests/test_integration.py::test_itc007_duplicate_category_name_different_case PASSED [ 57%]
tests/test_integration.py::test_itc008_delete_category_in_use_by_expense PASSED [ 58%]
tests/test_integration.py::test_itc009_monthly_report_three_categories_correct_aggregation PASSED [ 59%]
tests/test_integration.py::test_itc010_monthly_report_no_expenses_returns_zeros PASSED [ 60%]
tests/test_integration.py::test_itc011_health_check_returns_ok PASSED    [ 61%]
tests/test_integration.py::test_itc012_create_expense_invalid_date_format PASSED [ 62%]
tests/test_integration.py::test_itc013_patch_expense_date_only PASSED    [ 63%]
tests/test_integration.py::test_itc014_patch_expense_memo_only PASSED    [ 64%]
tests/test_integration.py::test_itc015_list_expenses_no_filter_sorted_desc PASSED [ 65%]
tests/test_integration.py::test_itc016_monthly_report_year_above_range PASSED [ 66%]
tests/test_integration.py::test_itc017_create_category_name_whitespace_trimmed PASSED [ 67%]
tests/test_integration.py::test_itc018_patch_expense_invalid_amount_zero PASSED [ 68%]
tests/test_integration.py::test_itc019_list_expenses_combined_category_and_date_filter PASSED [ 69%]
tests/test_integration.py::test_itc020_monthly_report_missing_params PASSED [ 70%]
tests/test_integration.py::test_itc021_monthly_report_isolates_single_month PASSED [ 71%]
tests/test_integration.py::test_itc022_deleted_expense_excluded_from_report PASSED [ 72%]
tests/test_integration.py::test_itc023_create_expense_with_deleted_category_fails PASSED [ 73%]
tests/test_integration.py::test_itc024_patched_amount_reflected_in_report PASSED [ 74%]
tests/test_integration.py::test_itc025_patch_date_moves_expense_out_of_month_report PASSED [ 75%]
tests/test_integration.py::test_itc026_list_expenses_combined_category_and_date_filter PASSED [ 76%]
tests/test_integration.py::test_itc027_recreate_category_after_delete PASSED [ 77%]
tests/test_integration.py::test_itc028_patch_category_moves_expense_in_filtered_list PASSED [ 78%]
tests/test_integration.py::test_itc029_delete_expenses_then_delete_category_succeeds PASSED [ 79%]
tests/test_integration.py::test_itc030_full_lifecycle_health_create_list PASSED [ 80%]
tests/test_integration.py::test_itc031_health_check_returns_ok PASSED    [ 81%]
tests/test_integration.py::test_itc032_patch_expense_date_only PASSED    [ 82%]
tests/test_integration.py::test_itc033_patch_expense_memo_only PASSED    [ 83%]
tests/test_integration.py::test_itc034_patch_expense_invalid_amount_zero PASSED [ 84%]
tests/test_integration.py::test_itc035_list_expenses_from_filter_only PASSED [ 85%]
tests/test_integration.py::test_itc036_list_expenses_to_filter_only PASSED [ 86%]
tests/test_integration.py::test_itc037_list_expenses_no_filter_sorted_desc PASSED [ 87%]
tests/test_integration.py::test_itc038_create_category_trims_whitespace PASSED [ 88%]
tests/test_integration.py::test_itc039_monthly_report_year_above_range PASSED [ 89%]
tests/test_integration.py::test_itc040_patch_expense_change_category PASSED [ 90%]
tests/test_integration.py::test_itc041_patch_expense_update_date_only PASSED [ 91%]
tests/test_integration.py::test_itc042_patch_expense_update_memo_only PASSED [ 92%]
tests/test_integration.py::test_itc043_patch_expense_update_multiple_fields PASSED [ 93%]
tests/test_integration.py::test_itc044_patch_expense_invalid_amount_zero PASSED [ 94%]
tests/test_integration.py::test_itc045_patch_expense_memo_exceeds_max_length PASSED [ 95%]
tests/test_integration.py::test_itc046_list_expenses_no_filters_returns_all_ordered PASSED [ 96%]
tests/test_integration.py::test_itc047_list_expenses_from_date_filter_only PASSED [ 97%]
tests/test_integration.py::test_itc048_list_expenses_to_date_filter_only PASSED [ 98%]
tests/test_integration.py::test_itc049_monthly_report_year_above_valid_range PASSED [ 99%]
tests/test_integration.py::test_itc050_health_check_returns_ok PASSED    [100%]

=============================== warnings summary ===============================
../../home/xolvien/.local/lib/python3.11/site-packages/fastapi/testclient.py:1
  /home/xolvien/.local/lib/python3.11/site-packages/fastapi/testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 100 passed, 1 warning in 1.85s ========================
```

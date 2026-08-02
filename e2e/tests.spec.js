const { test, expect } = require('@playwright/test');

// Helper: direct API calls
const BASE = 'http://localhost:8000';

async function apiPost(request, path, body) {
  const res = await request.post(`${BASE}${path}`, { data: body });
  const status = res.status();
  let json = null;
  try { json = await res.json(); } catch(e) {}
  return { status, json };
}

async function apiGet(request, path) {
  const res = await request.get(`${BASE}${path}`);
  const status = res.status();
  let json = null;
  try { json = await res.json(); } catch(e) {}
  return { status, json };
}

async function apiPatch(request, path, body) {
  const res = await request.patch(`${BASE}${path}`, { data: body });
  const status = res.status();
  let json = null;
  try { json = await res.json(); } catch(e) {}
  return { status, json };
}

async function apiDelete(request, path) {
  const res = await request.delete(`${BASE}${path}`);
  const status = res.status();
  let json = null;
  try { json = await res.json(); } catch(e) {}
  return { status, json };
}

async function resetViaAPI(request) {
  const expRes = await apiGet(request, '/api/v1/expenses');
  if (expRes.json && Array.isArray(expRes.json)) {
    for (const exp of expRes.json) {
      await apiDelete(request, `/api/v1/expenses/${exp.id}`);
    }
  }
  const catRes = await apiGet(request, '/api/v1/categories');
  if (catRes.json && Array.isArray(catRes.json)) {
    for (const cat of catRes.json) {
      await apiDelete(request, `/api/v1/categories/${cat.id}`);
    }
  }
}

test.beforeEach(async ({ request }) => {
  await resetViaAPI(request);
});

// E2E-001: Create a new category with valid name
test('test_e2e001_create_category_valid', async ({ request }) => {
  const res = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-001', actual: String(JSON.stringify({code: res.status, body: res.json}))}));

  expect(res.status).toBe(201);
  expect(res.json).toHaveProperty('id');
  expect(typeof res.json.id).toBe('number');
  expect(res.json.name).toBe('Food');
});

// E2E-002: List categories sorted alphabetically
test('test_e2e002_list_categories_sorted', async ({ request }) => {
  await apiPost(request, '/api/v1/categories', { name: 'Transport' });
  await apiPost(request, '/api/v1/categories', { name: 'Food' });
  await apiPost(request, '/api/v1/categories', { name: 'Bills' });

  const res = await apiGet(request, '/api/v1/categories');
  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-002', actual: String(JSON.stringify(res.json))}));

  expect(res.status).toBe(200);
  expect(res.json).toHaveLength(3);
  expect(res.json[0].name).toBe('Bills');
  expect(res.json[1].name).toBe('Food');
  expect(res.json[2].name).toBe('Transport');
});

// E2E-003: Reject duplicate category name with different casing
test('test_e2e003_create_category_duplicate_case_insensitive', async ({ request }) => {
  await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const res = await apiPost(request, '/api/v1/categories', { name: 'FOOD' });

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-003', actual: String(JSON.stringify({code: res.status, body: res.json}))}));

  expect(res.status).toBe(409);
  expect(res.json.error.code).toBe('DUPLICATE_NAME');
  expect(typeof res.json.error.message).toBe('string');
});

// E2E-004: Create a new expense with all valid fields
test('test_e2e004_create_expense_valid', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const catId = catRes.json.id;

  const res = await apiPost(request, '/api/v1/expenses', { date: '2025-07-15', amount: 2500, category_id: catId, memo: 'Lunch' });

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-004', actual: String(JSON.stringify({code: res.status, body: res.json}))}));

  expect(res.status).toBe(201);
  expect(typeof res.json.id).toBe('number');
  expect(res.json.date).toBe('2025-07-15');
  expect(res.json.amount).toBe(2500);
  expect(res.json.category_id).toBe(catId);
  expect(res.json.memo).toBe('Lunch');
  expect(res.json).toHaveProperty('created_at');
});

// E2E-005: Reject expense with amount zero and negative amount
test('test_e2e005_create_expense_invalid_amount', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const catId = catRes.json.id;

  const res0 = await apiPost(request, '/api/v1/expenses', { date: '2025-07-15', amount: 0, category_id: catId });
  const resNeg = await apiPost(request, '/api/v1/expenses', { date: '2025-07-15', amount: -100, category_id: catId });

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-005', actual: String(JSON.stringify({status0: res0.status, statusNeg: resNeg.status}))}));

  expect(res0.status).toBe(400);
  expect(res0.json.error.code).toBe('VALIDATION_ERROR');
  expect(resNeg.status).toBe(400);
  expect(resNeg.json.error.code).toBe('VALIDATION_ERROR');
});

// E2E-006: Reject expense with non-existent category_id
test('test_e2e006_create_expense_nonexistent_category', async ({ request }) => {
  const res = await apiPost(request, '/api/v1/expenses', { date: '2025-07-15', amount: 1000, category_id: 9999 });

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-006', actual: String(JSON.stringify({code: res.status, body: res.json}))}));

  expect(res.status).toBe(404);
  expect(res.json.error.code).toBe('NOT_FOUND');
});

// E2E-007: Filter expenses by date range and verify newest-first order
test('test_e2e007_list_expenses_date_range_sorted', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const catId = catRes.json.id;

  await apiPost(request, '/api/v1/expenses', { date: '2025-06-01', amount: 100, category_id: catId });
  await apiPost(request, '/api/v1/expenses', { date: '2025-07-15', amount: 200, category_id: catId });
  await apiPost(request, '/api/v1/expenses', { date: '2025-08-20', amount: 300, category_id: catId });

  const res = await apiGet(request, '/api/v1/expenses?from=2025-06-01&to=2025-07-31');

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-007', actual: String(JSON.stringify(res.json))}));

  expect(res.status).toBe(200);
  expect(res.json).toHaveLength(2);
  expect(res.json[0].date).toBe('2025-07-15');
  expect(res.json[1].date).toBe('2025-06-01');
});

// E2E-008: Partial update expense amount only leaves other fields unchanged
test('test_e2e008_patch_expense_amount_only', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const catId = catRes.json.id;
  const expRes = await apiPost(request, '/api/v1/expenses', { date: '2025-07-15', amount: 500, category_id: catId, memo: 'Dinner' });
  const expId = expRes.json.id;

  const res = await apiPatch(request, `/api/v1/expenses/${expId}`, { amount: 750 });

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-008', actual: String(JSON.stringify(res.json))}));

  expect(res.status).toBe(200);
  expect(res.json.amount).toBe(750);
  expect(res.json.date).toBe('2025-07-15');
  expect(res.json.category_id).toBe(catId);
  expect(res.json.memo).toBe('Dinner');
});

// E2E-009: Delete expense then verify it returns 404 on GET
test('test_e2e009_delete_then_get_expense', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const catId = catRes.json.id;
  const expRes = await apiPost(request, '/api/v1/expenses', { date: '2025-07-15', amount: 300, category_id: catId });
  const expId = expRes.json.id;

  const delRes = await apiDelete(request, `/api/v1/expenses/${expId}`);
  const getRes = await apiGet(request, `/api/v1/expenses/${expId}`);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-009', actual: String(JSON.stringify({deleteStatus: delRes.status, getStatus: getRes.status}))}));

  expect(delRes.status).toBe(204);
  expect(getRes.status).toBe(404);
  expect(getRes.json.error.code).toBe('NOT_FOUND');
});

// E2E-010: Monthly report with expenses across 3 categories
test('test_e2e010_monthly_report_three_categories', async ({ request }) => {
  const cat1 = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const cat2 = await apiPost(request, '/api/v1/categories', { name: 'Transport' });
  const cat3 = await apiPost(request, '/api/v1/categories', { name: 'Bills' });

  await apiPost(request, '/api/v1/expenses', { date: '2025-07-10', amount: 5000, category_id: cat1.json.id });
  await apiPost(request, '/api/v1/expenses', { date: '2025-07-12', amount: 3000, category_id: cat2.json.id });
  await apiPost(request, '/api/v1/expenses', { date: '2025-07-20', amount: 2000, category_id: cat3.json.id });

  const res = await apiGet(request, '/api/v1/reports/monthly?year=2025&month=7');

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-010', actual: String(JSON.stringify(res.json))}));

  expect(res.status).toBe(200);
  expect(res.json.year).toBe(2025);
  expect(res.json.month).toBe(7);
  expect(res.json.total).toBe(10000);
  expect(res.json.count).toBe(3);
  expect(res.json.by_category).toHaveLength(3);

  const foodCat = res.json.by_category.find(c => c.category === 'Food');
  const transportCat = res.json.by_category.find(c => c.category === 'Transport');
  const billsCat = res.json.by_category.find(c => c.category === 'Bills');
  expect(foodCat.subtotal).toBe(5000);
  expect(foodCat.share).toBe(50.0);
  expect(transportCat.subtotal).toBe(3000);
  expect(transportCat.share).toBe(30.0);
  expect(billsCat.subtotal).toBe(2000);
  expect(billsCat.share).toBe(20.0);

  const totalShare = res.json.by_category.reduce((sum, c) => sum + c.share, 0);
  expect(totalShare).toBeCloseTo(100.0, 0);
});

// E2E-011: Create category, create expense, list expenses returns created expense
test('test_e2e011_full_create_category_expense_and_list', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Groceries' });
  expect(catRes.status).toBe(201);
  expect(catRes.json.name).toBe('Groceries');
  const catId = catRes.json.id;

  const expRes = await apiPost(request, '/api/v1/expenses', { date: '2026-08-01', amount: 2500, category_id: catId, memo: 'Weekly shopping' });
  expect(expRes.status).toBe(201);
  expect(expRes.json.amount).toBe(2500);
  expect(expRes.json.category_id).toBe(catId);
  expect(expRes.json.memo).toBe('Weekly shopping');

  const listRes = await apiGet(request, '/api/v1/expenses');
  expect(listRes.status).toBe(200);
  const found = listRes.json.find(e => e.id === expRes.json.id);
  expect(found).toBeTruthy();

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-011', actual: String(JSON.stringify({catId, expId: expRes.json.id}))}));
});

// E2E-012: Create expense then partial update memo and verify via GET
test('test_e2e012_create_expense_patch_memo_verify_get', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Transport' });
  const catId = catRes.json.id;
  const expRes = await apiPost(request, '/api/v1/expenses', { date: '2026-07-15', amount: 1200, category_id: catId });
  const expId = expRes.json.id;

  const patchRes = await apiPatch(request, `/api/v1/expenses/${expId}`, { memo: 'Bus fare' });
  expect(patchRes.status).toBe(200);
  expect(patchRes.json.memo).toBe('Bus fare');
  expect(patchRes.json.amount).toBe(1200);
  expect(patchRes.json.date).toBe('2026-07-15');

  const getRes = await apiGet(request, `/api/v1/expenses/${expId}`);
  expect(getRes.status).toBe(200);
  expect(getRes.json.memo).toBe('Bus fare');
  expect(getRes.json.amount).toBe(1200);
  expect(getRes.json.date).toBe('2026-07-15');

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-012', actual: String(JSON.stringify(getRes.json))}));
});

// E2E-013: Create category, delete it, verify removed from list
test('test_e2e013_create_delete_category_verify_removed', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'TempCategory' });
  expect(catRes.status).toBe(201);
  const catId = catRes.json.id;

  const delRes = await apiDelete(request, `/api/v1/categories/${catId}`);
  expect(delRes.status).toBe(204);

  const listRes = await apiGet(request, '/api/v1/categories');
  expect(listRes.status).toBe(200);
  const found = listRes.json.find(c => c.name === 'TempCategory');
  expect(found).toBeUndefined();

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-013', actual: String(JSON.stringify(listRes.json))}));
});

// E2E-014: List expenses with date range filter returns only matching records sorted descending
test('test_e2e014_list_expenses_date_range_filter_boundaries', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const catId = catRes.json.id;

  await apiPost(request, '/api/v1/expenses', { date: '2026-06-01', amount: 500, category_id: catId });
  await apiPost(request, '/api/v1/expenses', { date: '2026-07-10', amount: 800, category_id: catId });
  await apiPost(request, '/api/v1/expenses', { date: '2026-08-01', amount: 300, category_id: catId });

  const listRes = await apiGet(request, '/api/v1/expenses?from=2026-06-15&to=2026-07-31');
  expect(listRes.status).toBe(200);
  expect(listRes.json).toHaveLength(1);
  expect(listRes.json[0].amount).toBe(800);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-014', actual: String(JSON.stringify(listRes.json))}));
});

// E2E-015: Deleted expense is excluded from monthly report
test('test_e2e015_deleted_expense_excluded_from_monthly_report', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Utilities' });
  const catId = catRes.json.id;

  const exp1 = await apiPost(request, '/api/v1/expenses', { date: '2026-07-01', amount: 3000, category_id: catId });
  const exp2 = await apiPost(request, '/api/v1/expenses', { date: '2026-07-15', amount: 2000, category_id: catId });

  await apiDelete(request, `/api/v1/expenses/${exp2.json.id}`);

  const reportRes = await apiGet(request, '/api/v1/reports/monthly?year=2026&month=7');
  expect(reportRes.status).toBe(200);
  expect(reportRes.json.total).toBe(3000);
  expect(reportRes.json.count).toBe(1);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-015', actual: String(JSON.stringify(reportRes.json))}));
});

// E2E-016: Cannot delete category that has expenses referencing it
test('test_e2e016_delete_category_in_use_returns_409', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Entertainment' });
  const catId = catRes.json.id;

  await apiPost(request, '/api/v1/expenses', { date: '2026-07-20', amount: 1500, category_id: catId });

  const delRes = await apiDelete(request, `/api/v1/categories/${catId}`);
  expect(delRes.status).toBe(409);
  expect(delRes.json.error.code).toBe('CATEGORY_IN_USE');

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-016', actual: String(JSON.stringify(delRes.json))}));
});

// E2E-017: Patching expense amount is reflected in monthly report
test('test_e2e017_patch_amount_reflected_in_monthly_report', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Health' });
  const catId = catRes.json.id;

  const expRes = await apiPost(request, '/api/v1/expenses', { date: '2026-07-05', amount: 1000, category_id: catId });
  const expId = expRes.json.id;

  const report1 = await apiGet(request, '/api/v1/reports/monthly?year=2026&month=7');
  expect(report1.json.total).toBe(1000);
  expect(report1.json.count).toBe(1);

  await apiPatch(request, `/api/v1/expenses/${expId}`, { amount: 5000 });

  const report2 = await apiGet(request, '/api/v1/reports/monthly?year=2026&month=7');
  expect(report2.json.total).toBe(5000);
  expect(report2.json.count).toBe(1);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-017', actual: String(JSON.stringify(report2.json))}));
});

// E2E-018: Case-insensitive duplicate category name rejected
test('test_e2e018_duplicate_category_case_insensitive_rejected', async ({ request }) => {
  const res1 = await apiPost(request, '/api/v1/categories', { name: 'Travel' });
  expect(res1.status).toBe(201);

  const res2 = await apiPost(request, '/api/v1/categories', { name: 'travel' });
  expect(res2.status).toBe(409);
  expect(res2.json.error.code).toBe('DUPLICATE_NAME');

  const res3 = await apiPost(request, '/api/v1/categories', { name: 'TRAVEL' });
  expect(res3.status).toBe(409);
  expect(res3.json.error.code).toBe('DUPLICATE_NAME');

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-018', actual: String(JSON.stringify({s1: res1.status, s2: res2.status, s3: res3.status}))}));
});

// E2E-019: Monthly report with multiple categories shows correct per-category breakdown and share percentages
test('test_e2e019_monthly_report_multi_category_breakdown_shares', async ({ request }) => {
  const rentCat = await apiPost(request, '/api/v1/categories', { name: 'Rent' });
  const mealsCat = await apiPost(request, '/api/v1/categories', { name: 'Meals' });

  await apiPost(request, '/api/v1/expenses', { date: '2026-08-01', amount: 70000, category_id: rentCat.json.id });
  await apiPost(request, '/api/v1/expenses', { date: '2026-08-10', amount: 30000, category_id: mealsCat.json.id });

  const report = await apiGet(request, '/api/v1/reports/monthly?year=2026&month=8');
  expect(report.status).toBe(200);
  expect(report.json.total).toBe(100000);
  expect(report.json.count).toBe(2);

  const rentEntry = report.json.by_category.find(c => c.category === 'Rent');
  const mealsEntry = report.json.by_category.find(c => c.category === 'Meals');
  expect(rentEntry.subtotal).toBe(70000);
  expect(rentEntry.share).toBe(70.0);
  expect(mealsEntry.subtotal).toBe(30000);
  expect(mealsEntry.share).toBe(30.0);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-019', actual: String(JSON.stringify(report.json))}));
});

// E2E-020: Patch expense category_id moves it to different category filter results
test('test_e2e020_patch_category_moves_expense_in_filtered_list', async ({ request }) => {
  const officeCat = await apiPost(request, '/api/v1/categories', { name: 'Office' });
  const personalCat = await apiPost(request, '/api/v1/categories', { name: 'Personal' });

  const exp = await apiPost(request, '/api/v1/expenses', { date: '2026-08-01', amount: 4000, category_id: officeCat.json.id, memo: 'Stationery' });

  await apiPatch(request, `/api/v1/expenses/${exp.json.id}`, { category_id: personalCat.json.id });

  const officeList = await apiGet(request, `/api/v1/expenses?category_id=${officeCat.json.id}`);
  expect(officeList.status).toBe(200);
  expect(officeList.json).toHaveLength(0);

  const personalList = await apiGet(request, `/api/v1/expenses?category_id=${personalCat.json.id}`);
  expect(personalList.status).toBe(200);
  expect(personalList.json).toHaveLength(1);
  expect(personalList.json[0].amount).toBe(4000);
  expect(personalList.json[0].memo).toBe('Stationery');

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-020', actual: String(JSON.stringify({office: officeList.json, personal: personalList.json}))}));
});

// E2E-021: Create category then create expense referencing it
test('test_e2e021_create_category_then_expense_and_verify_get', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Transport' });
  expect(catRes.status).toBe(201);
  expect(catRes.json.name).toBe('Transport');
  const catId = catRes.json.id;

  const expRes = await apiPost(request, '/api/v1/expenses', { date: '2026-08-01', amount: 2500, category_id: catId, memo: 'taxi ride' });
  expect(expRes.status).toBe(201);
  expect(expRes.json.category_id).toBe(catId);
  expect(expRes.json.amount).toBe(2500);
  expect(expRes.json.memo).toBe('taxi ride');

  const getRes = await apiGet(request, `/api/v1/expenses/${expRes.json.id}`);
  expect(getRes.status).toBe(200);
  expect(getRes.json).toHaveProperty('created_at');
  expect(getRes.json.amount).toBe(2500);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-021', actual: String(JSON.stringify(getRes.json))}));
});

// E2E-022: Patch expense date moves it between monthly reports
test('test_e2e022_patch_date_moves_expense_between_monthly_reports', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const catId = catRes.json.id;

  const expRes = await apiPost(request, '/api/v1/expenses', { date: '2026-07-15', amount: 3000, category_id: catId });
  const expId = expRes.json.id;

  const julyReport1 = await apiGet(request, '/api/v1/reports/monthly?year=2026&month=7');
  expect(julyReport1.json.count).toBe(1);
  expect(julyReport1.json.total).toBe(3000);

  const patchRes = await apiPatch(request, `/api/v1/expenses/${expId}`, { date: '2026-08-15' });
  expect(patchRes.status).toBe(200);

  const julyReport2 = await apiGet(request, '/api/v1/reports/monthly?year=2026&month=7');
  expect(julyReport2.json.count).toBe(0);
  expect(julyReport2.json.total).toBe(0);

  const augReport = await apiGet(request, '/api/v1/reports/monthly?year=2026&month=8');
  expect(augReport.json.count).toBe(1);
  expect(augReport.json.total).toBe(3000);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-022', actual: String(JSON.stringify({july: julyReport2.json, aug: augReport.json}))}));
});

// E2E-023: Delete all expenses then delete category succeeds
test('test_e2e023_delete_expenses_then_delete_category', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Gym' });
  const catId = catRes.json.id;

  const exp1 = await apiPost(request, '/api/v1/expenses', { date: '2026-07-01', amount: 5000, category_id: catId });
  const exp2 = await apiPost(request, '/api/v1/expenses', { date: '2026-07-02', amount: 3000, category_id: catId });

  // Try delete category while in use
  const delCatFail = await apiDelete(request, `/api/v1/categories/${catId}`);
  expect(delCatFail.status).toBe(409);
  expect(delCatFail.json.error.code).toBe('CATEGORY_IN_USE');

  // Delete expenses
  const del1 = await apiDelete(request, `/api/v1/expenses/${exp1.json.id}`);
  expect(del1.status).toBe(204);
  const del2 = await apiDelete(request, `/api/v1/expenses/${exp2.json.id}`);
  expect(del2.status).toBe(204);

  // Now delete category succeeds
  const delCatOk = await apiDelete(request, `/api/v1/categories/${catId}`);
  expect(delCatOk.status).toBe(204);

  // Verify removed
  const listRes = await apiGet(request, '/api/v1/categories');
  const found = listRes.json.find(c => c.name === 'Gym');
  expect(found).toBeUndefined();

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-023', actual: String(JSON.stringify(listRes.json))}));
});

// E2E-024: Monthly report aggregates multiple categories with correct percentages
test('test_e2e024_monthly_report_multi_category_percentage', async ({ request }) => {
  const foodCat = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const rentCat = await apiPost(request, '/api/v1/categories', { name: 'Rent' });
  const funCat = await apiPost(request, '/api/v1/categories', { name: 'Fun' });

  await apiPost(request, '/api/v1/expenses', { date: '2026-07-10', amount: 3000, category_id: foodCat.json.id });
  await apiPost(request, '/api/v1/expenses', { date: '2026-07-10', amount: 5000, category_id: rentCat.json.id });
  await apiPost(request, '/api/v1/expenses', { date: '2026-07-10', amount: 2000, category_id: funCat.json.id });

  const report = await apiGet(request, '/api/v1/reports/monthly?year=2026&month=7');
  expect(report.status).toBe(200);
  expect(report.json.year).toBe(2026);
  expect(report.json.month).toBe(7);
  expect(report.json.total).toBe(10000);
  expect(report.json.count).toBe(3);

  const food = report.json.by_category.find(c => c.category === 'Food');
  const rent = report.json.by_category.find(c => c.category === 'Rent');
  const fun = report.json.by_category.find(c => c.category === 'Fun');
  expect(food.subtotal).toBe(3000);
  expect(food.share).toBe(30.0);
  expect(rent.subtotal).toBe(5000);
  expect(rent.share).toBe(50.0);
  expect(fun.subtotal).toBe(2000);
  expect(fun.share).toBe(20.0);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-024', actual: String(JSON.stringify(report.json))}));
});

// E2E-025: Case-insensitive duplicate category name rejected
test('test_e2e025_duplicate_category_case_insensitive', async ({ request }) => {
  const res1 = await apiPost(request, '/api/v1/categories', { name: 'Travel' });
  expect(res1.status).toBe(201);

  const res2 = await apiPost(request, '/api/v1/categories', { name: 'travel' });
  expect(res2.status).toBe(409);
  expect(res2.json.error.code).toBe('DUPLICATE_NAME');

  const res3 = await apiPost(request, '/api/v1/categories', { name: 'TRAVEL' });
  expect(res3.status).toBe(409);
  expect(res3.json.error.code).toBe('DUPLICATE_NAME');

  const listRes = await apiGet(request, '/api/v1/categories');
  const travelEntries = listRes.json.filter(c => c.name.toLowerCase() === 'travel');
  expect(travelEntries).toHaveLength(1);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-025', actual: String(JSON.stringify(listRes.json))}));
});

// E2E-026: Patch expense category_id and verify list filter reflects change
test('test_e2e026_patch_category_id_reflects_in_filter', async ({ request }) => {
  const cat1 = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const cat2 = await apiPost(request, '/api/v1/categories', { name: 'Drink' });

  const exp = await apiPost(request, '/api/v1/expenses', { date: '2026-07-15', amount: 1000, category_id: cat1.json.id });

  // Verify initially in cat1
  const list1 = await apiGet(request, `/api/v1/expenses?category_id=${cat1.json.id}`);
  expect(list1.json).toHaveLength(1);

  // Patch to cat2
  const patchRes = await apiPatch(request, `/api/v1/expenses/${exp.json.id}`, { category_id: cat2.json.id });
  expect(patchRes.status).toBe(200);

  // Now cat1 should be empty
  const list1After = await apiGet(request, `/api/v1/expenses?category_id=${cat1.json.id}`);
  expect(list1After.json).toHaveLength(0);

  // Cat2 should have 1
  const list2After = await apiGet(request, `/api/v1/expenses?category_id=${cat2.json.id}`);
  expect(list2After.json).toHaveLength(1);
  expect(list2After.json[0].category_id).toBe(cat2.json.id);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-026', actual: String(JSON.stringify({cat1: list1After.json, cat2: list2After.json}))}));
});

// E2E-027: Date range filter boundaries are inclusive
test('test_e2e027_date_range_filter_inclusive_boundaries', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  const catId = catRes.json.id;

  await apiPost(request, '/api/v1/expenses', { date: '2026-07-01', amount: 100, category_id: catId });
  await apiPost(request, '/api/v1/expenses', { date: '2026-07-15', amount: 200, category_id: catId });
  await apiPost(request, '/api/v1/expenses', { date: '2026-07-31', amount: 300, category_id: catId });

  // Full range
  const fullRange = await apiGet(request, '/api/v1/expenses?from=2026-07-01&to=2026-07-31');
  expect(fullRange.json).toHaveLength(3);
  expect(fullRange.json[0].date).toBe('2026-07-31');

  // Single day - first
  const singleFirst = await apiGet(request, '/api/v1/expenses?from=2026-07-01&to=2026-07-01');
  expect(singleFirst.json).toHaveLength(1);
  expect(singleFirst.json[0].date).toBe('2026-07-01');

  // Single day - last
  const singleLast = await apiGet(request, '/api/v1/expenses?from=2026-07-31&to=2026-07-31');
  expect(singleLast.json).toHaveLength(1);
  expect(singleLast.json[0].date).toBe('2026-07-31');

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-027', actual: String(JSON.stringify({full: fullRange.json.length, first: singleFirst.json.length, last: singleLast.json.length}))}));
});

// E2E-028: Report for month with no expenses returns zeros
test('test_e2e028_monthly_report_empty_month_returns_zeros', async ({ request }) => {
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Food' });
  await apiPost(request, '/api/v1/expenses', { date: '2026-07-15', amount: 1000, category_id: catRes.json.id });

  const report = await apiGet(request, '/api/v1/reports/monthly?year=2026&month=3');
  expect(report.status).toBe(200);
  expect(report.json.year).toBe(2026);
  expect(report.json.month).toBe(3);
  expect(report.json.total).toBe(0);
  expect(report.json.count).toBe(0);
  expect(report.json.by_category).toHaveLength(0);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-028', actual: String(JSON.stringify(report.json))}));
});

// E2E-029: Chained 404 errors on non-existent resources
test('test_e2e029_not_found_errors_on_nonexistent_resources', async ({ request }) => {
  const getExp = await apiGet(request, '/api/v1/expenses/99999');
  expect(getExp.status).toBe(404);
  expect(getExp.json.error.code).toBe('NOT_FOUND');

  const patchExp = await apiPatch(request, '/api/v1/expenses/99999', { amount: 500 });
  expect(patchExp.status).toBe(404);
  expect(patchExp.json.error.code).toBe('NOT_FOUND');

  const delExp = await apiDelete(request, '/api/v1/expenses/99999');
  expect(delExp.status).toBe(404);
  expect(delExp.json.error.code).toBe('NOT_FOUND');

  const delCat = await apiDelete(request, '/api/v1/categories/99999');
  expect(delCat.status).toBe(404);
  expect(delCat.json.error.code).toBe('NOT_FOUND');

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-029', actual: String(JSON.stringify({getExp: getExp.status, patchExp: patchExp.status, delExp: delExp.status, delCat: delCat.status}))}));
});

// E2E-030: End-to-end CRUD lifecycle
test('test_e2e030_full_crud_lifecycle_health_create_read_update_delete', async ({ request }) => {
  // Health check
  const health = await apiGet(request, '/health');
  expect(health.status).toBe(200);
  expect(health.json.status).toBe('ok');

  // Create category
  const catRes = await apiPost(request, '/api/v1/categories', { name: 'Office' });
  expect(catRes.status).toBe(201);
  const catId = catRes.json.id;

  // Create expense
  const expRes = await apiPost(request, '/api/v1/expenses', { date: '2026-08-01', amount: 4500, category_id: catId, memo: 'supplies' });
  expect(expRes.status).toBe(201);
  const expId = expRes.json.id;

  // GET expense
  const getRes = await apiGet(request, `/api/v1/expenses/${expId}`);
  expect(getRes.status).toBe(200);
  expect(getRes.json.amount).toBe(4500);

  // PATCH expense
  const patchRes = await apiPatch(request, `/api/v1/expenses/${expId}`, { amount: 5000, memo: 'office supplies' });
  expect(patchRes.status).toBe(200);
  expect(patchRes.json.amount).toBe(5000);
  expect(patchRes.json.memo).toBe('office supplies');

  // Monthly report
  const report = await apiGet(request, '/api/v1/reports/monthly?year=2026&month=8');
  expect(report.json.total).toBe(5000);
  expect(report.json.count).toBe(1);

  // Delete expense
  const delExp = await apiDelete(request, `/api/v1/expenses/${expId}`);
  expect(delExp.status).toBe(204);

  // Delete category
  const delCat = await apiDelete(request, `/api/v1/categories/${catId}`);
  expect(delCat.status).toBe(204);

  // Final verification
  const finalExpenses = await apiGet(request, '/api/v1/expenses');
  expect(finalExpenses.json).toHaveLength(0);

  const finalCategories = await apiGet(request, '/api/v1/categories');
  expect(finalCategories.json).toHaveLength(0);

  console.log('XOLVIEN_RESULT:' + JSON.stringify({tc_id: 'E2E-030', actual: String(JSON.stringify({expCount: finalExpenses.json.length, catCount: finalCategories.json.length}))}));
});

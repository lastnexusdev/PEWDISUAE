# CoreJunkie Product Tracker (Working MVP)

This app is now a full working starter with:
- user registration + login,
- product catalog creation,
- per-user inventory tracking,
- run-out date forecasting from usage cadence,
- HTML UI and JSON API under a configurable base path.

## Configuration
Environment variables:

- `APP_BASE_URL` (default `http://localhost:8000`)
- `APP_BASE_PATH` (default `/app`)
- `DATABASE_URL` (default `sqlite:///./corejunkie.db`)
- `SECRET_KEY` (default `dev-secret-change-me`, override in production)

For production target domain/path:
- `APP_BASE_URL=https://corejunkie.com`
- `APP_BASE_PATH=/app`

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn corejunkie_app.main:app --reload
```

## Use the app
- Open UI: `http://localhost:8000/app/`
- Register: `http://localhost:8000/app/register`
- Login: `http://localhost:8000/app/login`
- Dashboard: `http://localhost:8000/app/dashboard`
- API docs: `http://localhost:8000/docs`

## Main flows implemented
1. Register/login user account.
2. Add product with size and unit.
3. Add inventory item with:
   - purchased date,
   - opened date,
   - cadence (`day` or `week`),
   - amount per use.
4. App computes `expected_run_out_at` automatically.

## JSON API examples
### Create user
```bash
curl -X POST http://localhost:8000/app/users \
  -H 'Content-Type: application/json' \
  -d '{"email":"you@example.com","display_name":"You","password":"supersecure"}'
```

### Create product
```bash
curl -X POST http://localhost:8000/app/products \
  -H 'Content-Type: application/json' \
  -d '{"name":"Botanic Hearth Peppermint Shampoo","category":"Hair","size_value":16,"size_unit":"fl_oz"}'
```

### Add inventory
```bash
curl -X POST http://localhost:8000/app/inventory \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id":1,
    "product_id":1,
    "purchased_at":"2026-03-30",
    "opened_at":"2026-03-31",
    "cadence_value":2,
    "cadence_unit":"day",
    "amount_per_use":0.5
  }'
```

# Product List Export → Web App Brainstorm

## Goal
Turn the current spreadsheet workflow into a web app where you can:
- Enter and update products over time.
- Store all data in a backend database.
- Search, filter, and list products on a front end.
- Support **multiple users** with private/product-level tracking.
- Track purchases, start dates, and expected run-out dates from frequency + package size.
- Track safety, cost efficiency, and product usage lifecycle.

## Recommended approach (best balance of speed + maintainability)

### Stack recommendation
- **Frontend:** Next.js (React) + TypeScript + Tailwind.
- **Backend API:** Next.js Route Handlers (or Nest/Express if you prefer separate services).
- **Database:** PostgreSQL.
- **ORM:** Prisma.
- **Auth:** Clerk/Auth0/Supabase Auth.
- **Hosting:** Vercel (frontend/API) + Neon/Supabase/RDS (Postgres).

Why this is likely best:
- Easy full-stack iteration from spreadsheet-era requirements.
- Strong support for filtering/search UIs and admin forms.
- Prisma gives safe schema migrations as your model evolves.


## Deployment/base URL requirement
- Primary production app path: `https://corejunkie.com/app`.
- Keep it configurable via environment variables so it can run on staging/dev too.
- Recommended config:
  - `APP_BASE_URL` (e.g., `https://corejunkie.com`)
  - `APP_BASE_PATH` (default `/app`)
  - `NEXT_PUBLIC_APP_BASE_PATH` for frontend routing/link generation

This avoids hard-coding the host/path while still supporting your target domain.

## Domain model from your workbook

### Core entities
1. **Product**
   - id
   - name
   - category_id (Hair, Body Wash, Lotion, Face, etc.)
   - type_id (Shampoo, Serum, Toner, etc.)
   - risk_level (Verified Safe, Unverified, etc.)
   - risk_flags (aloe/honey/almond, latex/shea/avocado)
   - botanical_density (Very High / High / Moderate / Low)
   - status (Best Match / Safe / etc.)
   - notes

2. **ProductVariant / Package**
   - id
   - product_id
   - cost
   - size_value
   - size_unit (fl_oz, count, etc.)
   - unit_cost (computed + stored)
   - source/vendor

3. **User**
   - id
   - email
   - display_name
   - role (admin, member, viewer)

4. **InventoryItem** (a user-owned product instance)
   - id
   - user_id
   - product_id
   - package_id
   - purchased_at
   - opened_at (start using)
   - quantity_purchased (default 1)
   - remaining_amount (computed/adjusted)
   - expected_run_out_at (computed)
   - status (sealed, active, low, finished)

5. **UsageLog**
   - id
   - inventory_item_id
   - used_at
   - amount_used
   - amount_unit
   - notes

6. **UsageProfile** (fallback when detailed logs are not entered daily)
   - id
   - inventory_item_id
   - cadence_value (e.g., 2)
   - cadence_unit (`day` | `week`)
   - estimated_amount_per_use
   - estimated_amount_unit

7. **Category**
   - id
   - name

8. **Tag / Concern (optional for flexibility)**
   - id
   - name (e.g., aloe, honey, almond, shea)
   - relation table product_tag with allowed/blocked/unknown state.

### Why normalize this way
- Supports simple listing today, but scalable for future analytics.
- Avoids repeating product details in every usage row.
- Lets you compare packages/prices per product.


## Run-out prediction logic (important for your requirement)

Track three key dates per user-owned inventory item:
1. `purchased_at`
2. `opened_at` (when started using)
3. `expected_run_out_at` (calculated)

### Simple estimation formula
- `uses_per_day` = convert cadence (`2/day` => 2, `2/week` => 2/7).
- `daily_consumption` = `uses_per_day * amount_per_use`.
- `days_to_empty` = `package_size / daily_consumption`.
- `expected_run_out_at` = `opened_at + days_to_empty`.

### Improve accuracy over time
- Recompute from real `UsageLog` entries when available.
- Apply smoothing (last 14–30 days) to adapt to changing habits.
- Show confidence labels: High/Medium/Low based on data completeness.

## Search and listing UX ideas

### Primary views
1. **Product Catalog**
   - Search by product name.
   - Filters: category, type, risk level, botanical density, status.
   - Sort: cheapest unit cost, newest, safest, highest botanical density.

2. **Usage Dashboard (per user)**
   - Active products in rotation.
   - “Run low soon” list.
   - Purchased vs opened timeline.
   - Estimated depletion date based on frequency + history.

3. **Data Quality Queue**
   - Missing risk level.
   - Missing size/cost.
   - Invalid frequency strings.
   - Unit-cost calc errors.

### Helpful interactions
- Quick-add form for new products.
- Inline edit in table rows.
- Bulk import from CSV/XLSX.
- Save filter presets (“Safe + High Botanical + Body Wash”).

## Backend/API design

### Suggested endpoints
- `GET /api/products` (search + filter + pagination)
- `POST /api/products`
- `PATCH /api/products/:id`
- `GET /api/products/:id`
- `POST /api/products/:id/packages`
- `GET /api/users/me/inventory`
- `POST /api/users/me/inventory` (record purchase/open event)
- `PATCH /api/users/me/inventory/:id`
- `POST /api/users/me/inventory/:id/usage-logs`
- `GET /api/users/me/inventory/:id/runout-forecast`
- `GET /api/dashboard/usage`
- `POST /api/import` (CSV/XLSX ingestion)

### Query strategy
- Use indexed columns for common filters:
  - `name` (trigram/full-text)
  - `category_id`, `type_id`, `risk_level`, `botanical_density`, `status`
- Add server-side pagination and sorting from day one.

## Migration plan from spreadsheet

### Phase 1: Define schema + clean data
- Canonical enums for risk level, botanical density, and statuses.
- Normalize dates and frequencies.
- Resolve malformed values (e.g., typo frequencies, invalid dates).

### Phase 2: Import
- Export workbook to CSV tabs or parse XLSX directly.
- Build idempotent import script (safe to rerun).
- Capture row-level import errors and write to an audit table.

### Phase 3: App MVP
- Product list page with search/filter/sort.
- Product detail page with package and usage history.
- User inventory page (purchased/opened/expected run out).
- Admin create/edit forms.

### Phase 4: Insights
- Cost-per-use estimates.
- Product recommendation score combining safety + botanical + cost.
- Alerts for soon-to-finish products.

## Data validation rules to add early
- Cost and size must be positive numbers.
- Unit cost auto-calculated, not manually typed.
- Frequency parsed into structured form (`times_per_day` / `times_per_week`).
- Prevent impossible dates (opened before purchased, finished before opened).
- Require risk fields for “Verified Safe” state.
- Ensure run-out prediction input fields are present (size + cadence + amount/use).

## Security and operations
- Role-based access:
  - Admin: CRUD/import/manage all users.
  - Member: manage own inventory and usage logs.
  - Viewer: read/search only.
- Add audit logs for edits/imports.
- Nightly backups and migration rollback plan.

## Fast MVP blueprint (2–3 weeks)
1. Scaffold Next.js + Prisma + Postgres with configurable base path (`/app`).
2. Implement Product/Category/User/InventoryItem/UsageLog tables.
3. Build import script for the existing workbook.
4. Build searchable product table UI.
5. Add user inventory flow (purchase date, opened date, forecast run-out).
6. Add auth + role checks and deploy to `corejunkie.com/app`.

## “Best method” summary
If you want the **most practical path**, use:
- **Next.js + Prisma + PostgreSQL**,
- start with a **normalized schema** (Product, Package, User, InventoryItem, UsageLog),
- build an **idempotent importer** for your workbook,
- ship a **catalog + per-user usage dashboard MVP** first,
- calculate **expected run-out** from size + cadence + amount/use,
- then add recommendation logic and alerts.

This keeps the app simple now, but future-proofs it for richer search, analytics, and better data quality.

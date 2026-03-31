# Product List Export and Further Research.xlsx — data inventory

## Workbook overview
- **Sheet 1:** `Product List Export and Further`
- **Sheet 2:** `Sheet1`

## What this workbook stores

### 1) A curated **safe-product shortlist** (Sheet 1)
This tab is a recommendation/triage list of products grouped by category, with risk screening and a quality-style score.

**Columns:**
1. `Category`
2. `Product Name`
3. `Aloe/Honey/Almond Risk`
4. `Latex/Shea/Avocado Risk`
5. `Botanical Density`
6. `Status`

**Observed categories:** Hair, Body Wash, Lotion, Face.

**Meaning of values (as represented):**
- Risk columns are marked mostly as `✅ Clear`.
- Botanical density is labeled with tiers like `🌿 Very High`, `🌿 High`, `🌾 Moderate`, `🧪 Low`.
- Status is mainly `✅ Best Match` or `✅ Safe`.

### 2) A **purchase + usage tracker** for those products (Sheet 2)
This tab is a larger operational tracker broken into repeated category blocks (each block repeats the same header row pattern).

**Common columns in each block:**
1. `Type`
2. `Product Name`
3. `Risk Level`
4. `Botanical Density`
5. `Cost`
6. `fl oz` or `Size`
7. `$/fl oz` or `Per Unit`
8. `started:`
9. `Freq`
10. `Run low/done:`
11. `#`
12. `Duration`
13. `Status`

**What is being tracked in this sheet:**
- Safety verification status (e.g., `Verified Safe`, some `UNVERIFIED`).
- Price and package size.
- Computed cost efficiency (`$/fl oz` or `Per Unit`).
- Start date and usage frequency (where entered).
- Lifecycle fields for depletion timing (`Run low/done`, `Duration`, `Status`)—currently mostly blank.

## Notable data quality observations
- Some rows are partially filled (example: some items missing risk/botanical fields).
- At least one calculation cell contains an error value: `#DIV/0!`.
- Date values appear in mixed formats:
  - text style like `03/20/0206` (likely intended to be `03/20/2026`)
  - Excel serial date numbers like `46099` (which corresponds to `2026-03-18`).
- At least one probable typo in frequency: `2/dsy` (likely `2/day`).

## Bottom line
The file is storing a **personal product safety and selection database** plus a **cost/consumption tracker**:
- Sheet 1 = recommendation shortlist after ingredient-risk filtering.
- Sheet 2 = detailed catalog with pricing economics and usage tracking fields.

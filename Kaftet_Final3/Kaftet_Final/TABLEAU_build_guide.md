# Rebuilding "Kaftet Restock Analytics" in Native Tableau Desktop

This environment has **no Tableau Desktop**, so a native `.twb`/`.twbx` was not produced.
If you have Tableau Desktop (or Public), this guide reproduces the same dashboard from the
prepared, Tableau-ready dataset.

## 0. Connect the data
- Open Tableau → **Connect → Text file** → `output/kaftet_dashboard_data.csv`
  (or **Microsoft Excel** if you first save it as `.xlsx`).
- One row = one restock line-item. 167 rows, 30 columns.
- Set the data source name to `Kaftet Restock`.

## 1. Field roles (dimensions vs measures)

**Dimensions**
- `item_name` (Produk) · `brand` (Brand) · `source_sheet`
- `receipt_date` (set type **Date**) · `trip_label`
- `plu_code` · `price_scale_flag` · `price_anomaly_flag` (Boolean) · `member`

**Measures**
- `qty` (SUM) — *mixed packaging; label as "Unit (kemasan campuran)"*
- `unit_price_rp` (AVG/MIN/MAX) — normalised unit price
- `line_spend_rp` (SUM) — qty × unit price
- `total_after_rp` (SUM) — **headline spend measure**

> In Tableau, change the default aggregation of `unit_price_rp` to **Average** (right-click
> → Default Properties → Aggregation → Average).

## 2. Calculated fields

```
// Rupiah number format (apply as a custom format, not a field):
//   "Rp"#,##0  with thousands separator "." and decimal ","  (set Locale = Indonesia)

// Purchase frequency (distinct trips a product appears on)
Purchase Frequency = COUNTD([Receipt Date])

// Line-item frequency
Line Item Count = COUNT([Item Name])     // or SIZE() in a per-product view

// Spend share of grand total
Spend % of Total = SUM([Total After Rp]) / TOTAL(SUM([Total After Rp]))

// Price range per product (for price-stability views)
Price Range = MAX([Unit Price Rp]) - MIN([Unit Price Rp])

// Anomaly flag already in data: [Price Anomaly Flag] (TRUE/FALSE)
```

Set the **number format** of all Rupiah measures to custom `"Rp"#,##0` with the Indonesia
locale so you get `Rp4.227.538`.

## 3. Worksheets

| # | Worksheet | Marks | Rows / Columns | Notes |
|---|-----------|-------|----------------|-------|
| 1 | **KPI – Total Belanja** | Text (BAN) | `SUM(Total After Rp)` | Big number card |
| 2 | **KPI – Catatan / Produk / Trip / Unit** | Text | `COUNT`, `COUNTD(Item Name)`, `COUNTD(Receipt Date)`, `SUM(Qty)` | Four BANs |
| 3 | **Belanja per Trip** | Bar | Cols `trip_label` (sorted by date); Rows `SUM(Total After Rp)` | color `#21ABB8` |
| 4 | **Top 10 Belanja** | Horizontal bar | Rows `item_name` (Top 10 by `SUM(Total After Rp)`); Cols spend | color `#1F646B` |
| 5 | **Paling Sering Di-restock** | Horizontal bar | Rows `item_name` (Top 10 by `Line Item Count`) | color `#21ABB8`; tooltip: "jumlah catatan, bukan terjual" |
| 6 | **Kuantitas Tertinggi** | Horizontal bar | Rows `item_name` (Top 10 by `SUM(Qty)`) | color `#9CB959`; label "kemasan campuran" |
| 7 | **Keberulangan Produk** | Bar | Cols `Purchase Frequency`; Rows `COUNTD(Item Name)` | color `#133539` |
| 8 | **Harga antar Trip** | Line | Cols `trip_label`; Rows `AVG(Unit Price Rp)`; Color `item_name` | filter to comparable drinks; exclude `Price Anomaly Flag = TRUE` |
| 9 | **Perubahan Harga** | Bar | per-product first-vs-last % (table calc) | diverging teal↔green |
| 10 | **Min/Max/Avg Harga** | Text table | Rows `item_name`; `MIN/MAX/AVG(Unit Price Rp)` | filter `Purchase Frequency >= 2`, exclude anomalies |
| 11 | **Missing & Quality** | Bar / text | % null of optional columns; anomaly list | from `price_anomaly_flag` |

## 4. Dashboard layout (desktop-first, ~1360×2000, tiled)

```
┌────────────────────────────────────────────────────────┐
│  Kaftet Restock Analytics                               │  title (#133539)
│  Memahami Pola Belanja dan Perubahan Harga              │  subtitle (#1F646B)
├────────────────────────────────────────────────────────┤
│  [Total Belanja] [Catatan] [Produk] [Trip] [Unit]       │  WS 1–2 (KPI row)
├────────────────────────────────────────────────────────┤
│  Belanja per Trip (WS 3, full width)                    │
├───────────────────────────┬────────────────────────────┤
│  Top 10 Belanja (WS 4)    │  Paling Sering (WS 5)       │
├───────────────────────────┼────────────────────────────┤
│  Kuantitas Tertinggi (6)  │  Keberulangan (WS 7)        │
├────────────────────────────────────────────────────────┤
│  Harga antar Trip (WS 8, full width)                    │
├───────────────────────────┬────────────────────────────┤
│  Perubahan Harga (WS 9)   │  Min/Max/Avg (WS 10)        │
├────────────────────────────────────────────────────────┤
│  Kualitas Data & Insight (WS 11 + text)                 │
└────────────────────────────────────────────────────────┘
```

- **Background:** `#F5F7F6`. Worksheet containers: white with 1px `#e3e9e8` border.
- **Fonts:** headings `#133539`; captions `#1F646B`.
- **Color palette (create a custom categorical palette in Preferences.tps):**
  `#133539, #1F646B, #21ABB8, #9CB959`.

## 5. Filters (make them global)
- Add `trip_label`, `brand`, `item_name` as filters; on each → **Apply to Worksheets →
  All Using This Data Source**.
- Enable **Use as Filter** on the "Belanja per Trip" and "Top 10 Belanja" sheets for
  Tableau-native cross-filtering.
- Add a parameter/boolean filter on `price_anomaly_flag` to replicate the
  "exclude anomalies" sensitivity toggle.

## 6. Tooltips
- Spend tooltips: `Belanja: <SUM(Total After Rp)>` (Rupiah format).
- Frequency tooltips: add the line *"jumlah catatan — bukan jumlah terjual"*.
- Quantity tooltips: add *"unit, kemasan campuran"*.

## 7. Publish
- File → Export Packaged Workbook (`.twbx`) to embed the CSV, or publish to Tableau
  Public for a portfolio link.

> Keep the honesty notes visible on the dashboard: this is **restock/purchasing** data,
> not sales; do **not** add forecast sheets from five irregular trips.

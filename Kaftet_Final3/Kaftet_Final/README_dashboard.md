# Kaftet Restock Analytics — Dashboard

An interactive, executive-style business-intelligence dashboard for the **Kaftet** (Kafe
TETI) restock dataset — five 2026 shopping trips at Indogrosir Yogyakarta.

- **Title:** Kaftet Restock Analytics
- **Subtitle:** *Memahami Pola Belanja dan Perubahan Harga*
- **Built with:** Streamlit + Plotly (Python)
- **Style:** corporate BI layout — card-based, 4 tabs, responsive KPI grid, navy/teal palette, Indonesian labels, Rupiah formatting (`Rp1.234.567`).

> **Why Streamlit and not a native Tableau workbook?**
> Tableau Desktop is **not installed** in this environment, so a native `.twb`/`.twbx`
> cannot be produced here (and I won't fake one). This Streamlit + Plotly app reproduces
> the Tableau look and interaction patterns. If you want to rebuild it in Tableau Desktop,
> follow `TABLEAU_build_guide.md` — the prepared CSV loads straight into Tableau.

---

## 1. Files

| File | Purpose |
|------|---------|
| `prepare_dashboard_data.py` | Reads the source Excel, reproduces the cleaned item-level table (same logic as the analysis notebooks), writes the dashboard dataset. **Only reads the source; never modifies it.** |
| `kaftet_dashboard.py` | The Streamlit + Plotly dashboard app. |
| `.streamlit/config.toml` | Light theme for the main area, dark theme for the sidebar, and viewer mode (hides Deploy/menu). Keep it next to `kaftet_dashboard.py`. |
| `output/kaftet_dashboard_data.csv` | 167 item-level rows the dashboard loads (also Tableau-ready). |
| `output/kpi_summary.csv` | Validated headline KPIs. |
| `requirements_dashboard.txt` | Python dependencies. |
| `TABLEAU_build_guide.md` | Step-by-step guide to rebuild this as a native Tableau workbook. |

---

## 2. Setup & run

```bash
# 1) install dependencies (one time)
pip install -r requirements_dashboard.txt

# 2) (re)generate the dashboard dataset from the source Excel
python prepare_dashboard_data.py

# 3) launch the dashboard
streamlit run kaftet_dashboard.py
```

Then open the URL Streamlit prints (default `http://localhost:8501`). The app was tested
with Streamlit 1.66 and Plotly 7.1. Run it **from this folder** so `.streamlit/config.toml` is picked up.

---

## 3. Dashboard story (4 tabs)

1. **Ringkasan Eksekutif** — KPI cards (total belanja, jumlah catatan, produk unik, trip,
   total unit) + belanja per trip.
2. **Kinerja Produk** — Top-10 belanja, produk paling sering di-restock, kuantitas
   tertinggi, keberulangan produk antar trip. Frequency / quantity / spend are shown as
   **separate** metrics.
3. **Intelijen Harga** — harga satuan antar trip, perubahan harga tercatat, dan tabel
   min/max/rata-rata (produk dengan ≥2 trip, baris anomali dikecualikan).
4. **Kualitas Data & Insight Bisnis** — kolom yang sering kosong, daftar periksa kualitas,
   baris anomali yang ditandai, temuan ringkas, dan rekomendasi.

### Interactivity
- **Sidebar filters:** Trip (pills), Brand, Produk — applied across the whole dashboard, plus a **Reset** button and a **CSV download** of the filtered data. The sidebar is dark and can be collapsed into an icon rail (click `«`); click `»` or any rail icon to expand it again. Filters are kept while collapsed.
  The Produk list narrows to the chosen Brand(s).
- **Sensitivity toggle:** "Kecualikan 2 baris anomali harga" recomputes everything without
  the two flagged rows (the underlying data is **not** changed).
- **Tooltips** on every chart with Rupiah-formatted values and metric clarifications
  (e.g. "jumlah catatan, bukan jumlah terjual").

---

## 4. KPI definitions (validated against the source)

All figures below were verified by `prepare_dashboard_data.py` against the source Excel.

| KPI | Definition | Value (all trips) |
|-----|-----------|-------------------|
| **Total Belanja Restock** | Σ `total_after_discount`, normalised to rupiah (`total_after_rp`) | **Rp4.227.538** |
| *Belanja alternatif* | Σ `qty × unit_price_rp` (before per-line discount) | Rp4.520.600 |
| **Jumlah Catatan** | number of receipt line-items (rows) | **167** |
| **Produk Unik** | distinct standardised `item_name` | **90** |
| **Trip Belanja** | distinct `receipt_date` | **5** |
| **Total Unit** | Σ `qty` — **mixed packaging** (pcs vs cartons) | **396** |

**Metric separation (important):**
- **Line-item frequency** = how many receipt rows a product appears on.
- **Purchase frequency** = how many distinct trips a product was bought on (≤5).
- **Recorded quantity** = Σ `qty` (mixed packaging; not a like-for-like piece count).
- **Expenditure** = money spent (Rp).

These are **not interchangeable** and are never mixed in a single chart.

### Monetary normalisation
One receipt sheet (18-Sep) recorded prices as small decimals (thousands scale, e.g. `17.5`
= Rp 17.500). For cross-trip comparison the dashboard uses derived columns
`unit_price_rp`, `total_after_rp`, `line_spend_rp`. The **original** `unit_price` /
`total_after_discount` columns are preserved in the dataset and never overwritten.

---

## 5. Known limitations

- **Restock data, not sales.** Everything here is *what was purchased*. It does **not**
  measure sales, demand, popularity, or profit. A product absent from a trip does **not**
  mean zero demand.
- **Five irregular trips** (gaps of 66, 57, 16, 14 days) → **no forecasting** of demand or
  sales is attempted; that would be indefensible at this sample size.
- **Mixed packaging units** in `qty` → "total unit" is indicative, not comparable piece
  counts.
- **Mixed date formats** (`dd-mm-yyyy` and `dd-mm-yy`) parsed with `dayfirst`; raw strings
  kept.
- **Two flagged anomalies preserved, not corrected:**
  - *ISOPLUS COCO 350ML* (19-Aug): `unit_price` 2.500 vs `total_after` 30.000.
  - *PUCUK HARUM TEH MELATI 350ml* (18-Sep): `qty` 24 at Rp3.150 vs ~66.600–75.600
    elsewhere (looks like a combined scale + qty/pack mix-up).
  Use the sidebar toggle to see their influence on totals.
- **Sparse optional fields** (`discount`, `profit`, `sisa`, `rusak`, `transaction_no`) →
  limited per-transaction/margin analysis.
- **Brand = first word of product name** (heuristic); coded names (N/P, S/N, BC) are
  approximate.

---

## 6. Data lineage

```
Struk_Indogrosir_restock_18_April_2026 (2).xlsx   (source, read-only)
          │   prepare_dashboard_data.py  (same cleaning logic as the notebooks)
          ▼
output/kaftet_dashboard_data.csv  ──►  kaftet_dashboard.py (Streamlit + Plotly)
```

The source workbook and the three analysis notebooks are never modified by the dashboard.

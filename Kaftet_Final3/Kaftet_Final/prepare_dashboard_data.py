"""Prepare the Tableau-/dashboard-ready dataset for Kaftet Restock Analytics.

Reproduces the SAME cleaned item-level table used in the analysis notebooks (identical
logic: header detection, type coercion, brand standardisation, jastip removal, the one
admin qty fix), then writes a tidy CSV + a KPI summary. Source file is only READ.

Run:  python prepare_dashboard_data.py
Outputs (in ./output):
  - kaftet_dashboard_data.csv   (167 item-level rows, analysis-ready)
  - kpi_summary.csv             (validated headline KPIs)
"""
import re, warnings
from pathlib import Path
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

SOURCE_FILE = Path("Struk_Indogrosir_restock_18_April_2026 (2).xlsx")
OUT = Path("output"); OUT.mkdir(exist_ok=True)

COLUMN_MAPPING = {"No":"line_no","Kode PLU":"plu_code","Nama Barang":"item_name","Qty":"qty",
 "Harga Satuan (Rp)":"unit_price","Diskon (Rp)":"discount","Total Sebelum Diskon (Rp)":"total_before_discount",
 "Total Akhir (Rp)":"total_after_discount","Total":"total_raw","Isi":"isi","Modal/pcs":"cost_per_pcs",
 "Jual/pcs":"sell_per_pcs","Jual Total":"sell_total","Untung":"profit","Untung/pcs":"profit_per_pcs",
 "sisa":"sisa","rusak":"rusak"}
NUMERIC_COLS = ["line_no","qty","unit_price","discount","total_before_discount","total_after_discount",
 "total_raw","isi","cost_per_pcs","sell_per_pcs","sell_total","profit","profit_per_pcs","sisa","rusak"]
NA_TOKENS = {"-","","nan","#div/0!","#value!","#ref!","#n/a","na","none"}

def find_header_row(df):
    for i in range(min(15,len(df))):
        row=" ".join(str(v).lower() for v in df.iloc[i].tolist())
        if "kode plu" in row and "nama barang" in row: return i
def classify_rows(df,h):
    out=[]
    for i in range(len(df)):
        if h is not None and i<h: out.append("metadata"); continue
        if i==h: out.append("header"); continue
        c0,c1=df.iat[i,0],df.iat[i,1]
        if pd.isna(c0) and pd.isna(c1): out.append("blank"); continue
        num=pd.to_numeric(pd.Series([c0]),errors="coerce").notna().iat[0]
        out.append("item" if (num and not pd.isna(c1)) else "summary")
    return pd.Series(out,index=df.index)
def to_number(x):
    if pd.isna(x): return np.nan
    s=str(x).strip()
    if s.lower() in NA_TOKENS: return np.nan
    if re.fullmatch(r"\d{1,3}(\.\d{3})+",s): s=s.replace(".","")
    s=s.replace(",","")
    try: return float(s)
    except ValueError: return np.nan
def extract_metadata(df):
    meta={"receipt_date_raw":np.nan,"receipt_time_raw":np.nan,"transaction_no":np.nan,"member":np.nan}
    top=" | ".join(str(v) for i in range(min(4,len(df))) for v in df.iloc[i].tolist() if not pd.isna(v))
    for k,pat in [("receipt_date_raw",r"Tanggal:\s*([0-9]{2}-[0-9]{2}-[0-9]{2,4})"),
                  ("receipt_time_raw",r"(\d{2}:\d{2}:\d{2})"),
                  ("transaction_no",r"No\.?\s*Transaksi:\s*([^\s|]+)"),
                  ("member",r"Member:\s*([^|]+?)\s*(?:\||$)")]:
        m=re.search(pat,top)
        if m: meta[k]=m.group(1).strip()
    return meta

raw_sheets = pd.read_excel(SOURCE_FILE, sheet_name=None, header=None)
header_rows = {n: find_header_row(d) for n,d in raw_sheets.items()}
row_kinds   = {n: classify_rows(d, header_rows[n]) for n,d in raw_sheets.items()}

def clean_sheet(name, df, h, kinds):
    items = df[kinds=="item"].copy(); items.columns=[str(c).strip() for c in df.iloc[h].tolist()]
    keep=[c for c in items.columns if c in COLUMN_MAPPING]; items=items[keep].rename(columns=COLUMN_MAPPING)
    items["source_row"]=items.index+1; items["source_sheet"]=name
    for col in ("item_name","plu_code"):
        if col in items: items[col]=items[col].astype(str).str.strip()
    if "plu_code" in items: items["plu_code"]=items["plu_code"].str.replace(r"\.0$","",regex=True).replace("nan",np.nan)
    for col in NUMERIC_COLS:
        if col in items: items[col]=items[col].map(to_number)
    for k,v in extract_metadata(df).items(): items[k]=v
    return items

cleaned = {n: clean_sheet(n, raw_sheets[n], header_rows[n], row_kinds[n]) for n in raw_sheets}
scale_flag = {n: ("thousands (decimals)" if (d["unit_price"].median()<1000) else "full rupiah")
              for n,d in cleaned.items()}
FINAL_COLUMNS = ["source_sheet","source_row","receipt_date_raw","receipt_time_raw","transaction_no",
 "member","line_no","plu_code","item_name","qty","unit_price","discount","total_before_discount",
 "total_after_discount","isi","cost_per_pcs","sell_per_pcs","sell_total","profit","profit_per_pcs",
 "sisa","rusak","price_scale_flag"]
parts=[]
for n,d in cleaned.items():
    t=d.copy(); t["price_scale_flag"]=scale_flag[n]
    for c in FINAL_COLUMNS:
        if c not in t: t[c]=np.nan
    parts.append(t[FINAL_COLUMNS])
integrated = pd.concat(parts, ignore_index=True)

df = integrated.copy()
df.loc[(df["item_name"]=="ISOPLUS COCO 350ML") & (df["qty"]==12), "qty"] = 1
rename_all = {
 "OISHI POPCRN COK 20G":"OISHI POPCORN COKELAT 20G","OISHI POPCRN KEJU20G":"OISHI POPCORN KEJU 20G",
 "OISHI PCRN CRMEL 20G":"OISHI POPCORN CARAMEL 20G","OISHI TCRN KEJU 20G":"OISHI POPCORN KEJU 20G",
 "OISHI PILLOW CHOCO12":"OISHI PILLOW CHOCO 12G","BC MKRONI LV.15/27G":"BONCABE MAKARONI LEVEL 15 27G",
 "BC CKR NAGA LV15 25G":"BONCABE CKR NAGA LEVEL 15 25G","MIKAKO S/AK MI GRG18":"MIKAKO SNACK MIE GORENG 18Gr",
 "MIKAKO SNAK MI GRG18":"MIKAKO SNACK MIE GORENG 18Gr","MIKAKO SNK RMPT LT18":"MIKAKO SNACK RUMPUT LAUT 18Gr",
 "TIC TAC SAPI PGG 14G":"TIC TAC SAPI PANGGANG 14Gr","TIC TAC AYAM BWNG 14":"TIC TAC AYAM BAWANG 14Gr",
 "TIC TAC PEDAS 14G":"TIC TAC PEDAS 14Gr","D/K TIC TAC MIX 14G":"TIC TAC MIX 14Gr",
 "MIE KRMEZ S&S AP 16G":"MIE KREMEZ SHAKE & SHOR AYAM PANGGANG 16Gr","MIE KREME S&S AP 16G":"MIE KREMEZ SHAKE & SHOR AYAM PANGGANG 16Gr",
 "M/KREMEZ S&S BLDO 16":"MIE KREMEZ SHAKE & SHOR BALADO 16Gr","TANGO WFLE CHOCOHZ21":"TANGO WAFFLE CHOCO HAZELNUT 21Gr",
 "TANGO WAF E CHOCOHZ21":"TANGO WAFFLE CHOCO HAZELNUT 21Gr","AOKA ROTI PGG KEJU15":"AOKA ROTI PGG KEJU65",
 "PUCUK/H TEH MLATI350":"PUCUK HARUM TEH MELATI 350ml","TEH PUCUK HARUM 6'S":"PUCUK HARUM TEH MELATI 350ml",
 "PUCUK/P TEH MELATI 350":"PUCUK HARUM TEH MELATI 350ml","PUCUK TH MLTI 350 ML":"PUCUK HARUM TEH MELATI 350ml",
 "ISOPLUS 2000 350ML":"ISOPLUS BTL 350ML","N/P MNM LIME 330 ML":"N/P MINUMAN LIME 330",
 "S/N SOSI MKN SP1525":"S/N SOSIS MKN SPI525","NABATI SIIP JG/BK20S":"NABATI SIIP JAGUNG BAKAR 4Gr",
 "NABATI SIIP KEJU 20S":"NABATI SIIP KEJU 4Gr","NABATI SIIP JG/BK 4G":"NABATI SIIP JAGUNG BAKAR 4Gr",
 "NABATI SIIP KEJU 4G":"NABATI SIIP KEJU 4Gr","NABATI RCHESE KEJU 5":"NABATI RICHEESE KEJU 5Gr",
 "NABATI RCHSE AHH 20S":"NABATI RICHEESE AHH 4Gr","NABATI SIIP CKLT 4G":"NABATI SIIP COKLAT 4Gr"}
df["item_name"] = df["item_name"].replace(rename_all).str.strip()
jastip = ["KIN B/YOG BLACK 45G","CMRY EAT MILK MATCHA","KZLER SS TOM YUM 60G",
          "GLADE PNY&BRY BLS 70","PRONAS SAUSGE CHIC65","INDF SMB CBK LIMAU5S"]
df = df[~df["item_name"].isin(jastip)].copy().reset_index(drop=True)

# analysis-only helper columns
df["receipt_date"] = pd.to_datetime(df["receipt_date_raw"], format="mixed", dayfirst=True, errors="coerce")
df["trip_label"] = df["receipt_date"].dt.strftime("%d %b %Y")
is_k = df["price_scale_flag"].str.startswith("thousands")
df["unit_price_rp"]  = np.where(is_k, df["unit_price"]*1000, df["unit_price"])
df["total_after_rp"] = np.where(is_k, df["total_after_discount"]*1000, df["total_after_discount"])
df["line_spend_rp"]  = df["qty"] * df["unit_price_rp"]
df["brand"] = df["item_name"].str.split().str[0].str.upper()

# flag the known price-total mismatch rows (preserve, do not change)
prod_med = df.groupby("item_name")["unit_price_rp"].transform("median")
df["price_anomaly_flag"] = ((df["unit_price_rp"] < prod_med*0.2) | (df["unit_price_rp"] > prod_med*5))

df.to_csv(OUT / "kaftet_dashboard_data.csv", index=False)

# ---- validated KPIs (both spend definitions reported) ----
kpis = {
    "restock_records": len(df),
    "unique_products": df["item_name"].nunique(),
    "shopping_trips": df["receipt_date"].nunique(),
    "total_units_mixed_packaging": df["qty"].sum(),
    "spend_qty_x_unitprice_rp": round(df["line_spend_rp"].sum()),
    "spend_sum_total_after_discount_rp": round(df["total_after_rp"].sum()),
}
pd.DataFrame([kpis]).T.rename(columns={0:"value"}).to_csv(OUT / "kpi_summary.csv")

print("=== VALIDATED KPIs ===")
for k,v in kpis.items(): print(f"  {k}: {v:,}" if isinstance(v,(int,float)) else f"  {k}: {v}")
print("\nrows:", len(df), "cols:", df.shape[1])
print("date formats seen:", df["receipt_date_raw"].dropna().unique().tolist())
print("price_anomaly rows:", int(df["price_anomaly_flag"].sum()))
print("wrote output/kaftet_dashboard_data.csv and output/kpi_summary.csv")

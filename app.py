import io
import pandas as pd
import streamlit as st


st.set_page_config(page_title="Bin ID Generator", page_icon="📦", layout="wide")


# -----------------------------
# Helper Functions
# -----------------------------


def shelf_letters(n: int) -> list:
"""Return ['A', 'B', ..., 'Z', 'AA', 'AB', ...] up to n shelves."""
if n < 1:
return []
letters = []
i = 0
while len(letters) < n:
# Excel-style column names starting at A=1
value = i + 1
name = ""
while value > 0:
value, rem = divmod(value - 1, 26)
name = chr(65 + rem) + name
letters.append(name)
i += 1
return letters




def build_labels_uniform(num_aisles: int, bays_per_aisle: int, shelves_per_bay: int, bins_per_shelf: int) -> pd.DataFrame:
rows = []
shelves = shelf_letters(shelves_per_bay)
for a in range(1, num_aisles + 1):
for b in range(1, bays_per_aisle + 1):
for s in shelves:
for n in range(1, bins_per_shelf + 1):
label = f"M{a:02d}-{b:02d}-{s}{n:02d}"
rows.append({
"aisle": a,
"bay": b,
"shelf": s,
"bin": n,
"label": label,
})
return pd.DataFrame(rows)




def build_labels_from_csv(df_cfg: pd.DataFrame) -> pd.DataFrame:
"""
Build labels from a configuration DataFrame with columns:
- aisle (int)
- bay (int)
- shelves (int) # number of shelves in this bay
- bins (int) # number of bins per shelf in this bay
Each row defines one bay's structure.
"""
required = {"aisle", "bay", "shelves", "bins"}
missing = required - set(c.lower() for c in df_cfg.columns)
if missing:
raise ValueError(f"CSV missing columns: {', '.join(sorted(missing))}")


# Normalize columns to lowercase
df_cfg = df_cfg.rename(columns={c: c.lower() for c in df_cfg.columns})


rows = []
for _, r in df_cfg.sort_values(["aisle", "bay"]).iterrows():
a = int(r["aisle"]) # aisle number
b = int(r["bay"]) # bay number within the aisle
shelves = shelf_letters(int(r["shelves"]))
bins_per_shelf = int(r["bins"]) # uniform across shelves for this bay
for s in shelves:
for n in range(1, bins_per_shelf + 1):
label = f"M{a:02d}-{b:02d}-{s}{n:02d}"
rows.append({
"aisle": a,
"bay": b,
"shelf": s,
"bin": n,
"label": label,
})
)

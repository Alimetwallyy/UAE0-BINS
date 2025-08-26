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
    required = {"aisle", "bay", "shelves", "bins"}
    missing = required - set(c.lower() for c in df_cfg.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {', '.join(sorted(missing))}")

    df_cfg = df_cfg.rename(columns={c: c.lower() for c in df_cfg.columns})

    rows = []
    for _, r in df_cfg.sort_values(["aisle", "bay"]).iterrows():
        a = int(r["aisle"])
        b = int(r["bay"])
        shelves = shelf_letters(int(r["shelves"]))
        bins_per_shelf = int(r["bins"])
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


def to_csv_download(df: pd.DataFrame, filename: str = "bin_labels.csv"):
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=buf.getvalue(),
        file_name=filename,
        mime="text/csv",
        use_container_width=True
    )

# -----------------------------
# UI
# -----------------------------
st.title("📦 Warehouse Bin ID Generator")
st.caption("Format: MAA-BB-XNN e.g. M01-03-B07")

mode = st.sidebar.radio("Generation Mode", ["Uniform counts", "Upload CSV (per-bay)"])

if mode == "Uniform counts":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        num_aisles = st.number_input("Number of aisles", min_value=1, value=3, step=1)
    with col2:
        bays_per_aisle = st.number_input("Bays per aisle", min_value=1, value=5, step=1)
    with col3:
        shelves_per_bay = st.number_input("Shelves per bay", min_value=1, value=4, step=1)
    with col4:
        bins_per_shelf = st.number_input("Bins per shelf", min_value=1, value=10, step=1)

    if st.button("Generate labels", use_container_width=True):
        df = build_labels_uniform(int(num_aisles), int(bays_per_aisle), int(shelves_per_bay), int(bins_per_shelf))
        st.success(f"Generated {len(df):,} labels.")
        st.dataframe(df, use_container_width=True, hide_index=True)
        to_csv_download(df)

else:
    st.markdown(
        "Upload a CSV with columns: **aisle, bay, shelves, bins**.\n\n"
        "Each row describes a single bay (its aisle number, bay number, how many shelves it has, "
        "and how many bins per shelf).\n\n"
        "Example rows:\n\n"
        "```\n"
        "aisle,bay,shelves,bins\n"
        "1,1,4,10\n"
        "1,2,3,8\n"
        "2,1,5,12\n"
        "```"
    )

    up = st.file_uploader("Choose CSV file", type=["csv"])
    if up is not None:
        try:
            df_cfg = pd.read_csv(up)
            st.subheader("Parsed configuration (first 100 rows)")
            st.dataframe(df_cfg.head(100), use_container_width=True, hide_index=True)

            if st.button("Generate labels from CSV", use_container_width=True):
                df = build_labels_from_csv(df_cfg)
                st.success(f"Generated {len(df):,} labels from {df_cfg.shape[0]:,} bay definitions.")
                st.dataframe(df, use_container_width=True, hide_index=True)
                to_csv_download(df, filename="bin_labels_from_csv.csv")
        except Exception as e:
            st.error(f"Problem reading CSV: {e}")

# Footer / help
with st.expander("Help & Notes"):
    st.markdown(
        "- **Aisles** and **bays** are always zero-padded to two digits (01, 02, ...).\n"
        "- **Shelf** uses letters A, B, C, ... and continues as AA, AB, ... if >26 shelves.\n"
        "- **Bin** is zero-padded to two digits (01, 02, ...).\n"
        "- Label example: for aisle 3, bay 7, shelf C, bin 5 → **M03-07-C05**."
    )

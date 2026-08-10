import streamlit as st
from utils import load_data
import pandas as pd

st.set_page_config(page_title="Dataset & Preprocessing", layout="wide")
st.title("📂 Dataset & Preprocessing")
st.caption("Inspect the IPL datasets, find data-quality issues, and prepare a clean working copy for analysis.")

matches, deliveries = load_data()

dataset_name = st.sidebar.radio("Choose dataset", ["Matches", "Deliveries"])
source_data = matches if dataset_name == "Matches" else deliveries

tab_overview, tab_quality, tab_explore, tab_prepare = st.tabs([
	"📊 Overview",
	"🧪 Data Quality",
	"🔎 Explore",
	"🛠️ Prepare Data",
])

with tab_overview:
	st.subheader(f"{dataset_name} dataset overview")

	total_cells = source_data.shape[0] * source_data.shape[1]
	missing_cells = int(source_data.isna().sum().sum())
	duplicate_rows = int(source_data.duplicated().sum())

	col1, col2, col3, col4 = st.columns(4)
	col1.metric("Rows", f"{len(source_data):,}")
	col2.metric("Columns", len(source_data.columns))
	col3.metric("Missing cells", f"{missing_cells:,}")
	col4.metric("Duplicate rows", f"{duplicate_rows:,}")

	st.subheader("What this dataset contains")
	if dataset_name == "Matches":
		st.info("One row represents a match. Use this dataset for seasons, venues, teams, toss decisions, and match winners.")
	else:
		st.info("One row represents a delivery. Use this dataset for batter, bowler, runs, overs, and wicket-level analysis.")

	st.subheader("Column profile")
	profile = pd.DataFrame({
		"Column": source_data.columns,
		"Type": source_data.dtypes.astype(str).values,
		"Non-null": source_data.notna().sum().values,
		"Missing": source_data.isna().sum().values,
		"Unique values": source_data.nunique(dropna=True).values,
	})
	profile["Completeness"] = (profile["Non-null"] / len(source_data) * 100).round(1).astype(str) + "%"
	st.dataframe(profile, use_container_width=True, hide_index=True)

with tab_quality:
	st.subheader(f"Data-quality checks for {dataset_name.lower()}")

	quality = pd.DataFrame({
		"Column": source_data.columns,
		"Missing values": source_data.isna().sum().values,
		"Missing %": (source_data.isna().mean().mul(100).round(2)).values,
		"Unique values": source_data.nunique(dropna=True).values,
	})
	quality = quality.sort_values(["Missing values", "Unique values"], ascending=[False, True])
	st.dataframe(quality, use_container_width=True, hide_index=True)

	missing_columns = quality[quality["Missing values"] > 0]
	if missing_columns.empty:
		st.success("No missing values were found in this dataset.")
	else:
		st.warning(f"{len(missing_columns)} column(s) contain missing values. Review the table before choosing a fill strategy.")

	duplicate_count = int(source_data.duplicated().sum())
	if duplicate_count:
		st.warning(f"{duplicate_count:,} duplicate row(s) detected.")
	else:
		st.success("No duplicate rows were found.")

	numeric_columns = source_data.select_dtypes(include="number").columns.tolist()
	if numeric_columns:
		st.subheader("Numeric summary")
		st.dataframe(source_data[numeric_columns].describe().T.round(2), use_container_width=True)

with tab_explore:
	st.subheader(f"Explore {dataset_name.lower()} records")
	search_text = st.text_input("Search all text columns", placeholder="Try a team, venue, player, or match id")
	selected_columns = st.multiselect(
		"Columns to display",
		source_data.columns.tolist(),
		default=source_data.columns.tolist()[: min(8, len(source_data.columns))],
	)
	rows_to_show = st.slider("Rows to preview", 5, 100, 20)

	preview = source_data.copy()
	if search_text:
		text_columns = preview.select_dtypes(include=["object", "string"]).columns
		if len(text_columns):
			matches_search = preview[text_columns].astype("string").apply(
				lambda column: column.str.contains(search_text, case=False, na=False)
			).any(axis=1)
			preview = preview[matches_search]

	if not selected_columns:
		st.warning("Select at least one column to display.")
	else:
		st.caption(f"Showing {min(len(preview), rows_to_show):,} of {len(preview):,} matching rows")
		st.dataframe(preview[selected_columns].head(rows_to_show), use_container_width=True, hide_index=True)

with tab_prepare:
	st.subheader("Create a clean working copy")
	st.caption("These options affect only the preview below. The original CSV files remain unchanged.")

	remove_duplicates = st.checkbox("Remove duplicate rows", value=True)
	remove_empty_columns = st.checkbox("Remove columns that are entirely empty", value=True)
	fill_missing = st.checkbox("Fill missing values", value=True)
	convert_dates = st.checkbox("Convert date column to a consistent date format", value=True)

	prepared = source_data.copy()
	actions = []

	if remove_duplicates:
		before = len(prepared)
		prepared = prepared.drop_duplicates()
		actions.append(f"Removed {before - len(prepared):,} duplicate row(s)")

	if remove_empty_columns:
		empty_columns = prepared.columns[prepared.isna().all()].tolist()
		if empty_columns:
			prepared = prepared.drop(columns=empty_columns)
		actions.append(f"Removed {len(empty_columns)} completely empty column(s)")

	if fill_missing:
		numeric_columns = prepared.select_dtypes(include="number").columns
		text_columns = prepared.select_dtypes(include=["object", "string"]).columns
		for column in numeric_columns:
			if prepared[column].isna().any():
				prepared[column] = prepared[column].fillna(prepared[column].median())
		for column in text_columns:
			if prepared[column].isna().any():
				prepared[column] = prepared[column].fillna("Unknown")
		actions.append("Filled numeric gaps with medians and text gaps with 'Unknown'")

	if convert_dates and "date" in prepared.columns:
		prepared["date"] = pd.to_datetime(prepared["date"], errors="coerce").dt.strftime("%Y-%m-%d")
		actions.append("Standardized the date column")

	col1, col2, col3 = st.columns(3)
	col1.metric("Prepared rows", f"{len(prepared):,}", delta=f"{len(prepared) - len(source_data):+,}")
	col2.metric("Prepared columns", len(prepared.columns), delta=f"{len(prepared.columns) - len(source_data.columns):+}")
	col3.metric("Remaining missing cells", f"{int(prepared.isna().sum().sum()):,}")

	st.subheader("Applied steps")
	for action in actions:
		st.write(f"- {action}")

	st.subheader("Prepared data preview")
	st.dataframe(prepared.head(50), use_container_width=True, hide_index=True)
	st.download_button(
		"📥 Download prepared CSV",
		prepared.to_csv(index=False).encode("utf-8"),
		file_name=f"{dataset_name.lower()}_prepared.csv",
		mime="text/csv",
	)
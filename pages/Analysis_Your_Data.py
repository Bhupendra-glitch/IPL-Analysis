import streamlit as st
import pandas as pd
import numpy as np
import importlib.util

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Check sklearn availability
SKLEARN_AVAILABLE = False
SKLEARN_DIAG = None
if importlib.util.find_spec("sklearn") is not None:
    try:
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, mean_squared_error, r2_score, classification_report
        from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
        from sklearn.preprocessing import LabelEncoder
        SKLEARN_AVAILABLE = True
    except Exception as exc:
        SKLEARN_DIAG = exc
else:
    SKLEARN_DIAG = "sklearn package not found in the current Python environment"

st.set_page_config(
    page_title="Analyze Your Data",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧪 Analyze Your Data")
st.write(
    "Upload your own dataset and perform a full exploratory data analysis, create visualizations, "
    "and build a basic machine learning prediction model from the same page."
)

uploaded_file = st.file_uploader("Upload a CSV file for analysis", type=["csv"])

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

if uploaded_file is None:
    st.info("Upload a CSV file to start. The page will analyze your data, show charts, and allow ML predictions.")
    st.warning("Tip: Your file should include a target column for best ML predictions.")
    st.stop()

try:
    df = load_csv(uploaded_file)
except Exception as exc:
    st.error("Unable to load uploaded file. Make sure it is a valid CSV.")
    st.write(exc)
    st.stop()

st.success("✅ File loaded successfully")

# Basic data overview
st.subheader("📋 Data Overview")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Rows", df.shape[0])
with col2:
    st.metric("Columns", df.shape[1])
with col3:
    st.metric("Missing cells", int(df.isna().sum().sum()))

with st.expander("Preview dataset"):
    st.dataframe(df.head(20))

with st.expander("Column summary"):
    desc = df.describe(include='all').transpose()
    st.dataframe(desc)

# Data types and missing values
st.subheader("🔎 Data Types & Missing Values")
missing = df.isna().sum().sort_values(ascending=False)
cols_by_type = df.dtypes.reset_index()
cols_by_type.columns = ["Column", "Type"]

col1, col2 = st.columns([2, 1])
with col1:
    st.dataframe(cols_by_type)
with col2:
    st.dataframe(missing[missing > 0].to_frame(name="Missing Count"))

numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_columns = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

# Visualization and EDA
st.subheader("📈 Exploratory Data Analysis")

with st.expander("Numeric feature distributions"):
    if not numeric_columns:
        st.warning("No numeric columns found for histogram visualization.")
    else:
        selected_numeric = st.selectbox("Select numeric column", numeric_columns)
        if PLOTLY_AVAILABLE:
            fig = px.histogram(df, x=selected_numeric, nbins=30, title=f"Distribution of {selected_numeric}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write(df[selected_numeric].hist(bins=30))
            st.warning("Install plotly for richer interactive charts.")

with st.expander("Categorical feature breakdown"):
    if not categorical_columns:
        st.warning("No categorical columns found for category charts.")
    else:
        selected_cat = st.selectbox("Select categorical column", categorical_columns)
        value_counts = df[selected_cat].value_counts().head(20)
        if PLOTLY_AVAILABLE:
            fig = px.bar(value_counts, x=value_counts.index, y=value_counts.values, title=f"Top categories for {selected_cat}")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.bar_chart(value_counts)
            st.warning("Install plotly for richer interactive charts.")

with st.expander("Correlation matrix"):
    if len(numeric_columns) < 2:
        st.warning("At least two numeric columns are required to compute correlations.")
    else:
        corr = df[numeric_columns].corr()
        st.dataframe(corr)
        if PLOTLY_AVAILABLE:
            fig = go.Figure(
                data=go.Heatmap(
                    z=corr.values,
                    x=corr.columns,
                    y=corr.columns,
                    colorscale="RdBu",
                    zmid=0,
                )
            )
            fig.update_layout(title="Numeric Feature Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)

# Feature summary
st.subheader("🧠 Feature Summary")
if numeric_columns:
    with st.expander("Numeric feature summary"):
        st.write(df[numeric_columns].describe().transpose())

if categorical_columns:
    with st.expander("Categorical feature summary"):
        cat_summary = pd.DataFrame({
            "Unique values": df[categorical_columns].nunique(),
            "Top value": df[categorical_columns].mode().iloc[0],
            "Missing": df[categorical_columns].isna().sum()
        })
        st.dataframe(cat_summary)

# Machine learning prediction
st.subheader("🤖 Machine Learning Prediction")
if not SKLEARN_AVAILABLE:
    st.warning("scikit-learn is not available in this environment. Install it with `pip install scikit-learn` to enable ML prediction.")
    if SKLEARN_DIAG:
        st.write("Diagnostic:", SKLEARN_DIAG)
    st.stop()

with st.expander("Build a prediction model"):
    if df.empty:
        st.error("The uploaded dataset is empty. Please upload a valid CSV file.")
    else:
        target_column = st.selectbox("Select target column", df.columns, index=0)
        available_features = [col for col in df.columns if col != target_column]
        feature_columns = st.multiselect("Select feature columns", available_features, default=available_features[:4])
        if not feature_columns:
            st.info("Choose one or more feature columns to train the model.")
        elif target_column is None:
            st.info("Select a target column first.")
        else:
            target_series = df[target_column]
            X = df[feature_columns].copy()
            y = target_series.copy()

            # Preprocess features
            X = pd.get_dummies(X, drop_first=True)
            X = X.fillna(0)

            problem_type = "classification"
            if pd.api.types.is_numeric_dtype(y) and y.nunique() > 15:
                problem_type = "regression"

            if problem_type == "classification":
                y_encoded = LabelEncoder().fit_transform(y.astype(str))
                y_model = y_encoded
                model = RandomForestClassifier(n_estimators=100, random_state=42)
            else:
                y_model = y.astype(float).fillna(0)
                model = RandomForestRegressor(n_estimators=100, random_state=42)

            test_size = st.slider("Test set size (%)", min_value=10, max_value=50, value=20)
            if st.button("Train and evaluate model"):
                with st.spinner("Training the model..."):
                    X_train, X_test, y_train, y_test = train_test_split(
                        X, y_model, test_size=test_size / 100.0, random_state=42
                    )
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)

                    if problem_type == "classification":
                        score = accuracy_score(y_test, y_pred)
                        st.success(f"Model type: Classification")
                        st.metric("Test Accuracy", f"{score:.2f}")
                        st.write("### Classification report")
                        st.text(classification_report(y_test, y_pred, zero_division=0))
                    else:
                        mse = mean_squared_error(y_test, y_pred)
                        r2 = r2_score(y_test, y_pred)
                        st.success("Model type: Regression")
                        st.metric("R² score", f"{r2:.2f}")
                        st.metric("MSE", f"{mse:.2f}")

                    st.write("### Example predictions")
                    example_results = X_test.copy()
                    example_results["Predicted"] = y_pred
                    if problem_type == "classification":
                        example_results["Actual"] = y_test
                    else:
                        example_results["Actual"] = y_test
                    st.dataframe(example_results.head(10))

                    st.write("### Feature importance")
                    importance = pd.DataFrame({
                        "feature": X.columns,
                        "importance": model.feature_importances_
                    }).sort_values("importance", ascending=False).head(15)
                    st.dataframe(importance)

                    if PLOTLY_AVAILABLE and not importance.empty:
                        fig = px.bar(importance, x="feature", y="importance", title="Top feature importances")
                        fig.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig, use_container_width=True)

# Download section
with st.expander("Download analysis report"):
    if st.button("Download summary as CSV"):
        report_df = pd.DataFrame({
            "Metric": ["Rows", "Columns", "Missing values", "Numeric features", "Categorical features"],
            "Value": [
                df.shape[0],
                df.shape[1],
                int(df.isna().sum().sum()),
                len(numeric_columns),
                len(categorical_columns),
            ],
        })
        csv = report_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download summary CSV", csv, "data_analysis_summary.csv", "text/csv")

st.markdown("---")
st.write("Upload your next file or scroll back up to repeat the analysis.")
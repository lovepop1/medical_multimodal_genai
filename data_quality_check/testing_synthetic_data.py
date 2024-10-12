def app():
    import streamlit as st
    import pandas as pd
    import matplotlib.pyplot as plt
    import plotly.express as px
    import io
    import base64
    import json

    # Function to automatically detect categorical columns
    def detect_categorical_columns(df):
        return df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

    # Function to compute general metrics
    def compute_general_metrics(df, dataset_name):
        metrics = {
            f"{dataset_name} Rows": df.shape[0],
            f"{dataset_name} Columns": df.shape[1],
            f"{dataset_name} Data Types": {str(k): v for k, v in df.dtypes.value_counts().items()}
        }
        return metrics

    # Function to compute missing values
    def compute_missing_values(df, dataset_name):
        missing = df.isnull().sum()
        missing_percent = (missing / len(df)) * 100
        missing_df = pd.DataFrame({
            'Column': df.columns,
            'Missing Values': missing,
            'Missing Percentage': missing_percent
        })
        return missing_df

    # Function to compute numerical statistics
    def compute_numerical_stats(df, dataset_name):
        numerical = df.select_dtypes(include=['int64', 'float64'])
        stats = numerical.describe().transpose()
        stats = stats.rename(columns={
            'count': 'Count',
            'mean': 'Mean',
            'std': 'Std Dev',
            'min': 'Min',
            '25%': '25%',
            '50%': '50%',
            '75%': '75%',
            'max': 'Max'
        })
        return stats

    # Function to compute categorical statistics
    def compute_categorical_stats(df, categorical_cols, dataset_name):
        cat_stats = {}
        for col in categorical_cols:
            counts = df[col].value_counts(dropna=False)
            percentages = df[col].value_counts(normalize=True, dropna=False) * 100
            cat_stats[col] = pd.DataFrame({
                'Category': counts.index.astype(str),
                'Count': counts.values,
                'Percentage': percentages.values
            })
        return cat_stats

    # Function to compute correlation matrix
    def compute_correlation_matrix(df, dataset_name):
        numerical = df.select_dtypes(include=['int64', 'float64'])
        corr = numerical.corr()
        return corr

    # Function to create download link for JSON
    def create_download_link_json(data, filename, text):
        json_str = json.dumps(data, indent=4)
        b64 = base64.b64encode(json_str.encode()).decode()  # Encode to base64
        href = f'<a href="data:file/json;base64,{b64}" download="{filename}">{text}</a>'
        return href

    # Streamlit App
    st.title("Synthetic Data Quality Assessment")

    st.markdown("""
    This application allows you to upload and compare real and synthetic datasets.
    It provides comprehensive metrics and visualizations to assess the quality of your synthetic data.
    """)

    # File uploaders
    uploaded_real = st.file_uploader("Upload your real dataset (CSV)", type="csv", key="real")
    uploaded_synthetic = st.file_uploader("Upload your synthetic dataset (CSV)", type="csv", key="synthetic")

    if uploaded_real is not None and uploaded_synthetic is not None:
        # Read datasets
        try:
            real_data = pd.read_csv(uploaded_real)
            synthetic_data = pd.read_csv(uploaded_synthetic)
        except Exception as e:
            st.error(f"Error reading CSV files: {e}")
            st.stop()

        # Detect categorical columns in real data
        categorical_features = detect_categorical_columns(real_data)

        # Create Tabs for Organization
        tabs = st.tabs(["Data Previews", "Data Quality Metrics", "Visualizations", "Download"])

        with tabs[0]:
            st.header("Data Previews")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Real Dataset Preview")
                st.dataframe(real_data.head(), height=300)
            with col2:
                st.subheader("Synthetic Dataset Preview")
                st.dataframe(synthetic_data.head(), height=300)

        with tabs[1]:
            st.header("Data Quality Metrics")

            metrics_tabs = st.tabs(["General Metrics", "Missing Values", "Numerical Statistics", "Categorical Statistics", "Correlation Matrix"])

            # General Metrics
            with metrics_tabs[0]:
                st.subheader("General Metrics - Real Data")
                real_general = compute_general_metrics(real_data, "Real")
                st.json(real_general)

                st.subheader("General Metrics - Synthetic Data")
                synthetic_general = compute_general_metrics(synthetic_data, "Synthetic")
                st.json(synthetic_general)

            # Missing Values
            with metrics_tabs[1]:
                st.subheader("Missing Values - Real Data")
                real_missing = compute_missing_values(real_data, "Real")
                st.dataframe(real_missing, height=300)

                st.subheader("Missing Values - Synthetic Data")
                synthetic_missing = compute_missing_values(synthetic_data, "Synthetic")
                st.dataframe(synthetic_missing, height=300)

            # Numerical Statistics
            with metrics_tabs[2]:
                st.subheader("Numerical Statistics - Real Data")
                real_num_stats = compute_numerical_stats(real_data, "Real")
                st.dataframe(real_num_stats, height=300)

                st.subheader("Numerical Statistics - Synthetic Data")
                synthetic_num_stats = compute_numerical_stats(synthetic_data, "Synthetic")
                st.dataframe(synthetic_num_stats, height=300)

            # Categorical Statistics
            with metrics_tabs[3]:
                if categorical_features:
                    st.subheader("Categorical Statistics - Real Data")
                    real_cat_stats = compute_categorical_stats(real_data, categorical_features, "Real")
                    for col, df_stats in real_cat_stats.items():
                        with st.expander(f"Categorical Statistics for '{col}' - Real Data"):
                            st.table(df_stats)

                    st.subheader("Categorical Statistics - Synthetic Data")
                    synthetic_cat_stats = compute_categorical_stats(synthetic_data, categorical_features, "Synthetic")
                    for col, df_stats in synthetic_cat_stats.items():
                        with st.expander(f"Categorical Statistics for '{col}' - Synthetic Data"):
                            st.table(df_stats)
                else:
                    st.write("No categorical features detected in the real dataset.")

            # Correlation Matrix
            with metrics_tabs[4]:
                st.subheader("Correlation Matrix - Real Data")
                real_corr = compute_correlation_matrix(real_data, "Real")
                if not real_corr.empty:
                    fig_real_corr = px.imshow(real_corr, text_auto=True, aspect="auto", title="Real Data Correlation Matrix")
                    st.plotly_chart(fig_real_corr, use_container_width=True)
                else:
                    st.write("No numerical features available to compute correlation matrix for Real Data.")

                st.subheader("Correlation Matrix - Synthetic Data")
                synthetic_corr = compute_correlation_matrix(synthetic_data, "Synthetic")
                if not synthetic_corr.empty:
                    fig_synthetic_corr = px.imshow(synthetic_corr, text_auto=True, aspect="auto", title="Synthetic Data Correlation Matrix")
                    st.plotly_chart(fig_synthetic_corr, use_container_width=True)
                else:
                    st.write("No numerical features available to compute correlation matrix for Synthetic Data.")

        with tabs[2]:
            st.header("Visualizations")

            # Create Sub-tabs for Different Visualizations
            viz_tabs = st.tabs(["Numerical Feature Distributions", "Categorical Feature Distributions"])

            # Numerical Feature Distributions
            with viz_tabs[0]:
                numerical_cols = real_data.select_dtypes(include=['int64', 'float64']).columns.tolist()
                if numerical_cols:
                    for col in numerical_cols:
                        with st.expander(f"Distribution of '{col}'"):
                            fig, ax = plt.subplots(figsize=(6, 4))
                            ax.hist(real_data[col].dropna(), bins=30, alpha=0.5, label='Real', color='blue')
                            ax.hist(synthetic_data[col].dropna(), bins=30, alpha=0.5, label='Synthetic', color='orange')
                            ax.set_title(f'Distribution of {col}')
                            ax.set_xlabel(col)
                            ax.set_ylabel('Frequency')
                            ax.legend()
                            st.pyplot(fig)
                else:
                    st.write("No numerical features available for histogram visualization.")

            # Categorical Feature Distributions
            with viz_tabs[1]:
                if categorical_features:
                    for col in categorical_features:
                        with st.expander(f"Value Counts for '{col}'"):
                            # Align categories between real and synthetic data
                            real_counts = real_data[col].value_counts(dropna=False)
                            synthetic_counts = synthetic_data[col].value_counts(dropna=False).reindex(real_counts.index, fill_value=0)
                            cat_df = pd.DataFrame({
                                'Category': real_counts.index.astype(str),
                                'Real': real_counts.values,
                                'Synthetic': synthetic_counts.values
                            })

                            fig = px.bar(
                                cat_df,
                                x='Category',
                                y=['Real', 'Synthetic'],
                                barmode='group',
                                title=f'Value Counts for {col}',
                                labels={'value': 'Count', 'Category': col}
                            )
                            st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write("No categorical features available for bar chart visualization.")

        with tabs[3]:
            st.header("Download Metrics Report")

            all_metrics = {
                "General Metrics - Real": real_general,
                "General Metrics - Synthetic": synthetic_general,
                "Missing Values - Real": real_missing.to_dict(orient='records'),
                "Missing Values - Synthetic": synthetic_missing.to_dict(orient='records'),
                "Numerical Statistics - Real": real_num_stats.reset_index().to_dict(orient='records'),
                "Numerical Statistics - Synthetic": synthetic_num_stats.reset_index().to_dict(orient='records')
                # You can add more metrics here if needed
            }

            # Convert metrics to JSON for download
            metrics_json = json.dumps(all_metrics, indent=4)

            # Create a download link for JSON
            download_link = create_download_link_json(metrics_json, "data_quality_metrics.json", "Download Metrics as JSON")
            st.markdown(download_link, unsafe_allow_html=True)

        # with tabs[4]:
        #     st.header("Privacy Analysis")
        #     st.markdown("""
        #     **Note:** This application provides a basic assessment of data quality between real and synthetic datasets.
        #     For comprehensive privacy risk analysis, consider implementing advanced techniques such as:
        #     - **Attribute Disclosure Evaluation:** Assess the risk of sensitive attributes being exposed.
        #     - **Membership Inference Attacks:** Determine if an attacker can infer whether a specific record was part of the training data.
        #     - **Differential Privacy:** Apply mathematical frameworks to provide guarantees about the privacy of individual records.
            
        #     These methods require specialized tools and algorithms beyond the scope of this application.
        #     """)

    # To run the app directly, you can uncomment the following lines:
    # if __name__ == "__main__":
    #     app()

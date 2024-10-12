import os
import streamlit as st
import pandas as pd
from Levenshtein import distance  # For Levenshtein distance calculation
import joblib  # For loading the models
import pickle  
from io import BytesIO, StringIO
from ctgan import CTGAN

# Function to automatically detect categorical columns
def detect_categorical_columns(df):
    return df.select_dtypes(include=['object', 'category']).columns.tolist()

def app():
    # Dropdown to select between "General" or "Specific" synthesizer
    synthesizer_type = st.selectbox(
        "Select the type of synthesizer",
        options=["General Health Record Synthesizer", "Specific Record Synthesizer"]
    )

    # Path to the models directory
    models_dir = r'data_synthesis_and_personalized_treatment\models'

    if synthesizer_type == "General Health Record Synthesizer":
        # Load unique conditions from the pickle file in the models directory
        conditions_filename = os.path.join(models_dir, 'unique_conditions.pkl')
        with open(conditions_filename, 'rb') as f:
            unique_conditions = pickle.load(f)

        # Function to find the most similar condition using Levenshtein distance
        def find_most_similar_condition(user_input, conditions):
            closest_condition = min(conditions, key=lambda x: distance(user_input.lower(), x.lower()))
            return closest_condition

        # Streamlit UI setup
        st.title("General Health Record Synthesizer")
        st.write("Generate synthetic medical records based on disease/condition using CT-GAN models")

        # User input for condition and number of records
        user_input = st.text_input("Enter the disease/condition you want to research:")
        num_records = st.number_input("Enter the number of synthetic records you want to generate:", min_value=1, max_value=1000, value=10)

        # Button to submit and generate the data
        if st.button("Generate Data"):
            if user_input and num_records:
                # Find the most similar condition
                closest_condition = find_most_similar_condition(user_input, unique_conditions)
                st.write(f"Most similar condition found: **{closest_condition}**")

                # Load the CTGAN model for the closest condition
                model_filename = os.path.join(models_dir, f'ctgan_model_{closest_condition}.pkl')
                model = joblib.load(model_filename)
                st.write(f"Model for condition '{closest_condition}' loaded successfully.")

                # Generate synthetic data
                synthetic_data = model.sample(num_records)

                # Filter synthetic data for the closest condition
                filtered_synthetic_data = synthetic_data[synthetic_data['Condition'] == closest_condition]

                # Show a preview of the generated synthetic data
                st.write("Preview of the generated synthetic data:")
                st.dataframe(filtered_synthetic_data.head())  # Show only the first few rows

                # Save the filtered data to a CSV file in memory for download
                buffer = BytesIO()
                filtered_synthetic_data.to_csv(buffer, index=False)
                buffer.seek(0)

                # Download button for the user to download the synthetic data as a CSV
                st.download_button(
                    label="Download Synthetic Data",
                    data=buffer,
                    file_name=f"synthetic_data_{closest_condition}.csv",
                    mime="text/csv"
                )
            else:
                st.write("Please enter a valid condition and number of records.")

    elif synthesizer_type == "Specific Record Synthesizer":
        st.title("Specific Record Synthesizer with CT-GAN")

        # File upload
        uploaded_file = st.file_uploader("Upload your dataset (CSV)", type="csv")
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Dataset preview:")
            st.write(df.head())

            # Let users select sensitive/private columns to remove
            sensitive_columns = st.multiselect(
                "Select any sensitive or private columns to exclude from the dataset",
                options=df.columns.tolist(),
                help="These columns will be removed before generating synthetic data."
            )

            # Remove sensitive columns from the dataset
            if sensitive_columns:
                st.write(f"Removing the following sensitive columns: {sensitive_columns}")
                df = df.drop(columns=sensitive_columns)

            # Automatically detect categorical features
            categorical_features = detect_categorical_columns(df)
            st.write(f"Detected categorical features: {categorical_features}")

            # Check if a condition column exists
            condition_column = st.selectbox(
                "Select the column to base conditional models on (optional)",
                options=[None] + df.columns.tolist(),
                help="If selected, CTGAN will train a separate model for each unique value in this column."
            )

            # Get the number of synthetic rows to generate
            num_rows = st.number_input("Number of synthetic data rows to generate", min_value=1, value=100, step=1)

            # Start synthetic data generation when button is clicked
            if st.button("Generate Synthetic Data"):
                st.write("Training CTGAN model...")

                # Path to the models directory
                os.makedirs(models_dir, exist_ok=True)

                # Train CTGAN model based on condition (if provided)
                if condition_column:
                    unique_conditions = df[condition_column].unique()

                    # Initialize a dictionary to store synthetic data for each condition
                    synthetic_data_dict = {}

                    # Train a model for each unique condition
                    for condition in unique_conditions:
                        st.write(f"Training CTGAN model for condition: {condition}")
                        
                        # Filter the data for the current condition
                        condition_df = df[df[condition_column] == condition]
                        
                        # Train the CTGAN model
                        model = CTGAN()
                        model.fit(condition_df, categorical_features, epochs=5)
                        
                        # Save the trained model for the current condition in the models directory
                        model_filename = os.path.join(models_dir, f'ctgan_model_{condition}.pkl')
                        joblib.dump(model, model_filename)
                        
                        # Generate synthetic data for the current condition
                        synthetic_data = model.sample(num_rows)
                        synthetic_data_dict[condition] = synthetic_data
                        
                        # Display preview for each condition
                        st.write(f"Synthetic Data Preview for condition: {condition}")
                        st.write(synthetic_data.head())

                        # Convert synthetic data to CSV format for download
                        csv_buffer = StringIO()
                        synthetic_data.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()

                        # Provide a download button for each condition
                        st.download_button(
                            label=f"Download synthetic data for condition: {condition}",
                            data=csv_data,
                            file_name=f'synthetic_data_{condition}.csv',
                            mime='text/csv'
                        )
                else:
                    # No conditional column: Train a single CTGAN model for the entire dataset
                    model = CTGAN()
                    model.fit(df, categorical_features, epochs=5)

                    # Save the trained model
                    model_filename = os.path.join(models_dir, 'ctgan_model.pkl')
                    joblib.dump(model, model_filename)
                    st.write("CTGAN model training completed.")

                    # Generate synthetic data
                    st.write(f"Generating {num_rows} synthetic rows...")
                    synthetic_data = model.sample(num_rows)

                    # Display synthetic data
                    st.write("Synthetic Data Preview:")
                    st.write(synthetic_data.head())

                    # Convert synthetic data to CSV format for download
                    csv_buffer = StringIO()
                    synthetic_data.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()

                    # Provide a download button
                    st.download_button(
                        label="Download synthetic data as CSV",
                        data=csv_data,
                        file_name='synthetic_data.csv',
                        mime='text/csv'
                    )

import os
import pandas as pd
from ctgan import CTGAN
import joblib  # For saving the models
import pickle  # For saving unique conditions

# Path to the models directory
models_dir = r'models'

# Ensure the models directory exists
os.makedirs(models_dir, exist_ok=True)

# Load the dataset
df = pd.read_csv(r'datasets/hospital_data.csv')
df = df.drop(columns=['Patient_ID'])

# Define categorical features
categorical_features = ['Gender', 'Procedure', 'Readmission', 'Outcome', 'Satisfaction', 'Condition']

# Get unique conditions
unique_conditions = df['Condition'].unique()

# Save the unique conditions to a pickle file
conditions_filename = os.path.join(models_dir, 'unique_conditions.pkl')
with open(conditions_filename, 'wb') as f:
    pickle.dump(unique_conditions, f)
print(f"Unique conditions saved to: {conditions_filename}")

# Train a separate CTGAN model for each condition
for condition in unique_conditions:
    print(f"Training CTGAN model for condition: {condition}")
    
    # Filter the data for the current condition
    condition_df = df[df['Condition'] == condition]
    
    # Train the CTGAN model
    model = CTGAN()
    model.fit(condition_df, categorical_features, epochs=2)  # Train for 20 epochs
    
    # Save the trained model for the current condition in the models directory
    model_filename = os.path.join(models_dir, f'ctgan_model_{condition}.pkl')
    joblib.dump(model, model_filename)

print("Training for all conditions completed.")

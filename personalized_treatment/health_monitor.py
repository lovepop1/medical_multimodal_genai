import streamlit as st

def health_monitor(user_data):
    st.subheader("Health Monitoring Dashboard")
    
    # Fetch user information from the passed data
    name = user_data.get("name", "N/A")
    age = user_data.get("age", "N/A")
    height = user_data.get("height", "N/A")
    weight = user_data.get("weight", "N/A")
    bmi = user_data.get("bmi", "N/A")
    allergies = user_data.get("allergies", "None")
    current_medications = user_data.get("current_medications", "None")
    previous_conditions = user_data.get("previous_conditions", "None")
    previous_medications = user_data.get("previous_medications", "None")
    visited_doctors = user_data.get("visited_doctors", "None")
    
    # Lifestyle information
    smoking_habits = user_data.get("smoking_habits", "N/A")
    drinking_habits = user_data.get("drinking_habits", "N/A")
    exercise_frequency = user_data.get("exercise_frequency", "N/A")
    sleep_duration = user_data.get("sleep_duration", "N/A")
    current_diet = user_data.get("current_diet", "N/A")
    family_medical_history = user_data.get("family_medical_history", "N/A")
    
    # Display user personal details
    st.write(f"### Personal Information for {name}")
    st.write(f"**Age**: {age}")
    st.write(f"**Height**: {height} cm")
    st.write(f"**Weight**: {weight} kg")
    st.write(f"**BMI**: {bmi:.2f}" if isinstance(bmi, (int, float)) else f"**BMI**: {bmi}")
    
    # Analyze BMI
    if isinstance(bmi, (int, float)):
        if bmi < 18.5:
            st.warning("You are underweight according to your BMI. Consider consulting a dietitian.")
        elif 18.5 <= bmi < 24.9:
            st.success("You have a normal BMI. Keep maintaining a healthy lifestyle!")
        elif 25 <= bmi < 29.9:
            st.warning("You are overweight according to your BMI. Consider adopting a balanced diet and exercise plan.")
        else:
            st.error("You are in the obese range according to your BMI. It's important to consult a healthcare provider for guidance.")

    # Display health information
    st.write("### Medical Information")
    st.write(f"**Allergies**: {allergies}")
    st.write(f"**Current Medications**: {current_medications}")
    st.write(f"**Previous Conditions**: {previous_conditions}")
    st.write(f"**Previous Medications**: {previous_medications}")
    st.write(f"**Doctors Visited**: {visited_doctors}")
    
    # Display lifestyle information
    st.write("### Lifestyle Habits")
    st.write(f"**Smoking Habits**: {smoking_habits}")
    st.write(f"**Drinking Habits**: {drinking_habits}")
    st.write(f"**Exercise Frequency**: {exercise_frequency}")
    st.write(f"**Sleep Duration**: {sleep_duration} hours/night")
    st.write(f"**Current Diet**: {current_diet}")
    st.write(f"**Family Medical History**: {family_medical_history}")
    
    st.write("**Keep monitoring your health regularly and consult a healthcare professional if needed.**")

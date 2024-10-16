

def app():
    import streamlit as st
    from personalized_treatment.firebaseConfig import auth, db  # Import Firebase authentication and database
    from personalized_treatment.medical_chatbot import medical_chatbot  # Import your chatbot function
    from personalized_treatment.monthly_goals import monthly_goals
    from personalized_treatment.diet import diet
    from personalized_treatment.workout import workout
    from personalized_treatment.health_monitor import health_monitor
    # Streamlit UI for Personal Medical Assistant
    st.title("Personal Medical Assistant")

    # Application state to manage user sessions and form progression
    if 'user' not in st.session_state:
        st.session_state['user'] = None  # Store the user session
    if 'page' not in st.session_state:
        st.session_state['page'] = "Medical Chatbot"  # Default page is the Medical Chatbot

    # Function to handle login
    def login_user(email, password):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state['user'] = user  # Save logged-in user to session state

            # Fetch the user's personal details from the database using their user ID
            user_id = user['localId']
            user_data = db.child("users").child(user_id).get().val()
            if user_data and 'name' in user_data:
                st.session_state['user_name'] = user_data['name']
                st.session_state['user_data'] = user_data  # Save user data for chatbot
                st.success(f"Welcome, {user_data['name']}!")  # Personalized welcome message
            else:
                st.success(f"Welcome, {email}!")  # Fallback to email if name is not available
            return user
        except Exception as e:
            st.error(f"Error: {e}")
            return None

    # Function to handle sign-up
    def signup_user(email, password):
        try:
            # Create the user account in Firebase
            user = auth.create_user_with_email_and_password(email, password)
            return user
        except Exception as e:
            st.error(f"Error: {e}")
            return None

    # Function to store user data in Realtime Database
    def store_user_data(user_id, user_data):
        try:
            db.child("users").child(user_id).set(user_data)  # Store data under user's unique ID
            st.success("Data saved successfully!")
        except Exception as e:
            st.error(f"Error saving data: {e}")

    # Function to handle logout
    def logout_user():
        st.session_state['user'] = None  # Reset user session
        st.success("Logged out successfully!")

    # Main layout and navigation bar
    if st.session_state['user']:
        # Horizontal navigation bar with six options
        menu_options = ["Medical Chatbot", "Monthly Goals", "Diet", "Health Monitoring", "Workout Plan"]
        user_name = st.session_state['user_data'].get('name', st.session_state['user']['email'])  # Use name if available, otherwise fallback to email
        st.write(f"Welcome, {user_name}")
        
        # Create the horizontal menu bar
        selected_option = st.selectbox("Select a feature", menu_options, key="page", format_func=lambda x: x)
        
        # Page selection logic
        if selected_option == "Medical Chatbot":
            st.header("Medical Chatbot")
            if 'user_data' in st.session_state:
                medical_chatbot(st.session_state['user_data'])  # Call chatbot function with user data
            else:
                st.warning("No user data available for the chatbot.")
        
        elif selected_option == "Monthly Goals":
            if 'user_data' in st.session_state:
                monthly_goals(st.session_state['user_data'])  # Call chatbot function with user data
            else:
                st.warning("No user data available for the chatbot.")

        elif selected_option == "Diet":
            st.header("Diet")
            if 'user_data' in st.session_state:
                diet(st.session_state['user_data'])  # Call chatbot function with user data
            else:
                st.warning("No user data available for the chatbot.")
        
        elif selected_option == "Health Monitoring":
            if 'user_data' in st.session_state:
                health_monitor(st.session_state['user_data'])  # Call chatbot function with user data
            else:
                st.warning("No user data available for the chatbot.")
        
        elif selected_option == "Workout Plan":
            st.header("Workout Plan")
            if 'user_data' in st.session_state:
                workout(st.session_state['user_data'])  # Call chatbot function with user data
            else:
                st.warning("No user data available for the chatbot.")
        
        # Add a logout button
        if st.button("Logout"):
            logout_user()
            st.rerun()  # Force rerun to refresh the UI

    else:
        option = st.selectbox("Choose an option", ["Login", "Sign Up"])

        if option == "Login":
            st.subheader("Login")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                user = login_user(email, password)
                if user:  # Only rerun if login was successful
                    st.rerun()

        elif option == "Sign Up":
            # Handle the multi-step sign-up process
            if 'step' not in st.session_state:
                st.session_state['step'] = 1

            if st.session_state['step'] == 1:
                st.subheader("Create New Account")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")

                if password == confirm_password and len(password)>6:
                    if st.button("Next"):
                        st.session_state['step'] = 2
                        st.session_state['user_data'] = {"email": email, "password": password}
                        st.rerun()
                else:
                    st.warning("Passwords do not match or password length less than 6 characters.")

            elif st.session_state['step'] == 2:
                st.subheader("User Information")
                name = st.text_input("Full Name")
                age = st.number_input("Age", min_value=0, max_value=120)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"])

                if st.button("Next"):
                    st.session_state['user_data'].update({"name": name, "age": age, "gender": gender})
                    st.session_state['step'] = 3
                    st.rerun()

            elif st.session_state['step'] == 3:
                st.subheader("Medical Information")
                height = st.number_input("Height (in cm)", min_value=0)
                weight = st.number_input("Weight (in kg)", min_value=0)
                bmi = weight / ((height / 100) ** 2) if height > 0 else 0
                allergies = st.text_area("Known Allergies (if any)")
                current_medications = st.text_area("Current Medications (if any)")
                previous_conditions = st.text_area("Previous Medical Conditions")
                previous_medications = st.text_area("Previous Medications Used")
                visited_doctors = st.text_area("Doctors Visited (if any)")

                if st.button("Next"):
                    st.session_state['user_data'].update({
                        "height": height,
                        "weight": weight,
                        "bmi": bmi,
                        "allergies": allergies,
                        "current_medications": current_medications,
                        "previous_conditions": previous_conditions,
                        "previous_medications": previous_medications,
                        "visited_doctors": visited_doctors
                    })
                    st.session_state['step'] = 4
                    st.rerun()

            elif st.session_state['step'] == 4:
                st.subheader("Lifestyle Information")
                smoking_habits = st.selectbox("Do you smoke?", ["Yes", "No", "Occasionally"])
                drinking_habits = st.selectbox("Do you drink alcohol?", ["Yes", "No", "Occasionally"])
                exercise_frequency = st.selectbox("How often do you exercise?", ["Daily", "Weekly", "Rarely", "Never"])
                sleep_duration = st.slider("Average hours of sleep per night", min_value=0, max_value=12, step=1)
                current_diet = st.text_area("Current Diet (describe your daily meals)")
                family_medical_history = st.text_area("Family Medical History (if any)")

                if st.button("Next"):
                    st.session_state['user_data'].update({
                        "smoking_habits": smoking_habits,
                        "drinking_habits": drinking_habits,
                        "exercise_frequency": exercise_frequency,
                        "sleep_duration": sleep_duration,
                        "current_diet": current_diet,
                        "family_medical_history": family_medical_history
                    })
                    st.session_state['step'] = 5
                    st.rerun()

            elif st.session_state['step'] == 5:
                st.subheader("Review & Submit")
                st.write("### Personal Information")
                st.write(f"Name: {st.session_state['user_data']['name']}")
                st.write(f"Age: {st.session_state['user_data']['age']}")
                st.write(f"Gender: {st.session_state['user_data']['gender']}")

                st.write("### Medical Information")
                st.write(f"Height: {st.session_state['user_data']['height']} cm")
                st.write(f"Weight: {st.session_state['user_data']['weight']} kg")
                st.write(f"BMI: {st.session_state['user_data']['bmi']:.2f}")
                st.write(f"Allergies: {st.session_state['user_data']['allergies']}")
                st.write(f"Current Medications: {st.session_state['user_data']['current_medications']}")
                st.write(f"Previous Medical Conditions: {st.session_state['user_data']['previous_conditions']}")
                st.write(f"Doctors Visited: {st.session_state['user_data']['visited_doctors']}")

                st.write("### Lifestyle Information")
                st.write(f"Smoking: {st.session_state['user_data']['smoking_habits']}")
                st.write(f"Drinking: {st.session_state['user_data']['drinking_habits']}")
                st.write(f"Exercise: {st.session_state['user_data']['exercise_frequency']}")
                st.write(f"Sleep: {st.session_state['user_data']['sleep_duration']} hours")
                st.write(f"Diet: {st.session_state['user_data']['current_diet']}")
                st.write(f"Family Medical History: {st.session_state['user_data']['family_medical_history']}")

                if st.button("Submit"):
                    user = signup_user(st.session_state['user_data']['email'], st.session_state['user_data']['password'])
                    if user:
                        user_id = user['localId']
                        store_user_data(user_id, st.session_state['user_data'])  # Store all collected data to Firebase
                        st.session_state['user'] = user  # Log in the newly registered user
                        st.rerun()  # Go to home page after submission

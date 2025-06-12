import streamlit as st
import streamlit_authenticator as stauth
import json
from datetime import datetime, timedelta

# ---- Hash passwords ----
hashed_passwords = [
    '$2b$12$U1hvqFGOFXh/ybpLb3g9muJzJvT6A5cGBsK5QaQAlRwL8KhPvW25a',  # admin_pass
    '$2b$12$Pf37xgJ8IBaeSWTzGaBeVuW38.fKLUFo1EJmXkczK9dw5aSjcChmq',  # user1_pass
]

# ---- Credentials Configuration ----
credentials = {
    "usernames": {
        "admin": {
            "email": "admin@example.com",
            "name": "Administrator",
            "password": hashed_passwords[0],
        },
        "user1": {
            "email": "user1@example.com",
            "name": "User One",
            "password": hashed_passwords[1],
        }
    }
}

# ---- Authenticator Object ----
authenticator = stauth.Authenticate(
    credentials,
    "habit_tracker_app",  # Cookie name
    "abcdef",             # Cookie key (secret)
    cookie_expiry_days=7  # Cookie expiration duration in days
)

# ---- User Login ----
name, authentication_status, username = authenticator.login("Login", location="main")

# ---- Authentication Handling ----
if authentication_status is False:
    st.error("Username/password is incorrect")

if authentication_status is None:
    st.warning("Please enter your username and password")

if authentication_status:
    st.success(f"Welcome {name} 👋")

    # ---- Main App Menu ----
    menu = ["Home", "Track Habits", "View Progress", "Settings"]
    choice = st.sidebar.selectbox("Choose an option", menu)

    # ---- Load user data from JSON file ----
    try:
        with open('user_data.json', 'r') as file:
            user_data = json.load(file)
    except FileNotFoundError:
        user_data = {}

    if username not in user_data:
        user_data[username] = {
            "user_name": name,
            "goals": ["Workout", "Business Creation", "Reading", "Meditation"],
            "daily_progress": {}
        }

    # ---- Handle Menu Choices ----
    if choice == "Home":
        st.title("Welcome to the Habit Tracker!")
        st.write(f"Hello {name}, start tracking your habits and stay consistent!")

    elif choice == "Track Habits":
        st.title("Track Your Habits")
        
        # Track today's date and progress
        today = datetime.today().strftime('%Y-%m-%d')

        if today not in user_data[username]["daily_progress"]:
            user_data[username]["daily_progress"][today] = {goal: False for goal in user_data[username]["goals"]}

        st.write(f"Today’s date: {today}")
        for goal in user_data[username]["goals"]:
            completed = st.checkbox(f"Did you complete: {goal}?", key=f"{goal}_{today}")
            user_data[username]["daily_progress"][today][goal] = completed

        if st.button("Save Progress"):
            # Save data back to the JSON file
            with open('user_data.json', 'w') as file:
                json.dump(user_data, file)
            st.success("Progress saved successfully!")

    elif choice == "View Progress":
        st.title("Your Habit Progress")

        # Show the user's progress for the past week
        today = datetime.today()
        st.write(f"Here’s your progress for the last week, {name}:")

        for i in range(7):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            st.write(f"**{date}:**")
            if date in user_data[username]["daily_progress"]:
                for goal, status in user_data[username]["daily_progress"][date].items():
                    st.write(f"  - {goal}: {'✅' if status else '❌'}")
            else:
                st.write("  - No progress logged")

    elif choice == "Settings":
        st.title("Settings")

        # Update goals
        new_goals = st.text_input("Update your goals (comma-separated)", ', '.join(user_data[username]["goals"]))
        if new_goals:
            user_data[username]["goals"] = [goal.strip() for goal in new_goals.split(",")]
            with open('user_data.json', 'w') as file:
                json.dump(user_data, file)
            st.success("Goals updated successfully!")

    # ---- Logout ----
    if st.button("Logout"):
        authenticator.logout("Logout", location="main")
        st.experimental_rerun()


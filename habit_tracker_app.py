import streamlit as st
import streamlit_authenticator as stauth
import json
from datetime import datetime, timedelta
import os

# ---- Helper functions ----

# Function to load user data from a file
def load_user_data(username):
    user_data_path = f"user_data/{username}.json"
    if os.path.exists(user_data_path):
        with open(user_data_path, 'r') as f:
            return json.load(f)
    return {"user_name": username, "goals": [], "daily_progress": {}}

# Function to save user data to a file
def save_user_data(username, user_data):
    user_data_path = f"user_data/{username}.json"
    with open(user_data_path, 'w') as f:
        json.dump(user_data, f, indent=4)

# ---- Main Streamlit App ----

# Hashed passwords (use stauth.Hasher(['password1', 'password2']).generate())
hashed_passwords = [
    '$2b$12$U1hvqFGOFXh/ybpLb3g9muJzJvT6A5cGBsK5QaQAlRwL8KhPvW25a',  # admin_pass
    '$2b$12$Pf37xgJ8IBaeSWTzGaBeVuW38.fKLUFo1EJmXkczK9dw5aSjcChmq',  # user1_pass
]

# Credentials config
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

# Set up authenticator
authenticator = stauth.Authenticate(
    credentials,
    "habit_tracker_app",  # Cookie name
    "abcdef",             # Cookie key (secret)
    cookie_expiry_days=7
)

# ---- Login ----
name, authentication_status, username = authenticator.login("Login")

if authentication_status is False:
    st.error("Username/password is incorrect")

if authentication_status is None:
    st.warning("Please enter your username and password")

if authentication_status:
    st.success(f"Welcome {name} 👋")

    # Load user data
    user_data = load_user_data(username)
    
    # ---- Habit Tracking ----
    st.header(f"Welcome to your habit tracker, {name}!")
    
    # Allow the user to set goals
    st.subheader("Set Your Goals:")
    goals = st.text_area("Enter your goals (comma separated)", 
                         value=", ".join(user_data.get("goals", [])))
    
    if st.button("Save Goals"):
        goals_list = [goal.strip() for goal in goals.split(",")]
        user_data["goals"] = goals_list
        save_user_data(username, user_data)
        st.success("Goals saved successfully!")

    # Show the user's goals
    st.subheader("Your Current Goals:")
    for goal in user_data.get("goals", []):
        st.write(f"- {goal}")

    # ---- Daily Progress ----
    st.subheader("Track Your Daily Progress")
    today = datetime.today().strftime('%Y-%m-%d')

    # Load today's progress or initialize
    daily_progress = user_data["daily_progress"].get(today, {goal: False for goal in user_data.get("goals", [])})

    # Create checkboxes for each goal
    for goal in user_data.get("goals", []):
        daily_progress[goal] = st.checkbox(f"Did you accomplish: {goal}", value=daily_progress[goal])

    # Save today's progress
    if st.button("Save Today's Progress"):
        user_data["daily_progress"][today] = daily_progress
        save_user_data(username, user_data)
        st.success("Your progress for today has been saved!")

    # ---- View Past Progress ----
    st.subheader("View Your Past Progress")

    # Let user select a date
    date_selected = st.date_input("Pick a date", datetime.today())
    selected_date = date_selected.strftime('%Y-%m-%d')

    if selected_date in user_data["daily_progress"]:
        st.write(f"Progress for {selected_date}:")
        for goal, completed in user_data["daily_progress"][selected_date].items():
            status = "Completed" if completed else "Not Completed"
            st.write(f"- {goal}: {status}")
    else:
        st.warning(f"No data available for {selected_date}")

    # ---- Motivational Messages ----
    st.subheader("Stay Consistent!")
    st.write("Consistency is the key to success. Keep working on your goals every day!")
    
    # Show motivational quote or message (you can expand this to random quotes)
    st.write("\"The journey of a thousand miles begins with one step.\" - Lao Tzu")

# ---- User Logout ----
if st.button("Logout"):
    authenticator.logout("Logout", "main")
    st.success("Logged out successfully!")

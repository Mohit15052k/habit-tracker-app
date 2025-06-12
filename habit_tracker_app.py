import streamlit as st
import streamlit_authenticator as stauth
from datetime import datetime, timedelta
import pickle

# Hashed passwords (use stauth.Hasher(['pass1', 'pass2']).generate())
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

authenticator = stauth.Authenticate(
    credentials,
    "habit_tracker_app",  # Cookie name
    "abcdef",             # Cookie key (secret)
    cookie_expiry_days=7
)

# ---- Login ----
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status is False:
    st.error("Username/password is incorrect")

if authentication_status is None:
    st.warning("Please enter your username and password")

if authentication_status:
    # Display user-oriented menu
    st.success(f"Welcome {name} 👋")
    
    # Habit data stored in session state for 7 days
    if 'habit_data' not in st.session_state:
        st.session_state.habit_data = {}

    def add_habit():
        habit_name = st.text_input("Enter habit name")
        if st.button("Add Habit") and habit_name:
            if habit_name not in st.session_state.habit_data:
                st.session_state.habit_data[habit_name] = {
                    "streak": 0,
                    "last_done": None
                }
                st.success(f"Habit '{habit_name}' added!")

    def mark_habit_done():
        habit_name = st.selectbox("Select habit to mark as done", list(st.session_state.habit_data.keys()))
        if st.button(f"Mark {habit_name} as done"):
            habit_data = st.session_state.habit_data[habit_name]
            habit_data["last_done"] = datetime.now()
            habit_data["streak"] += 1
            st.session_state.habit_data[habit_name] = habit_data
            st.success(f"Marked '{habit_name}' as done today!")

    def view_habits():
        if len(st.session_state.habit_data) == 0:
            st.write("No habits found.")
        else:
            for habit, data in st.session_state.habit_data.items():
                st.write(f"**{habit}** - Streak: {data['streak']} days")
                if data['last_done']:
                    st.write(f"Last done: {data['last_done'].strftime('%Y-%m-%d')}")
                else:
                    st.write("Not tracked yet")

    def logout():
        authenticator.logout("Logout", "sidebar")
        st.session_state.habit_data = {}

    # Menu options
    menu = ["Home", "Add Habit", "Track Habits", "View Habits", "Logout"]
    choice = st.sidebar.selectbox("Select an option", menu)

    if choice == "Home":
        st.write("Welcome to the Habit Tracker App!")
        st.write("Manage your habits and track your consistency.")

    elif choice == "Add Habit":
        add_habit()

    elif choice == "Track Habits":
        mark_habit_done()

    elif choice == "View Habits":
        view_habits()

    elif choice == "Logout":
        logout()


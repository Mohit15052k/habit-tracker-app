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
    st.error("Username/password is inco

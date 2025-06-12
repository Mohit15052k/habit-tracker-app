import streamlit as st
import datetime
import random
import pandas as pd
import json
import os
import base64
import calendar
import streamlit_authenticator as stauth # NEW: Import authenticator
from yaml.loader import SafeLoader # NEW: For authenticator config
import yaml # NEW: For authenticator config

st.set_page_config(page_title="Your App Title", layout="centered")
# --- Configuration and File Paths ---
APP_TITLE = "Habit Tracker"
DATA_DIR = "data"
QUOTES_FILE = os.path.join(DATA_DIR, "quotes.txt")
USER_DATA_FILE = os.path.join(DATA_DIR, "user_data.json")

# Define paths for background images for each page
BACKGROUND_IMAGES = {
    "Welcome": os.path.join("images", "welcome_bg.jpg"),
    "Goal Tracking": os.path.join("images", "goal_tracking_bg.jpg"),
    "Goal Setting": os.path.join("images", "goal_setting_bg.jpg"),
    "Quote of the Day": os.path.join("images", "quotes_bg.jpg"), # Renamed key
    "Progress Reports": os.path.join("images", "progress_reports_bg.jpg"),
    "Weekly Summary": os.path.join("images", "weekly_summary_bg.jpg"),
    "Default": os.path.join("images", "default_bg.jpg")
}

# --- Ensure Data Directory Exists ---
# NEW: Ensure necessary directories are created
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("images", exist_ok=True)

# --- Pre-hashed passwords (Use Hasher().generate([...]) separately and paste the results here) ---
hashed_passwords = [
    '$2b$12$SOMEHASHEDPASSWORD1...',  # hashed 'admin_pass'
    '$2b$12$SOMEHASHEDPASSWORD2...',  # hashed 'user1_pass'
    '$2b$12$SOMEHASHEDPASSWORD3...'   # hashed 'user2_pass'
]

# --- Credentials Dictionary ---
credentials = {
    "usernames": {
        "admin": {
            "email": "admin@example.com",
            "name": "Administrator",
            "password": hashed_passwords[0]
        },
        "user1": {
            "email": "user1@example.com",
            "name": "Regular User 1",
            "password": hashed_passwords[1]
        },
        "user2": {
            "email": "user2@example.com",
            "name": "Regular User 2",
            "password": hashed_passwords[2]
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "habit_tracker_cookie", # Name of your cookie
    "super_secret_key_change_me_in_production", # Secret key for the cookie. CHANGE THIS!
    cookie_expiry_days=30
)

# --- Helper Functions for Data Persistence (MODIFIED for multi-user) ---
def load_quotes():
    """Loads quotes from the quotes.txt file."""
    try:
        with open(QUOTES_FILE, "r", encoding="utf-8") as f:
            quotes = [line.strip() for line in f if line.strip()]
        return quotes if quotes else ["No quotes found. Please add some to quotes.txt."]
    except FileNotFoundError:
        st.error(f"Error: {QUOTES_FILE} not found. Please create it and add quotes.")
        return ["Error loading quotes."]
    except Exception as e:
        st.error(f"An error occurred while loading quotes: {e}. Please check the file encoding.")
        return ["Error loading quotes."]

# NEW: Loads all user data from the JSON file
def load_all_user_data():
    """Loads all user data from user_data.json."""
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError:
            st.warning("User data file is corrupted. Starting with empty data structure.")
            return {}
        except Exception as e:
            st.warning(f"Error loading all user data: {e}. Starting with empty data structure.")
            return {}
    return {}

# NEW: Saves all user data to the JSON file
def save_all_user_data(all_data):
    """Saves all user data to user_data.json."""
    try:
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving all user data: {e}")

# NEW: Gets data for the currently logged-in user
def get_current_user_data():
    """Retrieves current user's data (goals, daily_progress) from loaded all_user_data."""
    all_data = load_all_user_data()
    current_username = st.session_state.get('authenticated_username')
    if current_username and current_username in all_data:
        return all_data[current_username].get('goals', []), all_data[current_username].get('daily_progress', {})
    return [], {} # Return empty lists if user not found or not logged in

# NEW: Updates and saves data for the currently logged-in user
def update_current_user_data(goals, daily_progress):
    """Updates and saves the current user's goals and daily progress."""
    all_data = load_all_user_data()
    current_username = st.session_state.get('authenticated_username')

    if current_username:
        if current_username not in all_data:
            all_data[current_username] = {} # Initialize if first time for this user
        all_data[current_username]['goals'] = goals
        all_data[current_username]['daily_progress'] = daily_progress
        save_all_user_data(all_data)
    else:
        st.error("Cannot save data: No user is currently authenticated.")

# --- Global Data Loading ---
QUOTES = load_quotes()

# --- Session State Initialization (MODIFIED for multi-user) ---
def init_session_state():
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Welcome"

    # Only load user-specific data AFTER authentication
    if 'authenticated_username' in st.session_state and st.session_state.authenticated_username:
        # Load goals and daily progress for the current user
        st.session_state.goals, st.session_state.daily_progress = get_current_user_data()
    else:
        # If not authenticated, ensure these are empty or not set
        st.session_state.goals = []
        st.session_state.daily_progress = {}

# We will call init_session_state inside the authenticated block now.

# --- Helper Functions ---
def set_page(page_name):
    st.session_state.current_page = page_name

def get_daily_quote():
    today = datetime.date.today().strftime("%Y-%m-%d")
    random.seed(today)
    return random.choice(QUOTES)

def calculate_daily_completion(date_str):
    if date_str not in st.session_state.daily_progress:
        return 0.0
    tracked_goals_for_day = {
        goal: status for goal, status in st.session_state.daily_progress[date_str].items()
        if goal in st.session_state.goals
    }
    completed_goals = sum(1 for status in tracked_goals_for_day.values() if status)
    total_goals_tracked_that_day = len(tracked_goals_for_day)
    if total_goals_tracked_that_day == 0:
        return 0.0
    return (completed_goals / total_goals_tracked_that_day) * 100

def get_progress_color(percentage):
    if percentage >= 76:
        return "green"
    elif percentage >= 51:
        return "orange"
    else:
        return "red"

def get_motivational_message(average_completion):
    # Use st.session_state.user_name which is set by authenticator
    user_name_display = st.session_state.get('user_name', 'Habit Tracker User')
    if average_completion >= 80:
        return (
            f"🚀 **Fantastic work, {user_name_display}!** Your dedication is truly shining through. "
            "Keep this incredible momentum going – you're building habits that will transform your life!"
        )
    elif average_completion >= 50:
        return (
            f"✨ **Great effort, {user_name_display}!** You're consistently showing up, and that's the key. "
            "Remember, every step forward, no matter how small, leads to big changes. You're on the right path!"
        )
    elif st.session_state.goals: # Only show this if goals are set
        return (
            f"💪 **Keep pushing, {user_name_display}!** Even if things felt challenging, remember that consistency beats perfection. "
            "Identify one small change you can make today to get back on track. You've got the power to make it happen!"
        )
    else: # If no goals are set yet for this user
        return (
            f"👋 **Welcome, {user_name_display}!** Ready to unlock your full potential? "
            "Start by setting your first goal on the 'Goal Setting' page. "
            "Small steps lead to big victories!"
        )

# --- Function for Background Image ---
def set_page_background_image(page_name):
    image_path = BACKGROUND_IMAGES.get(page_name, BACKGROUND_IMAGES["Default"])

    ext = os.path.splitext(image_path)[1].lower()
    if ext == '.jpg' or ext == '.jpeg':
        mime_type = 'image/jpeg'
    elif ext == '.png':
        mime_type = 'image/png'
    elif ext == '.webp':
        mime_type = 'image/webp'
    else:
        st.warning(f"Unsupported image type: {ext}. Using default background if available.")
        image_path = BACKGROUND_IMAGES["Default"]
        ext = os.path.splitext(image_path)[1].lower()
        if ext == '.jpg' or ext == '.jpeg': mime_type = 'image/jpeg'
        elif ext == '.png': mime_type = 'image/png'
        elif ext == '.webp': mime_type = 'image/webp'
        else: mime_type = 'image/jpeg'


    try:
        if not os.path.exists(image_path):
            st.warning(f"Background image not found for '{page_name}' at {image_path}. Using default background.")
            image_path = BACKGROUND_IMAGES["Default"]
            ext = os.path.splitext(image_path)[1].lower()
            if ext == '.jpg' or ext == '.jpeg': mime_type = 'image/jpeg'
            elif ext == '.png': mime_type = 'image/png'
            elif ext == '.webp': mime_type = 'image/webp'
            else: mime_type = 'image/jpeg'


        with open(image_path, "rb") as f:
            img_bytes = f.read()
        encoded_image = base64.b64encode(img_bytes).decode()
        
        background_css = f"""
        <style>
        .stApp {{
            background-image: url("data:{mime_type};base64,{encoded_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(background_css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Default background image not found at {image_path}. No background image will be set.")
    except Exception as e:
        st.error(f"An error occurred while setting background image: {e}")


# --- Page Functions ---
def welcome_page():
    # 'st.session_state.user_name' is set by authenticator after login
    st.title(f"Welcome, {st.session_state.get('user_name', 'Habit Tracker User')}!")
    st.markdown("---")

    today = datetime.date.today()
    recent_percentages = []
    # Only calculate if goals exist for the current user
    if st.session_state.goals:
        for i in range(7):
            date_to_check = today - datetime.timedelta(days=i)
            date_str = date_to_check.strftime("%Y-%m-%d")
            # Only consider dates for which there is progress for the current user's goals
            if date_str in st.session_state.daily_progress and any(g in st.session_state.goals for g in st.session_state.daily_progress[date_str]):
                recent_percentages.append(calculate_daily_completion(date_str))

    avg_recent_completion = sum(recent_percentages) / len(recent_percentages) if recent_percentages else 0

    st.markdown(get_motivational_message(avg_recent_completion))
    st.markdown("---")
    st.markdown("Use the sidebar to navigate through the app.")


def goal_setting_page():
    st.title("Goal Setting")
    st.write("Enter your goals one by one. These are habits you want to track.")

    new_goal = st.text_input("New Goal:", key="new_goal_input")
    if st.button("Add Goal"):
        if new_goal and new_goal not in st.session_state.goals:
            st.session_state.goals.append(new_goal)
            # When a new goal is added, ensure it's added to past daily_progress entries as False
            for date_key in st.session_state.daily_progress:
                if new_goal not in st.session_state.daily_progress[date_key]:
                    st.session_state.daily_progress[date_key][new_goal] = False
            # MODIFIED: Use update_current_user_data
            update_current_user_data(st.session_state.goals, st.session_state.daily_progress)
            st.success(f"Goal '{new_goal}' added!")
            st.rerun()
        elif new_goal in st.session_state.goals:
            st.warning("This goal already exists!")
        else:
            st.warning("Please enter a goal.")

    st.subheader("Your Current Goals:")
    if st.session_state.goals:
        goals_copy = st.session_state.goals[:] # Use a copy to iterate while modifying
        for i, goal in enumerate(goals_copy):
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"- {goal}")
            with col2:
                if st.button(f"Remove", key=f"remove_goal_{i}"):
                    st.session_state.goals.remove(goal)
                    # When a goal is removed, also remove it from daily progress entries
                    for date_key in st.session_state.daily_progress:
                        if goal in st.session_state.daily_progress[date_key]:
                            del st.session_state.daily_progress[date_key][goal]
                    # MODIFIED: Use update_current_user_data
                    update_current_user_data(st.session_state.goals, st.session_state.daily_progress)
                    st.success(f"Goal '{goal}' removed.")
                    st.rerun()
    else:
        st.info("No goals set yet. Start by adding some!")

def goal_tracking_page():
    st.title("Goal Tracking for Today")
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    st.write(f"Mark the goals you completed on {today_str}.")

    if not st.session_state.goals:
        st.warning("You haven't set any goals yet! Please go to 'Goal Setting' to add your goals.")
        if st.button("Go to Goal Setting"):
            set_page("Goal Setting")
        return

    # Ensure today's entry exists for the current user
    if today_str not in st.session_state.daily_progress:
        st.session_state.daily_progress[today_str] = {}

    # Initialize or remove goals from today's progress based on current active goals
    for goal in st.session_state.goals:
        if goal not in st.session_state.daily_progress[today_str]:
            st.session_state.daily_progress[today_str][goal] = False
    
    # Remove goals from today's progress if they are no longer active goals
    goals_to_remove = [g for g in st.session_state.daily_progress[today_str] if g not in st.session_state.goals]
    for g in goals_to_remove:
        del st.session_state.daily_progress[today_str][g]


    st.subheader("Today's Goals:")
    updated_progress_for_today = {}

    sorted_goals = sorted(st.session_state.goals) # Display goals alphabetically

    for goal in sorted_goals:
        is_completed = st.checkbox(
            f"{goal}",
            value=st.session_state.daily_progress[today_str].get(goal, False),
            key=f"checkbox_{today_str}_{goal}"
        )
        updated_progress_for_today[goal] = is_completed

    if st.button("Save Today's Progress"):
        st.session_state.daily_progress[today_str] = updated_progress_for_today
        # MODIFIED: Use update_current_user_data
        update_current_user_data(st.session_state.goals, st.session_state.daily_progress)
        st.success("Today's progress saved!")
        st.rerun()

    completion_percentage = calculate_daily_completion(today_str)
    st.markdown(f"**Today's Completion:** {completion_percentage:.0f}%")
    st.progress(completion_percentage / 100)


def quotes_page(): # Renamed the internal function
    st.title("Quote of the Day") # Changed page title
    st.markdown("---")
    quote = get_daily_quote()
    st.markdown(
        f"<h2 style='text-align: center; font-weight: bold; font-size: 2em;'>\"{quote}\"</h2>",
        unsafe_allow_html=True
    )
    st.markdown("---")


def progress_reports_page():
    st.title("Daily Progress Overview")
    st.subheader("Last 7 Days of Completion")

    today = datetime.date.today()
    report_data = []

    st.markdown("""
        <style>
        .dataframe td.completion-red { color: red; font-weight: bold; }
        .dataframe td.completion-orange { color: orange; font-weight: bold; }
        .dataframe td.completion-green { color: green; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)


    for i in range(7):
        date_to_report = today - datetime.timedelta(days=i)
        date_str = date_to_report.strftime("%Y-%m-%d")
        display_date = date_to_report.strftime("%A, %b %d, %Y")
        
        percentage = calculate_daily_completion(date_str)
        color = get_progress_color(percentage)
        
        report_data.append({
            "Date": display_date,
            "Completion (%)": f"<span style='color:{color};'>{percentage:.0f}%</span>"
        })
    report_data.reverse()
    df_report = pd.DataFrame(report_data)
    st.markdown(df_report.to_html(escape=False, index=False), unsafe_allow_html=True)

    if not st.session_state.daily_progress and not st.session_state.goals:
        st.info("No tracking data or goals set yet. Start by setting goals and tracking them!")
    elif not st.session_state.daily_progress: # Only check if daily_progress is empty after checking for goals
        st.info("No tracking data available yet for your goals. Start tracking your goals!")


def weekly_summary_page():
    st.title("Weekly Summary")

    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)

    st.subheader(f"Summary for the week of {start_of_week.strftime('%b %d, %Y')} - {end_of_week.strftime('%b %d, %Y')}")

    weekly_percentages = []
    # Only consider dates that have entries for the current user's goals
    for i in range(7):
        date = start_of_week + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        if date_str in st.session_state.daily_progress and st.session_state.daily_progress[date_str]:
            weekly_percentages.append(calculate_daily_completion(date_str))

    if not weekly_percentages:
        st.info("No tracking data for this week yet. Keep tracking your goals to see a summary!")
        return

    avg_weekly_completion = sum(weekly_percentages) / len(weekly_percentages)
    min_completion = min(weekly_percentages)
    max_completion = max(weekly_percentages)

    # Use the motivational message function but adapt it for summary context
    summary_paragraph = get_motivational_message(avg_weekly_completion)
    # Remove emojis and adapt intro phrases for summary
    summary_paragraph = summary_paragraph.replace("🚀", "").replace("✨", "").replace("💪", "").replace("👋", "")
    summary_paragraph = summary_paragraph.replace("Fantastic work", "This week's performance was fantastic")
    summary_paragraph = summary_paragraph.replace("Great effort", "You've put in great effort this week")
    summary_paragraph = summary_paragraph.replace("Keep pushing", "There's room for improvement, but keep pushing")
    summary_paragraph = summary_paragraph.replace("Welcome, Habit Tracker User! Ready to unlock your full potential? Start by setting your first goal on the 'Goal Setting' page. Small steps lead to big victories!", "Your weekly summary will appear here once you have some tracking data.")


    st.write(summary_paragraph)

    st.markdown("---")
    st.subheader("Weekly Statistics:")
    st.write(f"**Average Daily Completion:** {avg_weekly_completion:.0f}%")
    st.write(f"**Highest Daily Completion:** {max_completion:.0f}%")
    st.write(f"**Lowest Daily Completion:** {min_completion:.0f}%")

    st.subheader("Daily Breakdown:")
    daily_breakdown_data = []
    for i in range(7):
        date = start_of_week + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        percentage = calculate_daily_completion(date_str)
        daily_breakdown_data.append({"Day": date.strftime("%A"), "Completion %": f"{percentage:.0f}%"})
    st.table(pd.DataFrame(daily_breakdown_data))



# Set background image for the login page as well
set_page_background_image("Default")

# Authenticator Login Widget
name, authentication_status, username = authenticator.login("Login", location="main")

if authentication_status: # User is successfully logged in
    st.session_state.authenticated_username = username # Store username
    st.session_state.user_name = name # Store display name
    init_session_state() # Initialize session state *after* user is authenticated

    # Set background image for the current app page
    set_page_background_image(st.session_state.current_page)

    # Sidebar for navigation and logout
    with st.sidebar:
        st.title(APP_TITLE)
        st.markdown(f"**Welcome, {st.session_state.user_name}!**")
        authenticator.logout("Logout", "main") # Logout button in sidebar
        st.markdown("---")
        st.subheader("Navigation")
        if st.button("Home", key="nav_home"):
            set_page("Welcome")
        if st.button("Goal Tracking", key="nav_track"):
            set_page("Goal Tracking")
        if st.button("Goal Setting", key="nav_set"):
            set_page("Goal Setting")
        if st.button("Quote of the Day", key="nav_quotes"): # Changed button label
            set_page("Quote of the Day") # Changed target page name
        if st.button("Progress Reports", key="nav_reports"):
            set_page("Progress Reports")
        if st.button("Weekly Summary", key="nav_summary"):
            set_page("Weekly Summary")

    # Render the selected page
    if st.session_state.current_page == "Welcome":
        welcome_page()
    elif st.session_state.current_page == "Goal Tracking":
        goal_tracking_page()
    elif st.session_state.current_page == "Goal Setting":
        goal_setting_page()
    elif st.session_state.current_page == "Quote of the Day": # Changed page name in conditional check
        quotes_page() # Function call remains the same
    elif st.session_state.current_page == "Progress Reports":
        progress_reports_page()
    elif st.session_state.current_page == "Weekly Summary":
        weekly_summary_page()

elif authentication_status == False: # Login failed
    st.error("Username/password is incorrect")
elif authentication_status == None: # Not yet logged in (or logged out)
    st.info("Please enter your username and password to log in.")

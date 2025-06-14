import streamlit as st
import datetime
import random
import pandas as pd
import json
import os
import base64
import calendar

# --- Configuration and File Paths ---
APP_TITLE = "Habit Tracker"
DATA_DIR = "data"
QUOTES_FILE = os.path.join(DATA_DIR, "quotes.txt")
USER_DATA_FILE = os.path.join(DATA_DIR, "user_data.json")

# --- Hardcoded User Credentials (Simple Login) ---
CREDENTIALS = {
    "mohit": "12345",
    "admin": "123456",
    "muskan": "12345",
    "ananya": "12345",
    "shreya": "12345",
    "rayan": "12345",
    "simran": "12345",
    "dhruv": "12345"
}

# Define paths for background images for each page
BACKGROUND_IMAGES = {
    "Login": os.path.join("images", "welcome_bg.jpg"),
    "Home": os.path.join("images", "welcome_bg.jpg"),
    "Goal Tracking": os.path.join("images", "goal_tracking_bg.jpg"),
    "Goal Setting": os.path.join("images", "goal_setting_bg.jpg"),
    "Quote of the Day": os.path.join("images", "quotes_bg.jpg"),
    "Progress Reports": os.path.join("images", "progress_reports_bg.jpg"),
    "Weekly Summary": os.path.join("images", "weekly_summary_bg.jpg"),
    "Default": os.path.join("images", "default_bg.jpg")
}

# --- IMPORTANT: THIS IS WHERE THE SUGGESTED HABITS ARE DEFINED ---
SUGGESTED_HABITS = [
    "Drink 8 glasses of water",
    "Exercise for 30 minutes",
    "Read for 15 minutes",
    "Meditate for 10 minutes",
    "Journal for 5 minutes",
    "Take a 15-minute walk",
    "Learn a new skill",
    "Practice gratitude",
    "Go to bed before 11 PM",
    "Wake up before 7 AM"
]

# --- Ensure Data Directories Exist ---
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs("images", exist_ok=True)

# --- Helper Functions for Data Persistence ---
def load_quotes():
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

def load_all_user_data():
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

def save_all_user_data(all_data):
    try:
        with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving all user data: {e}")

def get_current_user_data():
    all_data = load_all_user_data()
    current_username = st.session_state.get('username')
    if current_username and current_username in all_data:
        return all_data[current_username].get('goals', []), all_data[current_username].get('daily_progress', {})
    return [], {}

def update_current_user_data(goals, daily_progress):
    all_data = load_all_user_data()
    current_username = st.session_state.get('username')

    if current_username:
        if current_username not in all_data:
            all_data[current_username] = {}
        all_data[current_username]['goals'] = goals
        all_data[current_username]['daily_progress'] = daily_progress
        save_all_user_data(all_data)
    else:
        st.error("Cannot save data: No user is currently logged in.")

QUOTES = load_quotes()

def init_session_state_for_user():
    if 'logged_in' in st.session_state and st.session_state.logged_in and 'goals' not in st.session_state:
        st.session_state.goals, st.session_state.daily_progress = get_current_user_data()
        st.session_state.current_page = "Home"

def set_page_background_image(page_name):
    image_path = BACKGROUND_IMAGES.get(page_name, BACKGROUND_IMAGES["Default"])
    ext = os.path.splitext(image_path)[1].lower()
    mime_type_map = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}
    mime_type = mime_type_map.get(ext, 'image/jpeg')

    try:
        if not os.path.exists(image_path):
            st.warning(f"Background image not found for '{page_name}' at {image_path}. Using default background.")
            image_path = BACKGROUND_IMAGES["Default"]
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = mime_type_map.get(ext, 'image/jpeg')

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

def load_image_for_page(image_name):
    image_path = os.path.join("images", image_name)
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.warning(f"Image '{image_name}' not found in images/ folder.")

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
    user_name_display = st.session_state.get('username', 'Habit Tracker User')
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
    elif st.session_state.goals:
        return (
            f"💪 **Keep pushing, {user_name_display}!** Even if things felt challenging, remember that consistency beats perfection. "
            "Identify one small change you can make today to get back on track. You've got the power to make it happen!"
        )
    else:
        return (
            f"👋 **Welcome, {user_name_display}!** Ready to unlock your full potential? "
            "Start by setting your first goal on the 'Goal Setting' page. "
            "Small steps lead to big victories!"
        )

# --- Page Functions ---

def login_page():
    set_page_background_image("Login")
    st.title("Habit Tracker - Login")
    load_image_for_page("login.jpg")

    username_input = st.text_input("Username", key="login_username")
    password_input = st.text_input("Password", type="password", key="login_password")
    login_button = st.button("Login")

    if login_button:
        if username_input.lower() in CREDENTIALS and CREDENTIALS[username_input.lower()] == password_input:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username_input.lower()
            init_session_state_for_user()
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid username or password.")

def home_page():
    set_page_background_image("Home")
    st.title(f"Welcome, {st.session_state['username']}!")
    
    today = datetime.date.today()
    recent_percentages = []
    if st.session_state.goals:
        for i in range(7):
            date_to_check = today - datetime.timedelta(days=i)
            date_str = date_to_check.strftime("%Y-%m-%d")
            if date_str in st.session_state.daily_progress and any(goal in st.session_state.goals for goal in st.session_state.daily_progress[date_str]):
                 recent_percentages.append(calculate_daily_completion(date_str))

    avg_recent_completion = sum(recent_percentages) / len(recent_percentages) if recent_percentages else 0

    st.markdown(get_motivational_message(avg_recent_completion))
    st.markdown("---")
    st.markdown("Use the sidebar to navigate through the app.")

def goal_setting_page():
    set_page_background_image("Goal Setting")
    st.title("Goal Setting")
    
    st.write("Here you can manage your habits. Choose from suggestions or add your own!")

    st.subheader("Add from Suggestions:") # Always show this header
    
    available_suggestions = [habit for habit in SUGGESTED_HABITS if habit not in st.session_state.goals]
    
    if available_suggestions: # Only show the multiselect if there are suggestions
        selected_suggestions = st.multiselect(
            "Select habits to add:",
            options=available_suggestions,
            key="suggested_habits_multiselect"
        )
        if st.button("Add Selected Suggestions"):
            if selected_suggestions:
                for habit in selected_suggestions:
                    if habit not in st.session_state.goals:
                        st.session_state.goals.append(habit)
                        for date_key in st.session_state.daily_progress:
                            if habit not in st.session_state.daily_progress[date_key]:
                                st.session_state.daily_progress[date_key][habit] = False
                update_current_user_data(st.session_state.goals, st.session_state.daily_progress)
                st.success(f"Added {len(selected_suggestions)} suggested habit(s)!")
                st.rerun()
            else:
                st.info("Please select at least one habit from the suggestions.")
    else: # If no available suggestions, show a message
        st.info("All suggested habits are already in your active goals!")


    st.subheader("Add Your Own Custom Goal:")
    new_goal = st.text_input("New Goal:", key="new_goal_input")
    if st.button("Add Custom Goal"):
        if new_goal and new_goal not in st.session_state.goals:
            st.session_state.goals.append(new_goal)
            for date_key in st.session_state.daily_progress:
                if new_goal not in st.session_state.daily_progress[date_key]:
                    st.session_state.daily_progress[date_key][new_goal] = False
            update_current_user_data(st.session_state.goals, st.session_state.daily_progress)
            st.success(f"Goal '{new_goal}' added!")
            st.rerun()
        elif new_goal in st.session_state.goals:
            st.warning("This goal already exists!")
        else:
            st.warning("Please enter a goal.")

    st.subheader("Your Current Goals:")
    if st.session_state.goals:
        goals_copy = st.session_state.goals[:]
        for i, goal in enumerate(goals_copy):
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.write(f"- {goal}")
            with col2:
                goal_in_use = False
                for date_data in st.session_state.daily_progress.values():
                    if goal in date_data:
                        goal_in_use = True
                        break

                if goal_in_use:
                    st.button(f"Cannot Remove", key=f"remove_goal_{i}", disabled=True, help="This goal has recorded progress and cannot be removed.")
                else:
                    if st.button(f"Remove", key=f"remove_goal_{i}"):
                        st.session_state.goals.remove(goal)
                        for date_key in st.session_state.daily_progress:
                            if goal in st.session_state.daily_progress[date_key]:
                                del st.session_state.daily_progress[date_key][goal]
                        update_current_user_data(st.session_state.goals, st.session_state.daily_progress)
                        st.success(f"Goal '{goal}' removed.")
                        st.rerun()
    else:
        st.info("No goals set yet. Start by adding some!")

def goal_tracking_page():
    set_page_background_image("Goal Tracking")
    st.title("Goal Tracking for Today")
    
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    st.write(f"Mark the goals you completed on {today_str}.")

    if not st.session_state.goals:
        st.warning("You haven't set any goals yet! Please go to 'Goal Setting' to add your goals.")
        st.session_state.current_page = "Goal Setting"
        st.rerun()
        return

    if today_str not in st.session_state.daily_progress:
        st.session_state.daily_progress[today_str] = {}

    for goal in st.session_state.goals:
        if goal not in st.session_state.daily_progress[today_str]:
            st.session_state.daily_progress[today_str][goal] = False
    
    goals_to_remove = [g for g in st.session_state.daily_progress[today_str] if g not in st.session_state.goals]
    for g in goals_to_remove:
        del st.session_state.daily_progress[today_str][g]

    st.subheader("Today's Goals:")
    updated_progress_for_today = {}

    sorted_goals = sorted(st.session_state.goals)

    for goal in sorted_goals:
        is_completed = st.checkbox(
            f"{goal}",
            value=st.session_state.daily_progress[today_str].get(goal, False),
            key=f"checkbox_{today_str}_{goal}"
        )
        updated_progress_for_today[goal] = is_completed

    if st.button("Save Today's Progress"):
        st.session_state.daily_progress[today_str] = updated_progress_for_today
        update_current_user_data(st.session_state.goals, st.session_state.daily_progress)
        st.success("Today's progress saved!")
        st.rerun()

    completion_percentage = calculate_daily_completion(today_str)
    st.markdown(f"**Today's Completion:** {completion_percentage:.0f}%")
    st.progress(completion_percentage / 100)

def quotes_page():
    set_page_background_image("Quote of the Day")
    st.title("Quote of the Day")
    
    st.markdown("---")
    quote = get_daily_quote()
    st.markdown(
        f"<h2 style='text-align: center; font-weight: bold; font-size: 2em;'>\"{quote}\"</h2>",
        unsafe_allow_html=True
    )
    st.markdown("---")

def progress_reports_page():
    set_page_background_image("Progress Reports")
    st.title("Daily Progress Overview")
    
    st.subheader("Last 7 Days of Completion")

    st.markdown("""
        <style>
        .dataframe td.completion-red { color: red; font-weight: bold; }
        .dataframe td.completion-orange { color: orange; font-weight: bold; }
        .dataframe td.completion-green { color: green; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    today = datetime.date.today()
    report_data = []

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
    elif not st.session_state.daily_progress:
        st.info("No tracking data available yet for your goals. Start tracking your goals!")

def weekly_summary_page():
    set_page_background_image("Weekly Summary")
    st.title("Weekly Summary")
    
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)

    st.subheader(f"Summary for the week of {start_of_week.strftime('%b %d, %Y')} - {end_of_week.strftime('%b %d, %Y')}")

    weekly_percentages = []
    meaningful_percentages_for_avg = []
    daily_breakdown_data = []

    for i in range(7):
        date = start_of_week + datetime.timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        percentage = calculate_daily_completion(date_str)
        weekly_percentages.append(percentage)

        if percentage > 0 or (date_str in st.session_state.daily_progress and st.session_state.daily_progress[date_str]):
            meaningful_percentages_for_avg.append(percentage)


        daily_breakdown_data.append({"Day": date.strftime("%A"), "Completion %": f"{percentage:.0f}%"})

    if not st.session_state.goals:
        st.info("No goals set yet. Set goals to see your weekly summary!")
        return

    avg_weekly_completion = sum(meaningful_percentages_for_avg) / len(meaningful_percentages_for_avg) if meaningful_percentages_for_avg else 0
    min_completion = min(meaningful_percentages_for_avg) if meaningful_percentages_for_avg else 0
    max_completion = max(meaningful_percentages_for_avg) if meaningful_percentages_for_avg else 0

    if not meaningful_percentages_for_avg:
        st.info("No goals were tracked this week. Start tracking your goals to see a summary!")
        return
    
    st.write(get_motivational_message(avg_weekly_completion))

    st.markdown("---")
    st.subheader("Weekly Statistics:")
    st.write(f"**Average Daily Completion:** {avg_weekly_completion:.0f}%")
    st.write(f"**Highest Daily Completion:** {max_completion:.0f}%")
    st.write(f"**Lowest Daily Completion:** {min_completion:.0f}%")

    st.subheader("Daily Breakdown:")
    st.table(pd.DataFrame(daily_breakdown_data))

# --- Main Streamlit App Flow ---
st.set_page_config(layout="centered", page_title=APP_TITLE)

if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    login_page()
else:
    init_session_state_for_user()

    with st.sidebar:
        st.title(APP_TITLE)
        st.markdown(f"**Hello, {st.session_state['username']} 👋**")
        st.markdown("---")
        
        menu = st.sidebar.selectbox("Navigate", ["Home", "Goal Setting", "Goal Tracking", "Quote of the Day", "Progress Reports", "Weekly Summary", "Logout"])

        if menu == "Logout":
            st.session_state.clear()
            st.rerun()

    st.session_state.current_page = menu
    
    set_page_background_image(st.session_state.current_page)

    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Goal Setting":
        goal_setting_page()
    elif st.session_state.current_page == "Goal Tracking":
        goal_tracking_page()
    elif st.session_state.current_page == "Quote of the Day":
        quotes_page()
    elif st.session_state.current_page == "Progress Reports":
        progress_reports_page()
    elif st.session_state.current_page == "Weekly Summary":
        weekly_summary_page()

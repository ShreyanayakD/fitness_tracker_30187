import streamlit as st
import pandas as pd
import psycopg2
from backend_fitness_tracker_30187 import DatabaseManager
import datetime

# Database Configuration (replace with your actual credentials)
DB_CONFIG = {
    "dbname": "fitness_tracker_30187",
    "user": "postgres",
    "password": "Nayak",
    "host": "localhost"
}

# Initialize the database manager
db_manager = DatabaseManager(**DB_CONFIG)

# Streamlit UI
st.title("🏋️ Fitness Tracker Application (Shreya D 30187)")

if not db_manager.connect():
    st.error("Could not connect to the database. Please check your credentials and ensure the database is running.")
else:
    # --- AUTHENTICATION/USER SELECTION ---
    st.sidebar.header("User Management")
    all_users = db_manager.get_all_users()
    user_options = {f"{user[1]} ({user[2]})": user[0] for user in all_users}
    
    selected_user_name = st.sidebar.selectbox("Select User", options=list(user_options.keys()))
    if selected_user_name:
        current_user_id = user_options[selected_user_name]
        st.sidebar.success(f"Logged in as {selected_user_name}")
    
    st.sidebar.subheader("New User")
    with st.sidebar.form(key='new_user_form'):
        new_name = st.text_input("Name")
        new_email = st.text_input("Email")
        new_weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
        submit_button = st.form_submit_button("Create New User")
        if submit_button:
            if new_name and new_email:
                try:
                    db_manager.create_user(new_name, new_email, new_weight)
                    st.success(f"User '{new_name}' created successfully!")
                    st.rerun()  # Corrected function call
                except psycopg2.IntegrityError:
                    st.error("Email already exists. Please use a different email.")
            else:
                st.error("Name and Email are required.")

    # --- MAIN APP ---
    if selected_user_name:
        st.write(f"Welcome, {selected_user_name.split(' ')[0]}!")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "📝 Log Workout", "🎯 Goals", "👥 Social & Leaderboard", "📈 Business Insights"])

        # --- Dashboard Tab (Workout History) ---
        with tab1:
            st.header("Workout History")
            workouts = db_manager.get_user_workouts(current_user_id)
            if workouts:
                for w in workouts:
                    with st.expander(f"Workout on {w[2].strftime('%Y-%m-%d')} (Duration: {w[3]} min)"):
                        st.subheader("Exercises:")
                        exercises = db_manager.get_workout_exercises(w[0])
                        if exercises:
                            ex_df = pd.DataFrame(exercises, columns=['ID', 'Workout ID', 'Name', 'Reps', 'Sets', 'Weight (kg)'])
                            st.table(ex_df[['Name', 'Reps', 'Sets', 'Weight (kg)']])
                        else:
                            st.info("No exercises logged for this workout.")
            else:
                st.info("You haven't logged any workouts yet.")

        # --- Log Workout Tab ---
        with tab2:
            st.header("Log a New Workout")
            with st.form(key='workout_form'):
                workout_date = st.date_input("Date", datetime.date.today())
                duration = st.number_input("Duration (minutes)", min_value=1, value=30)
                
                st.subheader("Add Exercises")
                num_exercises = st.number_input("Number of exercises", min_value=1, value=1, step=1)
                
                exercises_data = []
                for i in range(num_exercises):
                    st.subheader(f"Exercise #{i+1}")
                    exercise_name = st.text_input(f"Name of Exercise #{i+1}")
                    reps = st.number_input(f"Reps", min_value=0, key=f"reps_{i}")
                    sets = st.number_input(f"Sets", min_value=0, key=f"sets_{i}")
                    weight = st.number_input(f"Weight Lifted (kg)", min_value=0.0, step=0.1, key=f"weight_{i}")
                    exercises_data.append({'name': exercise_name, 'reps': reps, 'sets': sets, 'weight': weight})
                
                submit_workout = st.form_submit_button("Log Workout")

            if submit_workout:
                try:
                    workout_id = db_manager.create_workout(current_user_id, workout_date, duration)
                    for ex in exercises_data:
                        if ex['name']:
                            db_manager.create_exercise(workout_id, ex['name'], ex['reps'], ex['sets'], ex['weight'])
                    st.success("Workout logged successfully!")
                    st.balloons()
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        # --- Goals Tab ---
        with tab3:
            st.header("Set and Track Goals")
            st.subheader("Create a New Goal")
            with st.form(key='goal_form'):
                goal_description = st.text_area("Goal Description")
                goal_metric = st.text_input("Metric (e.g., 'workouts per week', 'total minutes')")
                target_value = st.number_input("Target Value", min_value=0.0, step=0.1)
                submit_goal = st.form_submit_button("Set Goal")
                if submit_goal:
                    db_manager.create_goal(current_user_id, goal_description, goal_metric, target_value)
                    st.success("Goal set successfully!")

            st.subheader("Your Current Goals")
            goals = db_manager.get_user_goals(current_user_id)
            if goals:
                goals_df = pd.DataFrame(goals, columns=['ID', 'User ID', 'Description', 'Metric', 'Target Value', 'Current Value', 'Start Date', 'End Date'])
                st.table(goals_df[['Description', 'Metric', 'Target Value', 'Current Value', 'Start Date']])
            else:
                st.info("You haven't set any goals yet.")

        # --- Social & Leaderboard Tab ---
        with tab4:
            st.header("Social Connections")
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Your Friends")
                friends = db_manager.get_user_friends(current_user_id)
                if friends:
                    friends_df = pd.DataFrame(friends, columns=['ID', 'Name', 'Email'])
                    st.table(friends_df[['Name', 'Email']])
                    friend_to_remove = st.selectbox("Remove a friend:", options=friends_df['Name'].tolist())
                    if st.button("Remove Friend"):
                        friend_id_to_remove = friends_df[friends_df['Name'] == friend_to_remove]['ID'].iloc[0]
                        db_manager.delete_friend(current_user_id, friend_id_to_remove)
                        st.success(f"{friend_to_remove} removed successfully.")
                        st.rerun()  # Corrected function call
                else:
                    st.info("You have no friends yet.")
            
            with col2:
                st.subheader("Add a Friend")
                other_users = db_manager.get_all_users()
                other_users_df = pd.DataFrame(other_users, columns=['ID', 'Name', 'Email'])
                other_users_df = other_users_df[other_users_df['ID'] != current_user_id]
                
                if not other_users_df.empty:
                    friend_to_add = st.selectbox("Search for friends by name:", options=other_users_df['Name'].tolist())
                    if st.button("Add Friend"):
                        friend_id_to_add = other_users_df[other_users_df['Name'] == friend_to_add]['ID'].iloc[0]
                        try:
                            db_manager.add_friend(current_user_id, friend_id_to_add)
                            st.success(f"{friend_to_add} added successfully!")
                            st.rerun()  # Corrected function call
                        except psycopg2.IntegrityError:
                            st.warning("You are already friends with this user.")
                else:
                    st.info("No other users to add.")

            st.markdown("---")
            st.header("Leaderboard: Total Workout Minutes (Last 7 Days)")
            leaderboard_data = db_manager.get_leaderboard_data(current_user_id)
            if leaderboard_data:
                leaderboard_df = pd.DataFrame(leaderboard_data, columns=['Name', 'Total Minutes'])
                st.table(leaderboard_df)
            else:
                st.info("No friends have logged workouts in the last 7 days.")

        # --- Business Insights Tab ---
        with tab5:
            st.header("Application Insights")
            insights = db_manager.get_business_insights()
            if insights:
                st.subheader("General Statistics")
                st.metric(label="Total Users", value=insights.get('total_users'))
                st.metric(label="Total Workouts Logged", value=insights.get('total_workouts'))

                st.subheader("Workout Metrics")
                st.metric(label="Average Workout Duration", value=f"{insights.get('avg_workout_duration', 0)} min")
                st.metric(label="Max Workout Duration", value=f"{insights.get('max_workout_duration', 0)} min")
                st.metric(label="Most Common Exercise", value=insights.get('most_common_exercise', 'N/A'))
            else:
                st.error("Could not retrieve business insights.")
            
    db_manager.close()
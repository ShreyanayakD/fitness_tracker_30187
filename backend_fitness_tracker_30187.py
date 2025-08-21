import psycopg2

class DatabaseManager:
    def __init__(self, dbname, user, password, host):
        self.conn = None
        self.cursor = None
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host
            )
            self.cursor = self.conn.cursor()
            return True
        except psycopg2.OperationalError as e:
            print(f"Error connecting to database: {e}")
            return False

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    # --- CRUD OPERATIONS ---
    
    # ------------------ CREATE ------------------
    def create_user(self, name, email, weight):
        sql = "INSERT INTO users (name, email, weight_kg) VALUES (%s, %s, %s) RETURNING user_id;"
        self.cursor.execute(sql, (name, email, weight))
        user_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return user_id

    def create_workout(self, user_id, date, duration_minutes):
        sql = "INSERT INTO workouts (user_id, workout_date, duration_minutes) VALUES (%s, %s, %s) RETURNING workout_id;"
        self.cursor.execute(sql, (user_id, date, duration_minutes))
        workout_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return workout_id

    def create_exercise(self, workout_id, name, reps, sets, weight):
        sql = "INSERT INTO exercises (workout_id, exercise_name, reps, sets, weight_lifted_kg) VALUES (%s, %s, %s, %s, %s);"
        self.cursor.execute(sql, (workout_id, name, reps, sets, weight))
        self.conn.commit()

    def add_friend(self, user_id, friend_id):
        sql = "INSERT INTO friends (user_id, friend_id) VALUES (%s, %s);"
        self.cursor.execute(sql, (user_id, friend_id))
        self.conn.commit()

    def create_goal(self, user_id, description, metric, target_value):
        sql = "INSERT INTO goals (user_id, goal_description, goal_metric, target_value) VALUES (%s, %s, %s, %s);"
        self.cursor.execute(sql, (user_id, description, metric, target_value))
        self.conn.commit()

    # ------------------ READ ------------------
    def get_user_by_email(self, email):
        sql = "SELECT * FROM users WHERE email = %s;"
        self.cursor.execute(sql, (email,))
        return self.cursor.fetchone()

    def get_user_by_id(self, user_id):
        sql = "SELECT * FROM users WHERE user_id = %s;"
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchone()

    def get_all_users(self):
        sql = "SELECT user_id, name, email FROM users;"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_user_workouts(self, user_id):
        sql = "SELECT * FROM workouts WHERE user_id = %s ORDER BY workout_date DESC;"
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def get_workout_exercises(self, workout_id):
        sql = "SELECT * FROM exercises WHERE workout_id = %s;"
        self.cursor.execute(sql, (workout_id,))
        return self.cursor.fetchall()

    def get_user_friends(self, user_id):
        sql = """
        SELECT u.user_id, u.name, u.email
        FROM friends f
        JOIN users u ON f.friend_id = u.user_id
        WHERE f.user_id = %s;
        """
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def get_user_goals(self, user_id):
        sql = "SELECT * FROM goals WHERE user_id = %s ORDER BY start_date DESC;"
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    def get_leaderboard_data(self, user_id):
        sql = """
        SELECT u.name, SUM(w.duration_minutes) AS total_minutes
        FROM friends f
        JOIN workouts w ON f.friend_id = w.user_id
        JOIN users u ON w.user_id = u.user_id
        WHERE f.user_id = %s
        AND w.workout_date BETWEEN NOW() - INTERVAL '7 days' AND NOW()
        GROUP BY u.name
        ORDER BY total_minutes DESC;
        """
        self.cursor.execute(sql, (user_id,))
        return self.cursor.fetchall()

    # ------------------ UPDATE ------------------
    def update_user_profile(self, user_id, name, email, weight):
        sql = "UPDATE users SET name = %s, email = %s, weight_kg = %s WHERE user_id = %s;"
        self.cursor.execute(sql, (name, email, weight, user_id))
        self.conn.commit()

    # ------------------ DELETE ------------------
    def delete_friend(self, user_id, friend_id):
        sql = "DELETE FROM friends WHERE user_id = %s AND friend_id = %s;"
        self.cursor.execute(sql, (user_id, friend_id))
        self.conn.commit()

    # ------------------ BUSINESS INSIGHTS ------------------
    def get_business_insights(self):
        insights = {}
        
        # Total Users
        self.cursor.execute("SELECT COUNT(*) FROM users;")
        insights['total_users'] = self.cursor.fetchone()[0]

        # Total Workouts Logged
        self.cursor.execute("SELECT COUNT(*) FROM workouts;")
        insights['total_workouts'] = self.cursor.fetchone()[0]
        
        # Average Workout Duration
        self.cursor.execute("SELECT AVG(duration_minutes) FROM workouts;")
        insights['avg_workout_duration'] = round(self.cursor.fetchone()[0], 2) if self.cursor.fetchone()[0] else 0
        
        # Max Duration of a single workout
        self.cursor.execute("SELECT MAX(duration_minutes) FROM workouts;")
        insights['max_workout_duration'] = self.cursor.fetchone()[0] if self.cursor.fetchone()[0] else 0

        # Most Common Exercise
        self.cursor.execute("SELECT exercise_name, COUNT(*) as count FROM exercises GROUP BY exercise_name ORDER BY count DESC LIMIT 1;")
        most_common = self.cursor.fetchone()
        insights['most_common_exercise'] = most_common[0] if most_common else 'N/A'

        return insights
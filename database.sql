-- Table: users
-- Stores user profile information, including name, email, and weight.
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    weight_kg NUMERIC(5, 2)
);

-- Table: workouts
-- Logs a user's workout sessions. Links to the 'users' table via a foreign key.
CREATE TABLE workouts (
    workout_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    workout_date DATE NOT NULL,
    duration_minutes INTEGER NOT NULL
);

-- Table: exercises
-- Details the individual exercises performed within a workout.
-- Links to the 'workouts' table.
CREATE TABLE exercises (
    exercise_id SERIAL PRIMARY KEY,
    workout_id INTEGER NOT NULL REFERENCES workouts(workout_id) ON DELETE CASCADE,
    exercise_name VARCHAR(255) NOT NULL,
    reps INTEGER,
    sets INTEGER,
    weight_lifted_kg NUMERIC(5, 2)
);

-- Table: friends
-- Manages the social connections between users.
-- Uses a composite primary key to ensure unique pairs and prevent duplicate friendship entries.
CREATE TABLE friends (
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    friend_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, friend_id),
    CONSTRAINT different_users CHECK (user_id != friend_id)
);

-- Table: goals
-- Stores the personal fitness goals for a user.
-- The goal_metric column can be used to describe the type of goal (e.g., 'workouts per week', 'weight loss').
CREATE TABLE goals (
    goal_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    goal_description TEXT NOT NULL,
    goal_metric VARCHAR(50),
    target_value NUMERIC(10, 2),
    current_value NUMERIC(10, 2) DEFAULT 0,
    start_date DATE NOT NULL DEFAULT CURRENT_DATE,
    end_date DATE
);

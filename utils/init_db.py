import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': 'bluecard_data',
    'user': 'bluecard_data_user',
    'password': 'joqHxjeQXPAkIRozmOgBHn5kZdIWdaU4',
    'host': 'dpg-d038t8ali9vc73eo4jdg-a.frankfurt-postgres.render.com',
    'port': '5432',
}

DATABASE_URL = os.getenv("DATABASE_URL")

# Create a connection to the database
def init_db():
    # Establish the connection
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Drop existing tables if they exist (for development purposes)
    cur.execute("""
        DROP TABLE IF EXISTS transactions CASCADE;
        DROP TABLE IF EXISTS saving_goals CASCADE;
        DROP TABLE IF EXISTS expense CASCADE;
        DROP TABLE IF EXISTS income CASCADE;
        DROP TABLE IF EXISTS users CASCADE;
    """)

    # Create tables
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name VARCHAR(255),
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW(),
            is_active BOOLEAN DEFAULT TRUE,
            dashboard_settings JSONB DEFAULT '{"components":[]}'
        );

        CREATE TABLE IF NOT EXISTS income (
            income_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            amount DECIMAL(12, 2) NOT NULL,
            source VARCHAR(255) NOT NULL,
            monthly_amount DECIMAL(12, 2),
            weekly_amount DECIMAL(12, 2),
            daily_amount DECIMAL(12, 2),
            frequency VARCHAR(50),
            income_type VARCHAR(100),
            consistency VARCHAR(100),
            category VARCHAR(100),
            date TIMESTAMP DEFAULT NOW()
        );

        -- Add the UUID extension if not already enabled
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        CREATE TABLE IF NOT EXISTS expense (
            expense_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            description TEXT,
            amount DECIMAL(12, 2) NOT NULL,
            category VARCHAR(255),
            date TIMESTAMP DEFAULT NOW(),
            due_date TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS saving_goals (
            goal_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            goal_name VARCHAR(255) NOT NULL,
            target_amount DECIMAL(12, 2) NOT NULL,
            current_amount DECIMAL(12, 2) DEFAULT 0,
            deadline DATE,
            created_at TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            amount DECIMAL(12, 2) NOT NULL,
            type VARCHAR(50) NOT NULL,  -- e.g., 'income' or 'expense'
            category VARCHAR(255),      -- Adding the category column that was missing
            description TEXT,
            date TIMESTAMP DEFAULT NOW()
        );
                
        CREATE TABLE IF NOT EXISTS savings_target (
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            amount NUMERIC(12, 2) NOT NULL,   -- Use NUMERIC for money values
            date DATE NOT NULL                -- Use DATE type for dates
        );

    """)

    # Commit changes and close the connection
    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()

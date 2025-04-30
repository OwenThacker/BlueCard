import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor, Json  # Add Json here
from hashlib import sha256
import bcrypt
import json  # Make sure json is imported too

# Database connection parameters
DB_PARAMS = {
    'dbname': 'bluecard_data',
    'user': 'bluecard_data_user',
    'password': 'joqHxjeQXPAkIRozmOgBHn5kZdIWdaU4',
    'host': 'dpg-d038t8ali9vc73eo4jdg-a.frankfurt-postgres.render.com',
    'port': '5432',
}

# Function to connect to the database
def connect_db():
    conn = psycopg2.connect(**DB_PARAMS)
    return conn

# Function to register a new user
def register_user(email, password, full_name):
    conn = connect_db()
    cur = conn.cursor()

    # Hash password before storing it
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cur.execute("""
    INSERT INTO users (email, password_hash, full_name)
    VALUES (%s, %s, %s) RETURNING user_id;
    """, (email, hashed_pw, full_name))

    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return user_id

# Function to authenticate a user
def authenticate_user(email, password):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT user_id, password_hash FROM users WHERE email = %s;", (email,))
    result = cur.fetchone()

    if result and bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')):
        return result[0]  # return user_id if authentication is successful
    else:
        return None

def add_income(user_id, income_data):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            # Extract the user_id value if it's a dictionary
            actual_user_id = user_id.get('user_id') if isinstance(user_id, dict) else user_id
            
            # Insert into the existing "income" table instead of "income_sources"
            cur.execute("""
                INSERT INTO income 
                (user_id, source, amount, monthly_amount, weekly_amount, daily_amount, 
                 frequency, income_type, consistency, category) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING income_id
            """, (
                actual_user_id, 
                income_data.get('source'), 
                income_data.get('amount'), 
                income_data.get('monthly_amount'), 
                income_data.get('weekly_amount'), 
                income_data.get('daily_amount'),
                income_data.get('frequency'), 
                income_data.get('type'),  # Note: column is income_type, but data key is 'type'
                income_data.get('consistency'),
                income_data.get('category')
                # Removed the JSONB data field as it doesn't exist in your table
            ))
            income_id = cur.fetchone()[0]
            conn.commit()
            return income_id
    except Exception as e:
        conn.rollback()
        print(f"Error adding income: {e}")
        raise
    finally:
        conn.close()

def get_income_sources(user_id):
    conn = connect_db()
    print(f"Getting income sources for user_id: {user_id}")
    # Check if user_id is a dictionary and extract the actual user_id
    try:
        # Extract the user_id value if it's a dictionary
        actual_user_id = user_id.get('user_id') if isinstance(user_id, dict) else user_id
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT income_id, source, amount, monthly_amount, weekly_amount, daily_amount,
                       frequency, income_type as type, consistency, category
                FROM income
                WHERE user_id = %s
            """, (actual_user_id,))
            
            sources = cur.fetchall()
            
            # Process results into proper dictionaries
            result = []
            for source in sources:
                # Convert from RealDictRow to regular dict
                source_dict = dict(source)
                
                # Add id to the result
                source_dict["id"] = source_dict["income_id"]
                
                # If we have historical data as JSON string, parse it
                if source_dict.get("historical_data"):
                    if isinstance(source_dict["historical_data"], str):
                        source_dict["historical_data"] = json.loads(source_dict["historical_data"])
                
                # Add extra fields from the data JSON if they exist
                if source_dict.get("data") and isinstance(source_dict["data"], dict):
                    for key, value in source_dict["data"].items():
                        if key not in source_dict:
                            source_dict[key] = value
                
                # Set name field for compatibility with existing code
                source_dict["name"] = source_dict.get("source", "Unnamed Income")
                
                result.append(source_dict)
                
            return result
    except Exception as e:
        print(f"Error getting income sources: {e}")
        return []
    finally:
        conn.close()

def update_income(income_id, update_data):
    conn = connect_db()
    try:
        with conn.cursor() as cur:
            # Handle historical data separately
            if "historical_data" in update_data:
                historical_data = update_data["historical_data"]

                # Loop through each month’s data and save it
                for month, amount in historical_data.items():
                    # Check if this historical record exists
                    cur.execute("""
                        SELECT income_id FROM historical_income
                        WHERE income_id = %s AND month = %s
                    """, (income_id, month))

                    result = cur.fetchone()

                    if result:
                        # Update existing historical record with the user’s input amount
                        cur.execute("""
                            UPDATE historical_income
                            SET amount = %s
                            WHERE income_id = %s AND month = %s
                        """, (amount, income_id, month))
                    else:
                        # Insert new historical record with the user’s input amount
                        cur.execute("""
                            INSERT INTO historical_income (income_id, month, amount)
                            VALUES (%s, %s, %s)
                        """, (income_id, month, amount))

                # After updating historical data, calculate the average monthly amount (sum of all historical amounts / number of months)
                cur.execute("""
                    SELECT SUM(amount) FROM historical_income
                    WHERE income_id = %s
                """, (income_id,))
                
                total_yearly_amount = cur.fetchone()[0] or 0  # Ensure no NULLs if no historical data
                
                # Calculate the monthly amount by dividing the total yearly amount by 12
                monthly_amount = total_yearly_amount / 12

                # Update monthly_amount in the income table (this is the only field that's updated with the average)
                cur.execute("""
                    UPDATE income
                    SET monthly_amount = %s
                    WHERE income_id = %s
                """, (monthly_amount, income_id))

            # Handle other updates (non-historical) if present
            updates = []
            values = []

            for key, value in update_data.items():
                if key != "historical_data":
                    updates.append(f"{key} = %s")
                    values.append(value)

            if updates:
                query = f"UPDATE income SET {', '.join(updates)} WHERE income_id = %s"
                values.append(income_id)
                cur.execute(query, values)

            # Commit all changes
            conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error updating income: {e}")
        raise
    finally:
        conn.close()


# Function to delete an income source
# Check your delete_income function to make sure it's properly implemented
def delete_income(income_id):
    conn = connect_db()
    cur = conn.cursor()
    
    # First delete historical data
    cur.execute("DELETE FROM historical_income WHERE income_id = %s", (income_id,))
    
    # Then delete the income source itself
    cur.execute("DELETE FROM income WHERE income_id = %s", (income_id,))
    
    conn.commit()
    cur.close()
    conn.close()

# Function to add expense
def add_expense(user_id, amount, category):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO expense (user_id, amount, category)
    VALUES (%s, %s, %s);
    """, (user_id, amount, category))

    conn.commit()
    cur.close()
    conn.close()

# Function to add a saving goal
def add_saving_goal(user_id, goal_name, target_amount, deadline):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO saving_goals (user_id, goal_name, target_amount, deadline)
    VALUES (%s, %s, %s, %s);
    """, (user_id, goal_name, target_amount, deadline))

    conn.commit()
    cur.close()
    conn.close()

# Function to record a transaction (income or expense)
def record_transaction(user_id, amount, transaction_type, description):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO transactions (user_id, amount, type, description)
    VALUES (%s, %s, %s, %s);
    """, (user_id, amount, transaction_type, description))

    conn.commit()
    cur.close()
    conn.close()

# Function to retrieve income and expenses for a user
def get_user_financials(user_id):
    conn = connect_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
    SELECT * FROM income WHERE user_id = %s;
    """, (user_id,))
    income = cur.fetchall()

    cur.execute("""
    SELECT * FROM expense WHERE user_id = %s;
    """, (user_id,))
    expenses = cur.fetchall()

    cur.close()
    conn.close()

    return {"income": income, "expenses": expenses}

# Function for editing historical income data
def persist_historical_income(income_id, historical_data):
    conn = connect_db()
    with conn.cursor() as cur:
        for month, amount in historical_data.items():
            cur.execute("""
                INSERT INTO historical_income (income_id, month, amount)
                VALUES (%s, %s, %s)
                ON CONFLICT (income_id, month)
                DO UPDATE SET amount = EXCLUDED.amount
            """, (income_id, month, amount))
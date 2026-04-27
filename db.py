import mysql.connector
from mysql.connector import Error
import config

def get_connection():
    """Returns a MySQL connection. Raises exception if fails."""
    try:
        conn = mysql.connector.connect(
            host     = config.DB_HOST,
            user     = config.DB_USER,
            password = config.DB_PASSWORD,
            database = config.DB_NAME
        )
        return conn
    except Error as e:
        print(f"\n  [ERROR] MySQL connect failed: {e}")
        print("  Check config.py — host, user, password, database name.")
        raise

def execute_query(query, params=None, fetch=False):
    """Run a query. If fetch=True returns rows, else returns affected row count."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        conn.commit()
        return cursor.rowcount
    except Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()



# piyush_soni777

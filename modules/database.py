import sqlite3
import os
from logger import log_step

DB_PATH = "syndicate.db"

def init_db():
    """
    Create the databases and tables if they don't exist yet.
    Called once when main.py starts.
    """
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        #recent_form is optional, but we want to store it if available for future analysis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS processed_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT UNIQUE NOT NULL,
                home_team TEXT,
                away_team TEXT,
                recent_form TEXT,
                verdict TEXT,
                confidence INTEGER,
                reason TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        log_step("Database initialized successfully.")
        conn.close()
    except Exception as e:
        log_step(f"DATABASE ERROR","FAILURE",f"Could not initialize database: {e}")
def is_match_processed(match_id: str) -> bool:
    """
    Check if a match has already been processed.
    Returns True if the match_id exists in the database, False otherwise.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM processed_matches WHERE match_id = ?", (match_id,))
        result = cursor.fetchone()     
        conn.close()
        
        return result is not None #TRUE if match_id exists, FALSE if not
    except Exception as e:
        log_step(f"DATABASE ERROR","FAILURE",f"Could not check match: {e}")
        return False

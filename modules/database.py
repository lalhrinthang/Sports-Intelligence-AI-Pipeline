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
        log_step("DATABASE", "SUCCESS", f"Database file: {DB_PATH}")
        conn.close()
    except Exception as e:
        log_step("DATABASE", "FAILURE", f"Could not initialize database: {e}")

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
        log_step("DATABASE", "FAILURE", f"Could not check match: {e}")
        return False

# This function is called after we get Claude's verdict and want to save it to the database.
def save_verdict(match_id, home, away, recent_form, verdict, confidence, reason):
    """
    Save Claude's verdict to the database after processing.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR IGNORE INTO processed_matches
            (match_id, home_team, away_team, recent_form, verdict, confidence, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (match_id, home, away, recent_form, verdict, confidence, reason))

        conn.commit()
        conn.close()

        log_step("DATABASE", "SUCCESS",
                 f"Saved verdict for match {match_id}")

    except Exception as e:
        log_step("DATABASE", "FAILURE", f"Could not save verdict: {e}")
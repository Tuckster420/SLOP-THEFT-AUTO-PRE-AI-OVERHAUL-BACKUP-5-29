import os
import traceback
from datetime import datetime
import time

def debug_log(message):
    """
    Robust logging function that:
    - Tries default log location first
    - Falls back to temp directory if needed
    - Silently fails if no logging is possible
    """
    try:
        # First try default location
        log_path = os.path.join(os.getcwd(), 'debug.log')
        try_log_write(log_path, message)
    except PermissionError:
        # Fallback to temp directory if default fails
        try:
            import tempfile
            temp_log = os.path.join(tempfile.gettempdir(), 'stinkworld_debug.log')
            try_log_write(temp_log, message)
        except Exception:
            # Final fallback - print to console only
            print(f"[DEBUG FALLBACK] {message}")

def try_log_write(path, message):
    """Helper function to attempt a log write"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_line = f"[{timestamp}] {message}\n"
    
    with open(path, 'a', encoding='utf-8') as f:
        f.write(log_line)

def log_debug(message):
    """Log debug messages to a file with timestamps."""
    with open('game_debug.log', 'a') as f:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"[{timestamp}] {message}\n")

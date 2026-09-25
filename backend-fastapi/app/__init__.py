from dotenv import load_dotenv

# Loaded before any sibling module reads os.environ at import time (db.py,
# security.py, notification.py all do). No-op if .env doesn't exist —
# fine for CI and for anyone using real environment variables instead.
load_dotenv()

import os

bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = 4
threads = 4
timeout = 120
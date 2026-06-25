import os
import sys

# Ensure the backend directory (this file's location) is on sys.path so that
# `from app...` imports resolve when running pytest from backend/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

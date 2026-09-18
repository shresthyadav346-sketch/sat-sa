"""
Vercel Serverless Function Entrypoint for SAT-SA FastAPI Backend
Exposes FastAPI app to Vercel Python runtime.
"""
import sys
import os

# Put project root into sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.main import app

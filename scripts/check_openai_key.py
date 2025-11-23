"""
Simple script to verify OPENAI_API_KEY can authenticate and list models.
Run from project root with your venv activated:

python scripts/check_openai_key.py

It prints a short, safe summary (does not echo the key).
"""
import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("openai package not installed. Run: pip install -r apps/server/requirements.txt")
    sys.exit(1)

KEY = os.getenv('OPENAI_API_KEY')
if not KEY:
    print('OPENAI_API_KEY not set in environment. Set it or create apps/server/.env and run run.py')
    sys.exit(1)

client = OpenAI(api_key=KEY)

try:
    resp = client.models.list()
    count = len(getattr(resp, 'data', []))
    print(f'OK — API key appears valid. Models available: {count}')
except Exception as e:
    print('API call failed:', type(e).__name__, str(e))
    sys.exit(2)

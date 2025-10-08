from dotenv import load_dotenv
import os

load_dotenv()


REMLORX_API_KEY = os.getenv("RELMOX_API_KEY", "400394069570a4.iQ4WwRTV7QZo6B3PEbyN4A")

DEVCRAFT_USERNAME = os.getenv("DEVCRAFT_USERNAME", "gtas732ndnnppkkt56")
DEVCRAFT_PASSWORD = os.getenv("DEVCRAFT_PASSWORD", "honethonors3456")

SECRET_KEY = "ASDFGHJKLQWERTYUIOPZXCVBNM1234567890"

API_BASE_URL = os.getenv("API_BASE_URL", "https://hive-sooty-eight.vercel.app")

HEADER = {"Content-Type": "application/json"}






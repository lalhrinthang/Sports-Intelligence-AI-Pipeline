import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from logger import log_step

load_dotenv()

# Configure Gemini with our API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
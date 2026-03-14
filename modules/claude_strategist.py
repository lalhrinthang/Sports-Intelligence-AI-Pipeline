import os
import json
import anthropic
from dotenv import load_dotenv
from logger import log_step
from validator import MatchIntelligence

load_dotenv()

# Initialize the Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))
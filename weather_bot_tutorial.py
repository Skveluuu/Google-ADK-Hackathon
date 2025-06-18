#!/usr/bin/env python3
"""
Weather Bot with Google ADK
"""

import os
import asyncio
from dotenv import load_dotenv
import warnings
import logging
from runtime.main import run_conversation

# Load environment variables from .env file
load_dotenv()

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.ERROR)

# --- API and Model Configuration ---
# This can be set in your .env file or left here as a default
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
print("Environment configured.")


# --- Main Execution ---
if __name__ == "__main__":
    print("Starting Vacation Planner Bot...")
    asyncio.run(run_conversation()) 
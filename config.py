# config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # MCP Server Configuration
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "mock")  # Use "mock" for demo
    MCP_API_KEY = os.getenv("MCP_API_KEY", "demo-key")

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    # Model Configuration
    DEFAULT_MODEL = "gpt-4"

    # Stock Analysis Configuration
    SUPPORTED_PERIODS = ["1d", "1w", "1m", "3m", "6m", "1y", "2y", "5y"]
    DEFAULT_PERIOD = "1y"


config = Config()
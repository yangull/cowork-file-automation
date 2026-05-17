import os
import sys

from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("ANTHROPIC_API_KEY"):
    sys.exit("Error: ANTHROPIC_API_KEY is not set. Add it to .env or your environment.")

from watcher import start

if __name__ == "__main__":
    start()

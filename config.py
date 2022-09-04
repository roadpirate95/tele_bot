import os
from dotenv import load_dotenv
load_dotenv()

ACCEPT = os.environ.get("HEADERS")

USER_AGENT = os.environ.get("USER_AGENT")

TOKEN = os.environ.get("TOKEN")

HEADERS = {"Accept": ACCEPT, "User-Agent": USER_AGENT}

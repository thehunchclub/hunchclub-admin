import os
# Load dotenv
from dotenv import load_dotenv
load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"), 
    override=True
)

SERVER_ADDRESS = os.getenv("API_SERVER_ADDRESS").strip("/")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
BASEPATH = os.getcwd() #os.path.dirname(os.path.abspath(__file__))
API_TOKEN = os.getenv("API_TOKEN")

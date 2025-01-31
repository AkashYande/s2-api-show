
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    S2_API_BASE_URL = 'https://s2-api.botvfx.com'
    s2_tocken="_rJpJiX_RUQ0praWl5Y42HpF-dK3nDBsACa_wTiu"